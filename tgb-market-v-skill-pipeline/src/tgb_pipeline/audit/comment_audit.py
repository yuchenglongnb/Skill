"""Coverage audit for crawled comments and snapshots."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from tgb_pipeline.models import ArticleIndex, Comment, ImageAsset
from tgb_pipeline.storage import JSONLStore


def build_comment_coverage_report(raw_dir: Path, report_path: Path) -> dict:
    articles = JSONLStore(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id").read_all()
    comments = JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").read_all()
    images = JSONLStore(raw_dir / "images.jsonl", ImageAsset, "image_id").read_all()
    snapshots = list((raw_dir / "html").glob("*_comments_page_*.html"))

    comments_by_article: Counter[str] = Counter(comment.article_id for comment in comments)
    comments_by_page: Counter[str] = Counter(
        f"{comment.article_id}:page_{comment.page_num or 0}" for comment in comments
    )
    comment_images = [image for image in images if image.source_type == "comment"]
    images_by_page: Counter[str] = Counter(
        f"{image.article_id}:page_{image.raw.get('page_num', 0)}" for image in comment_images
    )
    pages_by_article: defaultdict[str, set[int]] = defaultdict(set)
    for snapshot in snapshots:
        article_id, page_num = _snapshot_parts(snapshot.name)
        pages_by_article[article_id].add(page_num)

    per_article_rows = []
    for article in articles:
        parsed_comments = comments_by_article.get(article.article_id, 0)
        expected = article.reply_count
        needs_review = bool(expected and parsed_comments < max(int(expected * 0.7), expected - 20))
        per_article_rows.append(
            {
                "article_id": article.article_id,
                "title": article.title,
                "expected_reply_count": expected,
                "parsed_comments": parsed_comments,
                "comment_pages": len(pages_by_article.get(article.article_id, set())),
                "parsed_images": sum(1 for image in comment_images if image.article_id == article.article_id),
                "needs_review": needs_review,
            }
        )

    report = {
        "article_count": len(articles),
        "total_raw_comments": len(comments),
        "total_comment_images": len(comment_images),
        "total_comment_pages_snapshots": len(snapshots),
        "comments_by_article": dict(comments_by_article),
        "comments_by_page": dict(comments_by_page),
        "images_by_page": dict(images_by_page),
        "per_article": per_article_rows,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(report), encoding="utf-8")
    return report


def _render_report(report: dict) -> str:
    lines = [
        "# Comment Coverage Report",
        "",
        "## Summary",
        f"- article_count: {report['article_count']}",
        f"- total_raw_comments: {report['total_raw_comments']}",
        f"- total_comment_images: {report['total_comment_images']}",
        f"- total_comment_pages_snapshots: {report['total_comment_pages_snapshots']}",
        f"- comments_by_article: {report['comments_by_article']}",
        f"- comments_by_page: {report['comments_by_page']}",
        f"- images_by_page: {report['images_by_page']}",
        "",
        "## Per Article",
        "| article_id | title | expected_reply_count | parsed_comments | comment_pages | parsed_images | needs_review |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in report["per_article"]:
        lines.append(
            f"| {row['article_id']} | {row['title']} | {row['expected_reply_count']} | "
            f"{row['parsed_comments']} | {row['comment_pages']} | {row['parsed_images']} | "
            f"{row['needs_review']} |"
        )
    return "\n".join(lines) + "\n"


def _snapshot_parts(name: str) -> tuple[str, int]:
    stem = Path(name).stem
    article_id, _, suffix = stem.partition("_comments_page_")
    return article_id, int(suffix or 0)

