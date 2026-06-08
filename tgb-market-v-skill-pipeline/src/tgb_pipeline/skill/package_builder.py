"""Build a distributable Skill v0.2 package."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tgb_pipeline.models import MethodologyRule
from tgb_pipeline.storage import JSONLStore

REQUIRED_PACKAGE_FILES = [
    "SKILL.md",
    "methodology_rules.jsonl",
    "rule_evidence_map.jsonl",
    "uncertainty_policy.md",
    "review_summary.md",
    "skill_quality_report.md",
]

OPTIONAL_PACKAGE_FILES = [
    "evidence_index.jsonl",
    "needs_edit_evidence_index.jsonl",
    "needs_edit_worklist.md",
]


def build_skill_package(
    source_dir: Path,
    dist_dir: Path,
    *,
    include_needs_edit: bool = True,
    version: str = "0.2",
) -> list[Path]:
    source_dir = source_dir.resolve()
    dist_dir.mkdir(parents=True, exist_ok=True)
    copied_paths: list[Path] = []

    for name in REQUIRED_PACKAGE_FILES:
        copied_paths.append(_copy_required_file(source_dir / name, dist_dir / name))

    evidence_index_path = source_dir / "evidence_index.jsonl"
    if evidence_index_path.exists():
        copied_paths.append(_copy_required_file(evidence_index_path, dist_dir / evidence_index_path.name))

    if include_needs_edit:
        for name in OPTIONAL_PACKAGE_FILES[1:]:
            source_path = source_dir / name
            if source_path.exists():
                copied_paths.append(_copy_required_file(source_path, dist_dir / name))

    copied_paths.append(_write_package_readme(source_dir, dist_dir))
    copied_paths.append(_write_manifest(source_dir, dist_dir, include_needs_edit=include_needs_edit, version=version))

    return copied_paths


def parse_review_summary(path: Path) -> dict[str, Any]:
    counts: dict[str, int] = {}
    accepted_by_tag: dict[str, int] = {}
    rule_count_by_theme: dict[str, int] = {}
    reviewed_packs: list[str] = []
    known_gaps: list[str] = []

    section = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            section = line[3:].strip().lower().replace(" ", "_")
            continue
        if not line.startswith("- "):
            continue
        value = line[2:]
        if section == "reviewed_packs":
            reviewed_packs.append(value)
        elif section == "counts" and ":" in value:
            key, count_text = value.split(":", 1)
            counts[key.strip()] = int(count_text.strip())
        elif section == "accepted_by_tag" and ":" in value:
            key, count_text = value.split(":", 1)
            accepted_by_tag[key.strip()] = int(count_text.strip())
        elif section == "rule_count_by_theme" and ":" in value:
            key, count_text = value.split(":", 1)
            rule_count_by_theme[key.strip()] = int(count_text.strip())
        elif section == "known_gaps":
            known_gaps.append(value)

    return {
        "counts": counts,
        "accepted_by_tag": accepted_by_tag,
        "rule_count_by_theme": rule_count_by_theme,
        "reviewed_packs": reviewed_packs,
        "known_gaps": known_gaps,
    }


def parse_skill_quality_report(path: Path) -> dict[str, Any]:
    summary: dict[str, int] = {}
    abstraction_checks: dict[str, int] = {}
    warnings_count = 0
    section = ""

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            section = line[3:].strip().lower().replace(" ", "_")
            continue
        if section == "summary" and line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            summary[key.strip()] = int(value.strip())
        elif section == "rule_abstraction_checks" and line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            abstraction_checks[key.strip().replace(" ", "_")] = int(value.strip())
        elif section == "warnings":
            if line == "- none":
                warnings_count = 0
            elif line.startswith("- "):
                warnings_count += 1

    return {
        "summary": summary,
        "rule_abstraction_checks": abstraction_checks,
        "warnings": warnings_count,
    }


def _copy_required_file(source_path: Path, destination_path: Path) -> Path:
    if not source_path.exists():
        raise FileNotFoundError(f"required skill package source missing: {source_path.as_posix()}")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination_path)
    return destination_path


def _write_package_readme(source_dir: Path, dist_dir: Path) -> Path:
    review_summary = parse_review_summary(source_dir / "review_summary.md")
    quality = parse_skill_quality_report(source_dir / "skill_quality_report.md")

    lines = [
        "# TGB Market V Skill",
        "",
        "This is a packaged Skill v0.2 generated from reviewed methodology claims.",
        "",
        "## What this skill does",
        "",
        "- Summarizes the target author's reviewed market methodology.",
        "- Helps analyze future posts/comments from the same author.",
        "- Provides rule-level themes and evidence claim IDs.",
        "",
        "## What this skill does not do",
        "",
        "- It does not provide investment advice.",
        "- It does not predict stock prices.",
        "- It does not generate buy/sell recommendations.",
        "- It does not treat sarcasm or jokes as literal methodology.",
        "",
        "## Files",
        "",
        "- `SKILL.md`: main skill instructions.",
        "- `methodology_rules.jsonl`: abstract rules.",
        "- `rule_evidence_map.jsonl`: evidence mapping for accepted claims.",
        "- `uncertainty_policy.md`: uncertainty and sarcasm handling.",
        "- `review_summary.md`: review status and corpus coverage.",
        "- `skill_quality_report.md`: package quality report.",
        "",
        "## Evidence Policy",
        "",
        "Core rules come from accepted claims only.",
        "Needs-edit claims are uncertain and must be manually checked.",
        "Rejected and unreviewed claims are excluded from core methodology.",
        "",
        "## Current Coverage",
        "",
        f"- accepted claims: {review_summary['counts'].get('accepted', 0)}",
        f"- rules: {quality['summary'].get('generated_rules', 0)}",
        f"- reviewed packs: {', '.join(review_summary['reviewed_packs']) if review_summary['reviewed_packs'] else 'none'}",
        f"- known gaps: {len(review_summary['known_gaps'])}",
        "",
    ]

    output_path = dist_dir / "README.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _write_manifest(source_dir: Path, dist_dir: Path, *, include_needs_edit: bool, version: str) -> Path:
    review_summary = parse_review_summary(source_dir / "review_summary.md")
    quality = parse_skill_quality_report(source_dir / "skill_quality_report.md")
    rules = JSONLStore(source_dir / "methodology_rules.jsonl", MethodologyRule, "rule_id").read_all()
    files = sorted({path.name for path in dist_dir.iterdir() if path.is_file()} | {"MANIFEST.json"})

    manifest = {
        "package_name": "tgb_market_v_skill",
        "version": version,
        "generated_at": datetime.now(UTC).isoformat(),
        "source_commit": _git_head(source_dir),
        "source_pipeline": "tgb-market-v-skill-pipeline",
        "accepted_claims": review_summary["counts"].get("accepted", 0),
        "needs_edit_claims": review_summary["counts"].get("needs_edit", 0) if include_needs_edit else 0,
        "rejected_claims": review_summary["counts"].get("rejected", 0),
        "unreviewed_claims": review_summary["counts"].get("unreviewed", 0),
        "rules_count": len(rules),
        "themes": review_summary["rule_count_by_theme"],
        "files": files,
        "quality": {
            "direct_excerpt_in_rule_text": quality["rule_abstraction_checks"].get("direct_excerpt_in_rule_text", 0),
            "generic_rule_titles": quality["rule_abstraction_checks"].get("generic_rule_titles", 0),
            "raw_excerpt_in_skill_md": quality["rule_abstraction_checks"].get("raw_excerpt_in_skill_md", 0),
            "warnings": quality["warnings"],
        },
        "boundaries": [
            "not_investment_advice",
            "no_stock_prediction",
            "accepted_claims_only_for_core_rules",
            "needs_edit_is_uncertain",
            "rejected_unreviewed_excluded",
            "sarcasm_requires_human_check",
        ],
    }
    output_path = dist_dir / "MANIFEST.json"
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def _git_head(source_dir: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=source_dir.parent.parent,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
    except Exception:
        return None
    return result.stdout.strip() or None
