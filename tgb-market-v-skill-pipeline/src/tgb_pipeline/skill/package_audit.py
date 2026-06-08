"""Audit a distributable Skill package."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tgb_pipeline.audit.text_encoding_audit import TEXT_EXTENSIONS, audit_text_encoding_paths
from tgb_pipeline.skill.package_builder import parse_review_summary, parse_skill_quality_report

REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "MANIFEST.json",
    "methodology_rules.jsonl",
    "rule_evidence_map.jsonl",
    "uncertainty_policy.md",
    "review_summary.md",
    "skill_quality_report.md",
]

FORBIDDEN_PATH_PATTERNS = [
    "raw",
    "html",
    "review_ready_decisions",
    "claim_review_decisions",
]

STRONG_ADVICE_PATTERNS = [
    "推荐买入",
    "必涨",
    "稳赚",
    "满仓买",
    "直接买",
    "无脑买",
    "必跌",
]

RAW_EXCERPT_QUOTE_RE = re.compile(r"^>\s", re.MULTILINE)


def audit_skill_package(dist_dir: Path) -> dict[str, Any]:
    dist_dir = dist_dir.resolve()
    checks: list[dict[str, str]] = []

    for name in REQUIRED_FILES:
        checks.append(_check(name, (dist_dir / name).exists(), f"required file {name}"))

    skill_path = dist_dir / "SKILL.md"
    manifest_path = dist_dir / "MANIFEST.json"
    rules_path = dist_dir / "methodology_rules.jsonl"
    evidence_map_path = dist_dir / "rule_evidence_map.jsonl"

    rules_count = _jsonl_count(rules_path)
    evidence_count = _jsonl_count(evidence_map_path)
    checks.append(_check("rules_count", rules_count > 0, f"{rules_count} rules"))
    checks.append(_check("evidence_map_count", evidence_count > 0, f"{evidence_count} evidence mappings"))

    raw_excerpt_warning_count = _count_raw_excerpt_leaks(skill_path, evidence_map_path) if skill_path.exists() and evidence_map_path.exists() else 0
    checks.append(
        _check(
            "raw_excerpt_in_skill",
            raw_excerpt_warning_count == 0 and not _has_quote_blocks(skill_path),
            f"overlap_count={raw_excerpt_warning_count}",
        )
    )

    advice_hits = _find_strong_advice(skill_path) if skill_path.exists() else []
    checks.append(_check("investment_advice_language", not advice_hits, f"hits={advice_hits}"))

    forbidden_paths = _find_forbidden_paths(dist_dir)
    checks.append(_check("excluded_artifacts", not forbidden_paths, f"forbidden_paths={forbidden_paths}"))

    text_audit = audit_text_encoding_paths(
        [path for path in dist_dir.rglob("*") if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS]
    )
    checks.append(
        _check(
            "encoding",
            text_audit["corrupted_files"] == 0,
            f"corrupted_files={text_audit['corrupted_files']}",
        )
    )

    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    summary_payload = parse_review_summary(dist_dir / "review_summary.md") if (dist_dir / "review_summary.md").exists() else {}
    quality_payload = parse_skill_quality_report(dist_dir / "skill_quality_report.md") if (dist_dir / "skill_quality_report.md").exists() else {}

    manifest_checks = _check_manifest_consistency(manifest_payload, summary_payload, quality_payload, rules_count)
    checks.extend(manifest_checks)

    warnings = [check for check in checks if check["status"] != "ok"]
    audit = {
        "files": sorted(path.name for path in dist_dir.iterdir() if path.is_file()),
        "rules": rules_count,
        "evidence_mappings": evidence_count,
        "warnings": len(warnings),
        "checks": checks,
        "boundaries": [
            "package excludes raw crawl data",
            "package excludes review decision files",
            "package excludes HTML snapshots",
            "package uses accepted claims only for core rules",
            "package keeps needs_edit as uncertain evidence only",
        ],
        "text_encoding": text_audit,
    }
    return audit


def build_skill_package_audit_report(audit: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Package Audit",
        "",
        "## Summary",
        f"- files: {len(audit['files'])}",
        f"- rules: {audit['rules']}",
        f"- evidence mappings: {audit['evidence_mappings']}",
        f"- warnings: {audit['warnings']}",
        "",
        "## Checks",
        "",
        "| check | status | details |",
        "| --- | --- | --- |",
    ]
    for check in audit["checks"]:
        lines.append(f"| {check['check']} | {check['status']} | {check['details']} |")

    lines.extend(
        [
            "",
            "## Boundaries",
        ]
    )
    for item in audit["boundaries"]:
        lines.append(f"- {item}")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def _check(name: str, condition: bool, details: str) -> dict[str, str]:
    return {
        "check": name,
        "status": "ok" if condition else "warning",
        "details": details,
    }


def _jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _count_raw_excerpt_leaks(skill_path: Path, evidence_map_path: Path) -> int:
    skill_text = skill_path.read_text(encoding="utf-8")
    count = 0
    for line in evidence_map_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        for key in ("raw_excerpt", "claim_text"):
            text = str(payload.get(key) or "").strip()
            if len(text) >= 20 and text in skill_text:
                count += 1
                break
    return count


def _has_quote_blocks(skill_path: Path) -> bool:
    return RAW_EXCERPT_QUOTE_RE.search(skill_path.read_text(encoding="utf-8")) is not None


def _find_strong_advice(skill_path: Path) -> list[str]:
    text = skill_path.read_text(encoding="utf-8")
    hits: list[str] = []
    for pattern in STRONG_ADVICE_PATTERNS:
        if pattern in text and not _is_negated_or_descriptive(text, pattern):
            hits.append(pattern)
    return hits


def _is_negated_or_descriptive(text: str, pattern: str) -> bool:
    for match in re.finditer(re.escape(pattern), text):
        snippet = text[max(0, match.start() - 8): min(len(text), match.end() + 8)]
        if "不" in snippet or "不要" in snippet or "避免" in snippet:
            return True
    return False


def _find_forbidden_paths(dist_dir: Path) -> list[str]:
    forbidden: list[str] = []
    for path in dist_dir.rglob("*"):
        relative = path.relative_to(dist_dir).as_posix().lower()
        if any(pattern in relative for pattern in FORBIDDEN_PATH_PATTERNS):
            forbidden.append(relative)
    return forbidden


def _check_manifest_consistency(
    manifest_payload: dict[str, Any],
    review_summary: dict[str, Any],
    quality_payload: dict[str, Any],
    rules_count: int,
) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    counts = review_summary.get("counts", {})
    quality = quality_payload.get("rule_abstraction_checks", {})

    checks.append(
        _check(
            "manifest_rules_count",
            manifest_payload.get("rules_count") == rules_count,
            f"manifest={manifest_payload.get('rules_count')} actual={rules_count}",
        )
    )
    checks.append(
        _check(
            "manifest_accepted_count",
            manifest_payload.get("accepted_claims") == counts.get("accepted"),
            f"manifest={manifest_payload.get('accepted_claims')} summary={counts.get('accepted')}",
        )
    )
    checks.append(
        _check(
            "manifest_needs_edit_count",
            manifest_payload.get("needs_edit_claims") == counts.get("needs_edit"),
            f"manifest={manifest_payload.get('needs_edit_claims')} summary={counts.get('needs_edit')}",
        )
    )
    checks.append(
        _check(
            "manifest_quality_direct_excerpt",
            manifest_payload.get("quality", {}).get("direct_excerpt_in_rule_text") == quality.get("direct_excerpt_in_rule_text", 0),
            f"manifest={manifest_payload.get('quality', {}).get('direct_excerpt_in_rule_text')} quality={quality.get('direct_excerpt_in_rule_text', 0)}",
        )
    )
    checks.append(
        _check(
            "manifest_quality_warnings",
            manifest_payload.get("quality", {}).get("warnings") == quality_payload.get("warnings", 0),
            f"manifest={manifest_payload.get('quality', {}).get('warnings')} quality={quality_payload.get('warnings', 0)}",
        )
    )
    return checks
