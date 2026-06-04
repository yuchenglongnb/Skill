"""Write accepted and uncertain skill evidence indices."""

from __future__ import annotations

import json
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.skill.profile_builder import primary_theme


def build_skill_evidence_index(
    accepted_claims: list[MethodologyClaim],
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "evidence_index.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for claim in accepted_claims:
            payload = {
                "claim_id": claim.claim_id,
                "theme": primary_theme(claim),
                "claim_text": claim.claim_text,
                "raw_excerpt": claim.raw_excerpt,
                "article_id": claim.article_id,
                "source_type": claim.source_type.value,
                "source_ids": claim.source_ids,
                "method_tags": claim.method_tags,
                "review_reason": claim.review_bucket or claim.review_status,
                "review_notes": claim.review_notes,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return output_path


def build_needs_edit_evidence_index(
    needs_edit_claims: list[MethodologyClaim],
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "needs_edit_evidence_index.jsonl"
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for claim in needs_edit_claims:
            payload = {
                "claim_id": claim.claim_id,
                "theme": primary_theme(claim),
                "claim_text": claim.claim_text,
                "raw_excerpt": claim.raw_excerpt,
                "article_id": claim.article_id,
                "source_type": claim.source_type.value,
                "source_ids": claim.source_ids,
                "method_tags": claim.method_tags,
                "review_reason": claim.review_bucket or claim.review_status,
                "review_notes": claim.review_notes,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return output_path
