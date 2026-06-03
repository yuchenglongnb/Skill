"""Summary report for review-ready claim subsets."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def build_review_ready_report(
    processed_dir: Path,
    reports_dir: Path,
) -> Path:
    all_claims = _read_optional(processed_dir / "methodology_claims.jsonl")
    review_ready = _read_optional(processed_dir / "review_ready_claims.jsonl")
    low_priority = _read_optional(processed_dir / "low_priority_methodology_claims.jsonl")
    by_tag = Counter(tag for claim in review_ready for tag in claim.method_tags)
    by_article = Counter(claim.article_id or "unknown" for claim in review_ready)
    low_bucket = Counter((claim.review_bucket or "unbucketed") for claim in low_priority)
    ratio = (len(review_ready) / len(all_claims)) if all_claims else 0.0

    report_path = reports_dir / "review_ready_claims_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Review Ready Claims Report",
        "",
        "## Summary",
        f"- methodology_claims: {len(all_claims)}",
        f"- review_ready_claims: {len(review_ready)}",
        f"- low_priority_claims: {len(low_priority)}",
        f"- reduction_ratio: {ratio:.2%}",
        "",
        "## Review Ready by Tag",
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
            "## Review Ready by Article",
            "| article_id | count |",
            "| --- | ---: |",
        ]
    )
    for article_id, count in by_article.most_common():
        lines.append(f"| {article_id} | {count} |")
    if not by_article:
        lines.append("| none | 0 |")

    lines.extend(
        [
            "",
            "## Low Priority Reasons",
            "| bucket | count |",
            "| --- | ---: |",
        ]
    )
    for bucket, count in low_bucket.most_common():
        lines.append(f"| {bucket} | {count} |")
    if not low_bucket:
        lines.append("| none | 0 |")

    lines.extend(
        [
            "",
            "## Caveats",
            "- review_ready_claims is a curated candidate subset, not final accepted methodology.",
            "- low_priority claims are not deleted.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def _read_optional(path: Path) -> list[MethodologyClaim]:
    if not path.exists():
        return []
    return JSONLStore(path, MethodologyClaim, "claim_id").read_all()
