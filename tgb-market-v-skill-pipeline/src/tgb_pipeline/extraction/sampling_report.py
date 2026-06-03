"""Sampling report for manual inspection of ranked claim buckets."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def build_claim_sampling_report(
    processed_dir: Path,
    reports_dir: Path,
    *,
    sample_per_bucket: int = 20,
) -> Path:
    all_claims = _read_optional(processed_dir / "methodology_claims.jsonl")
    review_ready = _read_optional(processed_dir / "review_ready_claims.jsonl")
    low_priority = _read_optional(processed_dir / "low_priority_methodology_claims.jsonl")
    combined = review_ready + low_priority

    by_priority = Counter(claim.review_priority for claim in combined)
    by_bucket = Counter((claim.review_bucket or "unbucketed") for claim in combined)
    by_source_type = Counter(claim.source_type.value for claim in combined)
    by_top_tags = Counter(tag for claim in review_ready for tag in claim.method_tags)
    grouped: dict[str, list[MethodologyClaim]] = defaultdict(list)
    for claim in combined:
        grouped[claim.review_bucket or "unbucketed"].append(claim)

    report_path = reports_dir / "claim_sampling_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Claim Sampling Report",
        "",
        "## Summary",
        f"- total_claims: {len(all_claims)}",
        f"- review_ready_claims: {len(review_ready)}",
        f"- low_priority_claims: {len(low_priority)}",
        f"- by_review_priority: {dict(by_priority)}",
        f"- by_review_bucket: {dict(by_bucket)}",
        f"- by_source_type: {dict(by_source_type)}",
        f"- by_top_tags: {dict(by_top_tags.most_common(10))}",
        "",
        "## Samples by Bucket",
        "",
    ]
    for bucket, claims in sorted(grouped.items()):
        lines.append(f"### {bucket}")
        for claim in claims[:sample_per_bucket]:
            lines.extend(
                [
                    f"- {claim.claim_id}",
                    f"  - tags: {claim.method_tags}",
                    f"  - source_type: {claim.source_type.value}",
                    f"  - raw_excerpt: {_truncate(claim.raw_excerpt)}",
                ]
            )
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def _read_optional(path: Path) -> list[MethodologyClaim]:
    if not path.exists():
        return []
    return JSONLStore(path, MethodologyClaim, "claim_id").read_all()


def _truncate(value: str, limit: int = 300) -> str:
    return value[:limit]
