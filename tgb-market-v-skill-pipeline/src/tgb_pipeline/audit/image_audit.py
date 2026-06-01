"""Image inventory and review candidate reports."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import Article, Comment, ImageAsset
from tgb_pipeline.storage import JSONLStore

SUSPICIOUS_TOKENS = ("avatar", "logo", "icon", "loading", "qrcode", "app", "ad")


def build_image_inventory(raw_dir: Path, report_path: Path) -> dict:
    images = JSONLStore(raw_dir / "images.jsonl", ImageAsset, "image_id").read_all()
    articles = JSONLStore(raw_dir / "articles.jsonl", Article, "article_id").read_all()
    comments_all = JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").read_all()
    kept_comments = _read_optional(raw_dir / "comments.jsonl", Comment, "comment_id")
    aoch_comments = _read_optional(raw_dir / "aoch_discussions.jsonl", Comment, "comment_id")

    kept_comment_ids = {comment.comment_id for comment in kept_comments}
    aoch_comment_ids = {comment.comment_id for comment in aoch_comments}
    article_ids = {article.article_id for article in articles}
    images_by_source = Counter(image.source_type or "unknown" for image in images)
    images_by_article = Counter(image.article_id or "unknown" for image in images)
    candidates = [
        image for image in images if _needs_review(image, kept_comment_ids, aoch_comment_ids)
    ]
    report = {
        "total_images": len(images),
        "article_body_images": sum(1 for image in images if image.source_type == "article_body"),
        "comment_images": sum(1 for image in images if image.source_type == "comment"),
        "images_with_keep_reason": sum(1 for image in images if image.keep_reason),
        "images_without_keep_reason": sum(1 for image in images if not image.keep_reason),
        "images_by_source_type": dict(images_by_source),
        "images_by_article": dict(images_by_article),
        "review_candidates": candidates,
        "article_ids": article_ids,
        "comments_all_count": len(comments_all),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_inventory(report), encoding="utf-8")
    report_path.parent.joinpath("image_review_candidates.md").write_text(
        _render_candidates(candidates),
        encoding="utf-8",
    )
    return report


def _needs_review(image: ImageAsset, kept_comment_ids: set[str], aoch_comment_ids: set[str]) -> bool:
    source_url = (image.source_url or "").casefold()
    if any(token in source_url for token in SUSPICIOUS_TOKENS):
        return True
    if not image.before_text and not image.after_text and not image.image_type:
        return True
    if image.comment_id and image.comment_id not in kept_comment_ids and image.comment_id not in aoch_comment_ids:
        return True
    return False


def _render_inventory(report: dict) -> str:
    return "\n".join(
        [
            "# Image Inventory Report",
            "",
            "## Summary",
            f"- total_images: {report['total_images']}",
            f"- article_body_images: {report['article_body_images']}",
            f"- comment_images: {report['comment_images']}",
            f"- images_with_keep_reason: {report['images_with_keep_reason']}",
            f"- images_without_keep_reason: {report['images_without_keep_reason']}",
            f"- images_by_source_type: {report['images_by_source_type']}",
            f"- images_by_article: {report['images_by_article']}",
        ]
    ) + "\n"


def _render_candidates(candidates: list[ImageAsset]) -> str:
    lines = [
        "# Image Review Candidates",
        "",
        "| image_id | source_type | article_id | comment_id | keep_reason | image_type | before_text | after_text | source_url |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for image in candidates:
        lines.append(
            f"| {image.image_id} | {image.source_type or ''} | {image.article_id or ''} | "
            f"{image.comment_id or ''} | {image.keep_reason or ''} | {image.image_type or ''} | "
            f"{_short(image.before_text)} | {_short(image.after_text)} | {image.source_url} |"
        )
    return "\n".join(lines) + "\n"


def _short(value: str | None, limit: int = 40) -> str:
    if not value:
        return ""
    return value if len(value) <= limit else value[: limit - 3] + "..."


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()

