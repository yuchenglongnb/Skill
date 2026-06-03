"""Reporting helpers for claim noise reduction."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim


def build_claim_noise_report(
    *,
    before_count: int | None,
    after_claims: list[MethodologyClaim],
    reports_dir: Path,
) -> Path:
    report_path = reports_dir / "claim_noise_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    after_count = len(after_claims)
    reduction = (before_count - after_count) if before_count is not None else None
    reduction_ratio = None
    if before_count:
        reduction_ratio = (before_count - after_count) / before_count

    by_tag = Counter(tag for claim in after_claims for tag in claim.method_tags)
    by_source_type = Counter(claim.source_type.value for claim in after_claims)
    by_reason = Counter(
        str((claim.raw.get("quality") or {}).get("reason", "unknown"))
        for claim in after_claims
    )

    lines = [
        "# Claim Noise Report",
        "",
        "## Summary",
        f"- before_count: {before_count if before_count is not None else 'n/a'}",
        f"- after_count: {after_count}",
        f"- reduction: {reduction if reduction is not None else 'n/a'}",
        (
            f"- reduction_ratio: {reduction_ratio:.2%}"
            if reduction_ratio is not None
            else "- reduction_ratio: n/a"
        ),
        "",
        "## Kept Claims by Tag",
        "| tag | count |",
        "| --- | ---: |",
    ]
    for tag, count in by_tag.most_common():
        lines.append(f"| {tag} | {count} |")
    if not by_tag:
        lines.append("| none | 0 |")

    lines.extend(
        [
            "",
            "## Kept Claims by Source Type",
            "| source_type | count |",
            "| --- | ---: |",
        ]
    )
    for source_type, count in by_source_type.most_common():
        lines.append(f"| {source_type} | {count} |")
    if not by_source_type:
        lines.append("| none | 0 |")

    lines.extend(
        [
            "",
            "## Quality Reasons",
            "| reason | count |",
            "| --- | ---: |",
        ]
    )
    for reason, count in by_reason.most_common():
        lines.append(f"| {reason} | {count} |")
    if not by_reason:
        lines.append("| none | 0 |")

    lines.extend(
        [
            "",
            "## Caveats",
            "- This report only covers generated claims.",
            "- Rejected candidate segments are not stored unless debug mode is enabled.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
