"""Audit article inventory coverage and crawl gaps."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import Article, ArticleIndex, Comment, CrawlError, ImageAsset
from tgb_pipeline.storage import JSONLStore


def build_article_inventory_report(raw_dir: Path, report_path: Path) -> dict:
    articles_index = _read_optional(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id")
    articles = _read_optional(raw_dir / "articles.jsonl", Article, "article_id")
    comments = _read_optional(raw_dir / "comments_all.jsonl", Comment, "comment_id")
    images = _read_optional(raw_dir / "images.jsonl", ImageAsset, "image_id")
    article_errors = _read_optional(raw_dir / "article_crawl_errors.jsonl", CrawlError, "error_id")
    comment_errors = _read_optional(raw_dir / "comment_crawl_errors.jsonl", CrawlError, "error_id")

    crawled_article_ids = {article.article_id for article in articles}
    comments_by_article = Counter(comment.article_id for comment in comments)
    images_by_article = Counter(image.article_id for image in images if image.article_id)
    article_error_by_article = Counter(error.article_id for error in article_errors if error.article_id)
    comment_error_by_article = Counter(error.article_id for error in comment_errors if error.article_id)

    per_article = []
    for article in sorted(articles_index, key=lambda record: (record.published_date, record.article_id)):
        per_article.append(
            {
                "article_id": article.article_id,
                "title": article.title,
                "published_date": article.published_date.isoformat(),
                "indexed": True,
                "article_crawled": article.article_id in crawled_article_ids,
                "comments_count": comments_by_article.get(article.article_id, 0),
                "images_count": images_by_article.get(article.article_id, 0),
                "article_error": article_error_by_article.get(article.article_id, 0),
                "comment_error": comment_error_by_article.get(article.article_id, 0),
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
        "",
        "## Per Article",
        "| article_id | title | published_date | indexed | article_crawled | comments_count | images_count | article_error | comment_error |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in report["per_article"]:
        lines.append(
            f"| {row['article_id']} | {row['title']} | {row['published_date']} | "
            f"{row['indexed']} | {row['article_crawled']} | {row['comments_count']} | "
            f"{row['images_count']} | {row['article_error']} | {row['comment_error']} |"
        )
    return "\n".join(lines) + "\n"


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()
