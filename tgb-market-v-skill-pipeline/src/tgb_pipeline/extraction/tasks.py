"""High-level claim extraction tasks."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.export.manifest import build_corpus_manifest
from tgb_pipeline.extraction.claim_extract import extract_claims_from_corpus
from tgb_pipeline.extraction.profile import build_methodology_profile_draft
from tgb_pipeline.extraction.review_queue import build_claim_review_queue


def extract_claims_bundle(raw_dir: Path, processed_dir: Path, reports_dir: Path) -> list[Path]:
    _require(raw_dir / "articles.jsonl", "articles.jsonl not found; run crawl-articles first.")
    _require(raw_dir / "comments.jsonl", "comments.jsonl not found; run filter-comments first.")
    _require(raw_dir / "interactions.jsonl", "interactions.jsonl not found; run filter-comments first.")
    extract_claims_from_corpus(raw_dir, processed_dir)
    review_path = build_claim_review_queue(processed_dir, reports_dir)
    profile_path = build_methodology_profile_draft(processed_dir, reports_dir)
    manifest_path = build_corpus_manifest(raw_dir, processed_dir, reports_dir)
    return [processed_dir / "methodology_claims.jsonl", review_path, profile_path, manifest_path]


def _require(path: Path, message: str) -> None:
    if not path.exists():
        raise ValueError(message)
