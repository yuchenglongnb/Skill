"""Build a curated methodology profile from reviewed claims."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim


def build_curated_methodology_profile(
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

    report_path = reports_dir / "curated_methodology_profile.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Curated Methodology Profile",
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
    for tag, count in tag_counts.most_common():
        lines.extend([f"### {tag}", f"- accepted count: {count}", "- representative claims:"])
        for claim in _representative_claims(grouped[tag])[:5]:
            lines.extend(
                [
                    f"  - {claim.claim_id}",
                    f"    - claim_text: {claim.claim_text}",
                    f"    - raw_excerpt: {claim.raw_excerpt[:120]}",
                    f"    - source_ids: {claim.source_ids}",
                ]
            )
        lines.append("")
    lines.extend(
        [
            "## Evidence Caveats",
            "- OCR claims require manual verification.",
            "- Interaction claims only include target-author text.",
            "- This is not investment advice.",
            "",
        ]
    )
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return report_path


def _representative_claims(claims: list[MethodologyClaim]) -> list[MethodologyClaim]:
    priority = {"article": 0, "comment": 1, "interaction": 2, "image_ocr": 3}
    return sorted(claims, key=lambda claim: (priority.get(claim.source_type.value, 9), claim.claim_id))

