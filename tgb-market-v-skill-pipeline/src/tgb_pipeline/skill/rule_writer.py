"""Writers for deterministic rule-mode skill outputs."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim, MethodologyRule
from tgb_pipeline.skill.rule_builder import THEME_ORDER, primary_theme


def write_methodology_rules(
    rules: list[MethodologyRule],
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "methodology_rules.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for rule in rules:
            payload = rule.model_dump(mode="json") if hasattr(rule, "model_dump") else json.loads(rule.json())
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return output_path


def write_needs_edit_worklist(
    needs_edit_claims: list[MethodologyClaim],
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[MethodologyClaim]] = defaultdict(list)
    for claim in needs_edit_claims:
        grouped[primary_theme(claim) or "未分类"].append(claim)

    lines = [
        "# Needs-edit Worklist",
        "",
        "## Summary",
        f"- total needs_edit: {len(needs_edit_claims)}",
        "",
        "## By Theme",
        "",
    ]
    for theme in [*THEME_ORDER, "未分类"]:
        theme_claims = grouped.get(theme, [])
        if not theme_claims:
            continue
        lines.append(f"### {theme}")
        for claim in theme_claims:
            lines.extend(
                [
                    f"- claim_id: `{claim.claim_id}`",
                    f"  - raw_excerpt: {claim.raw_excerpt}",
                    f"  - reason: {claim.review_bucket or claim.review_status}",
                    f"  - review_notes: {claim.review_notes or 'none'}",
                    f"  - suggested_action: {_suggested_action(claim)}",
                ]
            )
        lines.append("")

    output_path = output_dir / "needs_edit_worklist.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def write_skill_quality_report(
    audit_summary: dict,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Skill Quality Report",
        "",
        "## Summary",
        f"- accepted_claims: {audit_summary['accepted_claims']}",
        f"- generated_rules: {audit_summary['generated_rules']}",
        f"- needs_edit_claims: {audit_summary['needs_edit_claims']}",
        f"- rejected_claims: {audit_summary['rejected_claims']}",
        f"- unreviewed_claims: {audit_summary['unreviewed_claims']}",
        "",
        "## Rule Coverage by Theme",
        "| theme | rules | evidence claims |",
        "| --- | ---: | ---: |",
    ]
    for theme, counts in audit_summary["rule_coverage_by_theme"].items():
        lines.append(f"| {theme} | {counts['rules']} | {counts['evidence_claims']} |")

    lines.extend(["", "## Evidence Density", "| rule_id | evidence_count |", "| --- | ---: |"])
    for rule_id, evidence_count in audit_summary["evidence_density"].items():
        lines.append(f"| {rule_id} | {evidence_count} |")

    lines.extend(["", "## Warnings"])
    if audit_summary["warnings"]:
        for warning in audit_summary["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- none")

    output_path = output_dir / "skill_quality_report.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _suggested_action(claim: MethodologyClaim) -> str:
    notes = claim.review_notes or ""
    if "反讽" in notes or "打趣" in notes or "needs_human_check" in notes:
        return "confirm_context"
    if claim.review_status == "needs_edit":
        return "rewrite_neutral"
    return "reject_later"
