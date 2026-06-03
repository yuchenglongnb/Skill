"""Reporting helpers for review-ready claim curation."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim


def build_review_ready_curation_report(
    all_review_ready_claims: list[MethodologyClaim],
    accepted: list[MethodologyClaim],
    rejected: list[MethodologyClaim],
    needs_edit: list[MethodologyClaim],
    reports_dir: Path,
) -> Path:
    total = len(all_review_ready_claims)
    unreviewed_count = max(total - len(accepted) - len(rejected) - len(needs_edit), 0)
    by_decision = Counter(
        claim.raw.get("review_decision", claim.review_status)
        for claim in [*accepted, *rejected, *needs_edit]
    )
    by_reason = Counter(
        claim.raw.get("review_reason")
        for claim in [*accepted, *rejected, *needs_edit]
        if claim.raw.get("review_reason")
    )
    accepted_by_tag = Counter(tag for claim in accepted for tag in claim.method_tags)
    rejected_by_reason = Counter(
        claim.raw.get("review_reason")
        for claim in rejected
        if claim.raw.get("review_reason")
    )
    source_distribution = Counter(claim.source_type.value for claim in [*accepted, *needs_edit])

    warnings: list[str] = []
    if not accepted:
        warnings.append("accepted claims are empty.")
    if total and unreviewed_count / total > 0.5:
        warnings.append("unreviewed claim ratio is high.")
    if total and len(rejected) / total < 0.05:
        warnings.append("rejected claim ratio is very low.")
    if any(claim.source_type.value == "image_ocr" and claim.evidence_level == "image_ocr_unreviewed" for claim in accepted):
        warnings.append("accepted claims contain OCR-unverified evidence.")

    report_path = reports_dir / "review_ready_curation_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Review-ready Curation Report",
        "",
        f"- total_review_ready_claims: {total}",
        f"- accepted_count: {len(accepted)}",
        f"- rejected_count: {len(rejected)}",
        f"- needs_edit_count: {len(needs_edit)}",
        f"- unreviewed_count: {unreviewed_count}",
        f"- by_decision: {dict(by_decision)}",
        f"- by_reason: {dict(by_reason)}",
        f"- accepted_by_tag: {dict(accepted_by_tag)}",
        f"- rejected_by_reason: {dict(rejected_by_reason)}",
        f"- source_type_distribution: {dict(source_distribution)}",
        "",
        "## Warnings",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- none")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
