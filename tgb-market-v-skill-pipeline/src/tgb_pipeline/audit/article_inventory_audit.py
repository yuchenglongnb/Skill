"""Audit article inventory coverage and crawl gaps."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import (
    Article,
    ArticleIndex,
    Comment,
    CommentArticleState,
    CrawlError,
    ImageAsset,
)
from tgb_pipeline.storage import JSONLStore


def build_article_inventory_report(raw_dir: Path, report_path: Path) -> dict:
    articles_index = _read_optional(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id")
    articles = _read_optional(raw_dir / "articles.jsonl", Article, "article_id")
    comments = _read_optional(raw_dir / "comments_all.jsonl", Comment, "comment_id")
    images = _read_optional(raw_dir / "images.jsonl", ImageAsset, "image_id")
    article_errors = _read_optional(raw_dir / "article_crawl_errors.jsonl", CrawlError, "error_id")
    comment_errors = _read_optional(raw_dir / "comment_crawl_errors.jsonl", CrawlError, "error_id")
    comment_states = _read_optional(
        raw_dir / "comment_article_states.jsonl",
        CommentArticleState,
        "article_id",
    )

    crawled_article_ids = {article.article_id for article in articles}
    comment_state_by_article = {state.article_id: state for state in comment_states}
    comments_by_article = Counter(comment.article_id for comment in comments)
    images_by_article = Counter(image.article_id for image in images if image.article_id)
    active_article_errors = [error for error in article_errors if not error.resolved]
    resolved_article_errors = [error for error in article_errors if error.resolved]
    active_comment_errors = [error for error in comment_errors if not error.resolved]
    resolved_comment_errors = [error for error in comment_errors if error.resolved]
    article_error_by_article = Counter(error.article_id for error in active_article_errors if error.article_id)
    comment_error_by_article = Counter(error.article_id for error in active_comment_errors if error.article_id)

    per_article = []
    for article in sorted(articles_index, key=lambda record: (record.published_date, record.article_id)):
        state = comment_state_by_article.get(article.article_id)
        per_article.append(
            {
                "article_id": article.article_id,
                "title": article.title,
                "published_date": article.published_date.isoformat(),
                "indexed": True,
                "article_crawled": article.article_id in crawled_article_ids,
                "comments_count": comments_by_article.get(article.article_id, 0),
                "images_count": images_by_article.get(article.article_id, 0),
                "max_comment_page": state.max_fetched_page if state else 0,
                "discovered_last_page": state.discovered_last_page if state else None,
                "comment_completed": state.completed if state else False,
                "max_limit_reached": state.max_limit_reached if state else False,
                "next_page_to_fetch": state.next_page_to_fetch if state else 1,
                "active_article_error": article_error_by_article.get(article.article_id, 0),
                "active_comment_error": comment_error_by_article.get(article.article_id, 0),
            }
        )

    report = {
        "indexed_articles": len(articles_index),
        "crawled_articles": len(crawled_article_ids),
        "articles_with_comments": sum(1 for count in comments_by_article.values() if count > 0),
        "total_comments": len(comments),
        "total_images": len(images),
        "article_crawl_errors": len(article_errors),
        "comment_crawl_errors": len(comment_errors),
        "active_article_errors": len(active_article_errors),
        "resolved_article_errors": len(resolved_article_errors),
        "active_comment_errors": len(active_comment_errors),
        "resolved_comment_errors": len(resolved_comment_errors),
        "per_article": per_article,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(report), encoding="utf-8")
    return report


def _render_report(report: dict) -> str:
    lines = [
        "# Article Inventory Report",
        "",
        "## Summary",
        f"- indexed_articles: {report['indexed_articles']}",
        f"- crawled_articles: {report['crawled_articles']}",
        f"- articles_with_comments: {report['articles_with_comments']}",
        f"- total_comments: {report['total_comments']}",
        f"- total_images: {report['total_images']}",
        f"- article_crawl_errors: {report['article_crawl_errors']}",
        f"- comment_crawl_errors: {report['comment_crawl_errors']}",
        f"- active_article_errors: {report['active_article_errors']}",
        f"- resolved_article_errors: {report['resolved_article_errors']}",
        f"- active_comment_errors: {report['active_comment_errors']}",
        f"- resolved_comment_errors: {report['resolved_comment_errors']}",
        "",
        "## Per Article",
        "| article_id | title | crawled | comments_count | max_page | last_page | completed | max_limit_reached | next_page_to_fetch | active_article_error | active_comment_error |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: |",
    ]
    for row in report["per_article"]:
        lines.append(
            f"| {row['article_id']} | {row['title']} | {row['article_crawled']} | "
            f"{row['comments_count']} | {row['max_comment_page']} | "
            f"{row['discovered_last_page'] or ''} | {row['comment_completed']} | "
            f"{row['max_limit_reached']} | {row['next_page_to_fetch']} | "
            f"{row['active_article_error']} | {row['active_comment_error']} |"
        )
    return "\n".join(lines) + "\n"


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()
