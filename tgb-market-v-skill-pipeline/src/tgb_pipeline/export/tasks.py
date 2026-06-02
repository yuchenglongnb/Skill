"""High-level export pipeline for audit reports and markdown corpora."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.audit.article_inventory_audit import build_article_inventory_report
from tgb_pipeline.audit.author_audit import build_author_inventory
from tgb_pipeline.audit.comment_audit import build_comment_coverage_report
from tgb_pipeline.audit.crawl_error_audit import (
    build_crawl_error_report,
    mark_resolved_crawl_errors,
)
from tgb_pipeline.audit.filter_audit import build_filter_quality_report
from tgb_pipeline.audit.image_audit import build_image_inventory
from tgb_pipeline.config import TargetConfig
from tgb_pipeline.crawler.comment_checkpoint import (
    bootstrap_comment_page_states_from_snapshots,
    reconcile_comment_article_states,
)
from tgb_pipeline.export.export_markdown import export_all_corpora
from tgb_pipeline.export.manifest import build_corpus_manifest


def export_corpus_bundle(raw_dir: Path, processed_dir: Path, reports_dir: Path, target_config: TargetConfig) -> list[Path]:
    _require(raw_dir / "articles_index.jsonl", "articles_index.jsonl not found; run crawl-index first.")
    _require(raw_dir / "articles.jsonl", "articles.jsonl not found; run crawl-articles first.")
    _require(raw_dir / "images.jsonl", "images.jsonl not found; run crawl-articles or crawl-comments first.")
    _require(raw_dir / "comments_all.jsonl", "comments_all.jsonl not found; run crawl-comments first.")
    _require(raw_dir / "comments.jsonl", "comments.jsonl not found; run filter-comments first.")
    _require(raw_dir / "interactions.jsonl", "interactions.jsonl not found; run filter-comments first.")

    report_paths = [
        reports_dir / "article_inventory_report.md",
        reports_dir / "crawl_error_report.md",
        reports_dir / "comment_coverage_report.md",
        reports_dir / "author_inventory.md",
        reports_dir / "image_inventory_report.md",
        reports_dir / "filter_quality_report.md",
    ]
    bootstrap_comment_page_states_from_snapshots(raw_dir)
    reconcile_comment_article_states(raw_dir)
    mark_resolved_crawl_errors(raw_dir)
    build_article_inventory_report(raw_dir, report_paths[0])
    build_crawl_error_report(raw_dir, reports_dir)
    build_comment_coverage_report(raw_dir, report_paths[2])
    build_author_inventory(raw_dir, report_paths[3], target_config)
    build_image_inventory(raw_dir, report_paths[4])
    build_filter_quality_report(raw_dir, report_paths[5])
    corpus_paths = export_all_corpora(raw_dir, processed_dir)
    manifest_path = build_corpus_manifest(raw_dir, processed_dir, reports_dir)
    return [*report_paths, reports_dir / "image_review_candidates.md", *corpus_paths, manifest_path]


def _require(path: Path, message: str) -> None:
    if not path.exists():
        raise ValueError(message)
