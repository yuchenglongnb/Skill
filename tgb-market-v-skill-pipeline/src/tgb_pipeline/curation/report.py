"""Reporting helpers for claim curation and review suggestions."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim

STRONG_TAGS = {"情绪周期", "成交额", "短线基础行情", "量化影响", "市场结构", "指数环境"}
ANALOGY_TERMS = ("四季", "温度", "降雨", "天气", "春夏秋冬")


def suggest_review_reason(claim: MethodologyClaim) -> tuple[str, str]:
    text = claim.raw_excerpt or ""
    if text.endswith(("？", "?")):
        return "rejected", "pure_question"
    if not claim.method_tags:
        return "rejected", "not_methodology"
    if claim.evidence_level == "image_ocr_unreviewed":
        return "needs_edit", "ocr_unverified"
    if any(term in text for term in ANALOGY_TERMS) and not set(claim.method_tags).intersection(STRONG_TAGS):
        return "rejected", "analogy_or_background"
    if len(text.strip()) < 12:
        return "rejected", "too_generic"
    if claim.source_type.value in {"article", "comment"} and set(claim.method_tags).intersection(STRONG_TAGS):
        return "accepted", "core_methodology"
    return "needs_edit", "needs_human_check"


def build_claim_curation_report(
    all_claims: list[MethodologyClaim],
    accepted: list[MethodologyClaim],
    rejected: list[MethodologyClaim],
    needs_edit: list[MethodologyClaim],
    reports_dir: Path,
) -> Path:
    unreviewed_count = max(len(all_claims) - len(accepted) - len(rejected) - len(needs_edit), 0)
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
    source_distribution = Counter(claim.source_type.value for claim in accepted)
    warnings = []
    if not accepted:
        warnings.append("accepted claims are empty.")
    if all_claims and unreviewed_count / len(all_claims) > 0.5:
        warnings.append("unreviewed claim ratio is high.")
    if accepted and source_distribution.get("interaction", 0) / len(accepted) > 0.5:
        warnings.append("accepted interaction claims are disproportionately high.")
    if any(claim.source_type.value == "image_ocr" for claim in accepted):
        warnings.append("accepted OCR claims should be manually verified.")

    report_path = reports_dir / "claim_curation_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Claim Curation Report",
        "",
        f"- total_claims: {len(all_claims)}",
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

