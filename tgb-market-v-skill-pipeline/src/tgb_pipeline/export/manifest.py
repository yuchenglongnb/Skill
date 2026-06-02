"""Manifest for derived corpus exports and reports."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from tgb_pipeline.models import (
    Article,
    ArticleIndex,
    ArticleSeedCandidate,
    Comment,
    CommentArticleState,
    CommentPageState,
    CrawlError,
    ImageAsset,
    ImageOCR,
    Interaction,
)
from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def build_corpus_manifest(raw_dir: Path, processed_dir: Path, reports_dir: Path) -> Path:
    downloaded_images = _read_optional(raw_dir / "images_downloaded.jsonl", ImageAsset, "image_id")
    interim_dir = raw_dir.parent.parent / "interim" / raw_dir.name
    candidates_path = interim_dir / "article_seed_candidates.jsonl"
    seeds_config_path = Path("configs/article_seeds.yaml")
    article_errors = _read_optional(raw_dir / "article_crawl_errors.jsonl", CrawlError, "error_id")
    comment_errors = _read_optional(raw_dir / "comment_crawl_errors.jsonl", CrawlError, "error_id")
    counts = {
        "article_index": len(_read_optional(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id")),
        "article_seed_candidates": len(_read_optional(candidates_path, ArticleSeedCandidate, "candidate_id")),
        "article_seed_candidates_report": 1 if (reports_dir / "article_seed_candidates.md").exists() else 0,
        "article_seeds_config_count": _count_article_seeds_config(seeds_config_path),
        "articles": len(_read_optional(raw_dir / "articles.jsonl", Article, "article_id")),
        "article_crawl_errors": len(_read_optional(raw_dir / "article_crawl_errors.jsonl", CrawlError, "error_id")),
        "active_article_crawl_errors": sum(1 for error in article_errors if not error.resolved),
        "resolved_article_crawl_errors": sum(1 for error in article_errors if error.resolved),
        "comments_all": len(_read_optional(raw_dir / "comments_all.jsonl", Comment, "comment_id")),
        "comment_crawl_errors": len(_read_optional(raw_dir / "comment_crawl_errors.jsonl", CrawlError, "error_id")),
        "active_comment_crawl_errors": sum(1 for error in comment_errors if not error.resolved),
        "resolved_comment_crawl_errors": sum(1 for error in comment_errors if error.resolved),
        "comment_page_states": len(_read_optional(raw_dir / "comment_page_states.jsonl", CommentPageState, "state_id")),
        "comment_article_states": len(_read_optional(raw_dir / "comment_article_states.jsonl", CommentArticleState, "article_id")),
        "crawl_error_report": 1 if (reports_dir / "crawl_error_report.md").exists() else 0,
        "comment_state_warnings": 1 if (reports_dir / "comment_state_warnings.md").exists() else 0,
        "comment_completion_plan": 1 if (interim_dir / "comment_completion_plan.json").exists() else 0,
        "comment_completion_plan_report": 1 if (reports_dir / "comment_completion_plan.md").exists() else 0,
        "comments": len(_read_optional(raw_dir / "comments.jsonl", Comment, "comment_id")),
        "interactions": len(_read_optional(raw_dir / "interactions.jsonl", Interaction, "interaction_id")),
        "images": len(_read_optional(raw_dir / "images.jsonl", ImageAsset, "image_id")),
        "aoch_discussions": len(_read_optional(raw_dir / "aoch_discussions.jsonl", Comment, "comment_id")),
        "images_downloaded": len(downloaded_images),
        "image_ocr": len(_read_optional(processed_dir / "image_ocr.jsonl", ImageOCR, "ocr_id")),
        "image_ocr_review_queue": 1 if (reports_dir / "image_ocr_review_queue.md").exists() else 0,
        "methodology_claims": len(_read_optional(processed_dir / "methodology_claims.jsonl", MethodologyClaim, "claim_id")),
        "claim_review_queue": 1 if (reports_dir / "claim_review_queue.md").exists() else 0,
        "methodology_profile_draft": 1 if (reports_dir / "methodology_profile_draft.md").exists() else 0,
        "accepted_methodology_claims": len(_read_optional(processed_dir / "accepted_methodology_claims.jsonl", MethodologyClaim, "claim_id")),
        "rejected_methodology_claims": len(_read_optional(processed_dir / "rejected_methodology_claims.jsonl", MethodologyClaim, "claim_id")),
        "needs_edit_methodology_claims": len(_read_optional(processed_dir / "needs_edit_methodology_claims.jsonl", MethodologyClaim, "claim_id")),
        "claim_review_decisions": 1 if (processed_dir / "claim_review_decisions.yaml").exists() else 0,
        "curated_methodology_profile": 1 if (reports_dir / "curated_methodology_profile.md").exists() else 0,
        "claim_curation_report": 1 if (reports_dir / "claim_curation_report.md").exists() else 0,
    }
    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "inputs": [
            _relative(raw_dir / "articles_index.jsonl"),
            _relative(raw_dir / "articles.jsonl"),
            _relative(raw_dir / "article_crawl_errors.jsonl"),
            _relative(raw_dir / "comments_all.jsonl"),
            _relative(raw_dir / "comment_crawl_errors.jsonl"),
            _relative(raw_dir / "comment_page_states.jsonl"),
            _relative(raw_dir / "comment_article_states.jsonl"),
            _relative(raw_dir / "comments.jsonl"),
            _relative(raw_dir / "interactions.jsonl"),
            _relative(raw_dir / "images.jsonl"),
        ],
        "outputs": [
            _relative(processed_dir / "target_author_corpus.md"),
            _relative(processed_dir / "interaction_pairs.md"),
            _relative(processed_dir / "aoch_corpus.md"),
            _relative(processed_dir / "image_ocr.jsonl"),
            _relative(processed_dir / "methodology_claims.jsonl"),
            _relative(processed_dir / "accepted_methodology_claims.jsonl"),
            _relative(processed_dir / "rejected_methodology_claims.jsonl"),
            _relative(processed_dir / "needs_edit_methodology_claims.jsonl"),
            _relative(processed_dir / "claim_review_decisions.yaml"),
        ],
        "reports": [
            _relative(reports_dir / "comment_coverage_report.md"),
            _relative(reports_dir / "article_inventory_report.md"),
            _relative(reports_dir / "crawl_error_report.md"),
            _relative(reports_dir / "comment_state_warnings.md"),
            _relative(reports_dir / "comment_completion_plan.md"),
            _relative(reports_dir / "article_seed_candidates.md"),
            _relative(reports_dir / "author_inventory.md"),
            _relative(reports_dir / "image_inventory_report.md"),
            _relative(reports_dir / "image_review_candidates.md"),
            _relative(reports_dir / "filter_quality_report.md"),
            _relative(reports_dir / "image_ocr_review_queue.md"),
            _relative(reports_dir / "claim_review_queue.md"),
            _relative(reports_dir / "methodology_profile_draft.md"),
            _relative(reports_dir / "curated_methodology_profile.md"),
            _relative(reports_dir / "claim_curation_report.md"),
        ],
        "counts": counts,
        "has_aoch": counts["aoch_discussions"] > 0,
        "downloaded_images_path": _relative(raw_dir / "images_downloaded.jsonl"),
        "image_ocr_path": _relative(processed_dir / "image_ocr.jsonl"),
        "methodology_claims_path": _relative(processed_dir / "methodology_claims.jsonl"),
        "claim_review_decisions_path": _relative(processed_dir / "claim_review_decisions.yaml"),
    }
    output_path = processed_dir / "corpus_manifest.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path


def _relative(path: Path) -> str:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        return resolved.relative_to(cwd).as_posix()
    except ValueError:
        return path.as_posix()


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()
def _count_article_seeds_config(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        import yaml

        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except Exception:
        return 0
    articles = data.get("articles", [])
    return len(articles) if isinstance(articles, list) else 0
