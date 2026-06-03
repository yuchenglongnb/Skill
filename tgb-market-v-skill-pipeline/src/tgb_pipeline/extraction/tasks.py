"""High-level claim extraction tasks."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.export.manifest import build_corpus_manifest
from tgb_pipeline.extraction.claim_extract import extract_claims_from_corpus
from tgb_pipeline.extraction.noise_report import build_claim_noise_report
from tgb_pipeline.extraction.profile import build_methodology_profile_draft
from tgb_pipeline.extraction.review_queue import build_claim_review_queue
from tgb_pipeline.extraction.review_ready import build_review_ready_claims
from tgb_pipeline.extraction.review_ready_report import build_review_ready_report
from tgb_pipeline.extraction.sampling_report import build_claim_sampling_report


def extract_claims_bundle(
    raw_dir: Path,
    processed_dir: Path,
    reports_dir: Path,
    *,
    max_per_tag: int = 500,
    sample_per_bucket: int = 20,
) -> list[Path]:
    _require(raw_dir / "articles.jsonl", "articles.jsonl not found; run crawl-articles first.")
    _require(raw_dir / "comments.jsonl", "comments.jsonl not found; run filter-comments first.")
    _require(raw_dir / "interactions.jsonl", "interactions.jsonl not found; run filter-comments first.")
    before_count = _read_existing_claim_count(processed_dir / "methodology_claims.jsonl")
    claims = extract_claims_from_corpus(raw_dir, processed_dir)
    noise_report_path = build_claim_noise_report(
        before_count=before_count,
        after_claims=claims,
        reports_dir=reports_dir,
    )
    review_ready_path, low_priority_path = build_review_ready_claims(
        processed_dir,
        reports_dir,
        max_per_tag=max_per_tag,
    )
    sampling_report_path = build_claim_sampling_report(
        processed_dir,
        reports_dir,
        sample_per_bucket=sample_per_bucket,
    )
    review_ready_report_path = build_review_ready_report(processed_dir, reports_dir)
    review_path = build_claim_review_queue(processed_dir, reports_dir)
    profile_path = build_methodology_profile_draft(processed_dir, reports_dir)
    manifest_path = build_corpus_manifest(raw_dir, processed_dir, reports_dir)
    return [
        processed_dir / "methodology_claims.jsonl",
        noise_report_path,
        review_ready_path,
        low_priority_path,
        sampling_report_path,
        review_ready_report_path,
        review_path,
        profile_path,
        manifest_path,
    ]


def build_review_ready_claims_bundle(
    raw_dir: Path,
    processed_dir: Path,
    reports_dir: Path,
    *,
    max_per_tag: int = 500,
    sample_per_bucket: int = 20,
) -> list[Path]:
    _require(processed_dir / "methodology_claims.jsonl", "methodology_claims.jsonl not found; run extract-claims first.")
    review_ready_path, low_priority_path = build_review_ready_claims(
        processed_dir,
        reports_dir,
        max_per_tag=max_per_tag,
    )
    sampling_report_path = build_claim_sampling_report(
        processed_dir,
        reports_dir,
        sample_per_bucket=sample_per_bucket,
    )
    review_ready_report_path = build_review_ready_report(processed_dir, reports_dir)
    manifest_path = build_corpus_manifest(raw_dir, processed_dir, reports_dir)
    return [review_ready_path, low_priority_path, sampling_report_path, review_ready_report_path, manifest_path]


def _require(path: Path, message: str) -> None:
    if not path.exists():
        raise ValueError(message)


def _read_existing_claim_count(path: Path) -> int | None:
    if not path.exists():
        return None
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
