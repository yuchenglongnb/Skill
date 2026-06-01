"""Draft a human-reviewable methodology profile from candidate claims."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def build_methodology_profile_draft(processed_dir: Path, reports_dir: Path) -> Path:
    claims = _read_claims(processed_dir)
    report_path = reports_dir / "methodology_profile_draft.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    tag_counts = Counter(tag for claim in claims for tag in claim.method_tags)
    source_counts = Counter(claim.source_type.value for claim in claims)
    ticker_counts = Counter(ticker for claim in claims for ticker in claim.mentioned_tickers)
    sector_counts = Counter(sector for claim in claims for sector in claim.mentioned_sectors)
    grouped: dict[str, list[MethodologyClaim]] = defaultdict(list)
    for claim in claims:
        for tag in claim.method_tags:
            grouped[tag].append(claim)
    lines = [
        "# Methodology Profile Draft",
        "",
        "## Summary",
        f"- total_claims: {len(claims)}",
        f"- top_method_tags: {tag_counts.most_common(10)}",
        f"- source_type_distribution: {dict(source_counts)}",
        f"- ticker_mentions: {ticker_counts.most_common(10)}",
        f"- sector_mentions: {sector_counts.most_common(10)}",
        "",
        "## Method Tags",
        "",
    ]
    for tag, count in tag_counts.most_common():
        lines.extend(
            [
                f"### {tag}",
                f"- claim count: {count}",
                "- representative claims:",
            ]
        )
        for claim in _representative_claims(grouped[tag])[:5]:
            lines.append(f"  - {claim.claim_id} / {_short(claim.raw_excerpt)}")
        lines.append("")
    lines.extend(
        [
            "## Caveats",
            "- 本报告是候选方法论画像，不是最终 Skill。",
            "- 所有 claim 均需人工复核。",
            "- OCR 来源未人工校验时不能作为强证据。",
            "",
        ]
    )
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return report_path


def _representative_claims(claims: list[MethodologyClaim]) -> list[MethodologyClaim]:
    priority = {"article": 0, "comment": 1, "interaction": 2, "image_ocr": 3}
    return sorted(claims, key=lambda claim: (priority.get(claim.source_type.value, 9), claim.claim_id))


def _short(text: str, limit: int = 80) -> str:
    return text[:limit]


def _read_claims(processed_dir: Path) -> list[MethodologyClaim]:
    path = processed_dir / "methodology_claims.jsonl"
    if not path.exists():
        return []
    return JSONLStore(path, MethodologyClaim, "claim_id").read_all()

