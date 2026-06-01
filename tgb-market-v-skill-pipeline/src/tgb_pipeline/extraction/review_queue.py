"""Markdown review queue for methodology claims."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def build_claim_review_queue(processed_dir: Path, reports_dir: Path) -> Path:
    claims = _read_claims(processed_dir)
    report_path = reports_dir / "claim_review_queue.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    by_source_type = Counter(claim.source_type.value for claim in claims)
    by_method_tag = Counter(tag for claim in claims for tag in claim.method_tags)
    by_review_status = Counter(claim.review_status for claim in claims)
    by_evidence_level = Counter(claim.evidence_level for claim in claims)
    lines = [
        "# Claim Review Queue",
        "",
        "## Summary",
        f"- total_claims: {len(claims)}",
        f"- by_source_type: {dict(by_source_type)}",
        f"- by_method_tag: {dict(by_method_tag)}",
        f"- by_review_status: {dict(by_review_status)}",
        f"- by_evidence_level: {dict(by_evidence_level)}",
        "",
        "## Review Items",
        "",
    ]
    for claim in claims:
        lines.extend(
            [
                f"### {claim.claim_id}",
                "",
                f"- source_type: {claim.source_type.value}",
                f"- source_ids: {claim.source_ids}",
                f"- article_id: {claim.article_id}",
                f"- source_author: {claim.source_author}",
                f"- method_tags: {claim.method_tags}",
                f"- mentioned_tickers: {claim.mentioned_tickers}",
                f"- mentioned_sectors: {claim.mentioned_sectors}",
                f"- direction: {claim.direction}",
                f"- horizon: {claim.horizon}",
                f"- evidence_level: {claim.evidence_level}",
                f"- review_status: {claim.review_status}",
                "",
                "Raw excerpt:",
                f"> {_truncate(claim.raw_excerpt)}",
                "",
                "Candidate claim:",
                f"> {_truncate(claim.claim_text)}",
                "",
            ]
        )
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return report_path


def _truncate(value: str, limit: int = 500) -> str:
    return value[:limit]


def _read_claims(processed_dir: Path) -> list[MethodologyClaim]:
    path = processed_dir / "methodology_claims.jsonl"
    if not path.exists():
        return []
    return JSONLStore(path, MethodologyClaim, "claim_id").read_all()

