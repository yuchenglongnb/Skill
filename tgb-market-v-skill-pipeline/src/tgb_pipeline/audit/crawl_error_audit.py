"""Resolve historical crawl errors and report active failures."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from tgb_pipeline.models import Article, CommentPageState, CrawlError
from tgb_pipeline.storage import JSONLStore


def mark_resolved_crawl_errors(raw_dir: Path) -> tuple[int, int]:
    article_error_store = JSONLStore(
        raw_dir / "article_crawl_errors.jsonl",
        CrawlError,
        "error_id",
    )
    comment_error_store = JSONLStore(
        raw_dir / "comment_crawl_errors.jsonl",
        CrawlError,
        "error_id",
    )
    article_errors = article_error_store.read_all()
    comment_errors = comment_error_store.read_all()
    crawled_article_ids = {
        article.article_id
        for article in _read_optional(raw_dir / "articles.jsonl", Article, "article_id")
    }
    fetched_comment_pages = {
        (state.article_id, state.page_num)
        for state in _read_optional(
            raw_dir / "comment_page_states.jsonl",
            CommentPageState,
            "state_id",
        )
        if state.status in {"fetched", "empty", "max_limit_reached"}
    }

    resolved_article_errors = _resolve_article_errors(article_errors, crawled_article_ids)
    resolved_comment_errors = _resolve_comment_errors(comment_errors, fetched_comment_pages)
    if article_errors or (raw_dir / "article_crawl_errors.jsonl").exists():
        article_error_store.rewrite_all(article_errors)
    if comment_errors or (raw_dir / "comment_crawl_errors.jsonl").exists():
        comment_error_store.rewrite_all(comment_errors)
    return resolved_article_errors, resolved_comment_errors


def build_crawl_error_report(raw_dir: Path, reports_dir: Path) -> Path:
    article_errors = _read_optional(
        raw_dir / "article_crawl_errors.jsonl",
        CrawlError,
        "error_id",
    )
    comment_errors = _read_optional(
        raw_dir / "comment_crawl_errors.jsonl",
        CrawlError,
        "error_id",
    )
    active_article_errors = [error for error in article_errors if not error.resolved]
    active_comment_errors = [error for error in comment_errors if not error.resolved]
    report_path = reports_dir / "crawl_error_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _render_report(
            article_errors,
            comment_errors,
            active_article_errors,
            active_comment_errors,
        ),
        encoding="utf-8",
    )
    return report_path


def _resolve_article_errors(errors: list[CrawlError], crawled_article_ids: set[str]) -> int:
    resolved_count = 0
    for error in errors:
        if error.resolved or error.article_id not in crawled_article_ids:
            continue
        _mark_resolved(error, "article_exists_in_articles_jsonl")
        resolved_count += 1
    return resolved_count


def _resolve_comment_errors(
    errors: list[CrawlError],
    fetched_comment_pages: set[tuple[str, int]],
) -> int:
    resolved_count = 0
    for error in errors:
        page_num = error.raw.get("page_num")
        if (
            error.resolved
            or not error.article_id
            or not isinstance(page_num, int)
            or (error.article_id, page_num) not in fetched_comment_pages
        ):
            continue
        _mark_resolved(error, "comment_page_state_is_fetched")
        resolved_count += 1
    return resolved_count


def _mark_resolved(error: CrawlError, note: str) -> None:
    error.resolved = True
    error.resolved_at = datetime.now(UTC)
    error.resolved_by = "mark_resolved_crawl_errors"
    error.resolution_note = note


def _render_report(
    article_errors: list[CrawlError],
    comment_errors: list[CrawlError],
    active_article_errors: list[CrawlError],
    active_comment_errors: list[CrawlError],
) -> str:
    lines = [
        "# Crawl Error Report",
        "",
        "## Summary",
        f"- article_errors_total: {len(article_errors)}",
        f"- article_errors_resolved: {len(article_errors) - len(active_article_errors)}",
        f"- article_errors_active: {len(active_article_errors)}",
        f"- comment_errors_total: {len(comment_errors)}",
        f"- comment_errors_resolved: {len(comment_errors) - len(active_comment_errors)}",
        f"- comment_errors_active: {len(active_comment_errors)}",
        "",
        "## Active Article Errors",
        "| error_id | article_id | stage | error_type | error_message |",
        "| --- | --- | --- | --- | --- |",
    ]
    for error in active_article_errors:
        lines.append(
            f"| {error.error_id} | {error.article_id or ''} | {error.stage} | "
            f"{error.error_type} | {_one_line(error.error_message)} |"
        )
    lines.extend(
        [
            "",
            "## Active Comment Errors",
            "| error_id | article_id | page_num | stage | error_type | error_message |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
    )
    for error in active_comment_errors:
        lines.append(
            f"| {error.error_id} | {error.article_id or ''} | "
            f"{error.raw.get('page_num', '')} | {error.stage} | {error.error_type} | "
            f"{_one_line(error.error_message)} |"
        )
    return "\n".join(lines) + "\n"


def _one_line(value: str) -> str:
    return " ".join(value.split()).replace("|", "\\|")


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()
