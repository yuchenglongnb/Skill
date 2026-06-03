"""Curated profile outputs for review-ready claim review."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim

PREFERRED_TAG_ORDER = [
    "量化影响",
    "成交额",
    "短线基础行情",
    "指数环境",
    "风控",
    "牛熊切换",
    "数字化/标准化",
]


def build_review_ready_curated_profile(
    accepted_claims: list[MethodologyClaim],
    needs_edit_claims: list[MethodologyClaim],
    reports_dir: Path,
) -> Path:
    curated = [*accepted_claims, *needs_edit_claims]
    tag_counts = Counter(tag for claim in curated for tag in claim.method_tags)
    source_counts = Counter(claim.source_type.value for claim in curated)
    grouped: dict[str, list[MethodologyClaim]] = defaultdict(list)
    for claim in curated:
        for tag in claim.method_tags:
            grouped[tag].append(claim)

    ordered_tags = [tag for tag in PREFERRED_TAG_ORDER if tag in tag_counts]
    ordered_tags.extend(tag for tag, _ in tag_counts.most_common() if tag not in ordered_tags)

    report_path = reports_dir / "review_ready_curated_profile.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Review-ready Curated Methodology Profile",
        "",
        "## Summary",
        f"- accepted_claims: {len(accepted_claims)}",
        f"- needs_edit_claims: {len(needs_edit_claims)}",
        f"- top_method_tags: {tag_counts.most_common(10)}",
        f"- source_type_distribution: {dict(source_counts)}",
        "",
        "## Core Method Tags",
        "",
    ]
    for tag in ordered_tags:
        lines.extend([f"### {tag}", f"- accepted count: {tag_counts[tag]}", "- representative claims:"])
        for claim in _representative_claims(grouped[tag])[:5]:
            lines.extend(
                [
                    f"  - {claim.claim_id}",
                    f"    - claim_text: {claim.claim_text}",
                    f"    - raw_excerpt: {(claim.raw_excerpt or '')[:160]}",
                    f"    - article_id: {claim.article_id}",
                    f"    - source_ids: {claim.source_ids}",
                ]
            )
        lines.append("")
    lines.extend(
        [
            "## Evidence Caveats",
            "- Only accepted and needs-edit claims are included here.",
            "- This profile is for methodology review, not investment advice.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def _representative_claims(claims: list[MethodologyClaim]) -> list[MethodologyClaim]:
    source_priority = {"article": 0, "comment": 1, "interaction": 2, "image_ocr": 3}
    review_priority = {"high": 0, "normal": 1, "low": 2}
    return sorted(
        claims,
        key=lambda claim: (
            source_priority.get(claim.source_type.value, 9),
            review_priority.get(claim.review_priority, 9),
            claim.claim_id,
        ),
    )
