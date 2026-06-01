"""Build a review queue for downloaded images and OCR results."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.models import Article, AuthorRole, Comment, ImageAsset, ImageOCR
from tgb_pipeline.storage import JSONLStore


def build_image_review_queue(raw_dir: Path, processed_dir: Path, reports_dir: Path) -> Path:
    image_path = raw_dir / "images_downloaded.jsonl"
    if not image_path.exists():
        image_path = raw_dir / "images.jsonl"
    images = JSONLStore(image_path, ImageAsset, "image_id").read_all()
    ocr_records = _read_optional(processed_dir / "image_ocr.jsonl", ImageOCR, "ocr_id")
    comments = _read_optional(raw_dir / "comments_all.jsonl", Comment, "comment_id")
    articles = _read_optional(raw_dir / "articles.jsonl", Article, "article_id")
    ocr_by_image = {record.image_id: record for record in ocr_records}
    comments_by_id = {comment.comment_id: comment for comment in comments}
    articles_by_id = {article.article_id: article for article in articles}

    review_items: list[tuple[ImageAsset, str, ImageOCR | None]] = []
    failed_downloads = 0
    missing_local_files = 0
    skipped_noise_images = 0
    low_confidence_ocr = 0

    for image in images:
        review_reasons: list[str] = []
        ocr_record = ocr_by_image.get(image.image_id)
        if image.raw.get("download_error"):
            failed_downloads += 1
            review_reasons.append("download_error")
        if not image.local_path or not Path(image.local_path).exists():
            missing_local_files += 1
            review_reasons.append("missing_local_file")
        if image.raw.get("probably_noise_image"):
            skipped_noise_images += 1
            review_reasons.append("probably_noise_image")
        if ocr_record is None and image.local_path and Path(image.local_path).exists():
            review_reasons.append("ocr_missing")
        if ocr_record is not None and ocr_record.raw.get("need_manual_review"):
            low_confidence_ocr += 1
            review_reasons.append("low_confidence_ocr")
        if image.source_type == "article_body":
            review_reasons.append("article_body_image")
        if image.keep_reason == "target_author_comment_image":
            review_reasons.append("target_author_comment_image")
        if comment := comments_by_id.get(image.comment_id or ""):
            if comment.author_role == AuthorRole.TARGET:
                review_reasons.append("target_author_comment_image")
        if _looks_like_screenshot(image):
            review_reasons.append("possible_chart_or_screenshot")
        if review_reasons:
            review_items.append((image, ", ".join(dict.fromkeys(review_reasons)), ocr_record))

    report_path = reports_dir / "image_ocr_review_queue.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Image OCR Review Queue",
        "",
        "## Summary",
        f"- total_images: {len(images)}",
        f"- downloaded_images: {sum(1 for image in images if image.local_path and Path(image.local_path).exists())}",
        f"- ocr_records: {len(ocr_records)}",
        f"- low_confidence_ocr: {low_confidence_ocr}",
        f"- failed_downloads: {failed_downloads}",
        f"- skipped_noise_images: {skipped_noise_images}",
        f"- missing_local_files: {missing_local_files}",
        "",
        "## Review Items",
        "",
    ]
    for image, reason, ocr_record in review_items:
        comment = comments_by_id.get(image.comment_id or "")
        article = articles_by_id.get(image.article_id or "")
        excerpt = ""
        if ocr_record and ocr_record.normalized_text:
            excerpt = ocr_record.normalized_text[:120]
        elif comment and comment.content_text:
            excerpt = comment.content_text[:120]
        elif article and article.content_text:
            excerpt = article.content_text[:120]
        lines.extend(
            [
                f"### {image.image_id}",
                "",
                f"- source_type: {image.source_type}",
                f"- article_id: {image.article_id}",
                f"- comment_id: {image.comment_id}",
                f"- local_path: {image.local_path}",
                f"- source_url: {image.source_url}",
                f"- before_text: {image.before_text}",
                f"- after_text: {image.after_text}",
                f"- review_reason: {reason}",
                f"- ocr_confidence: {ocr_record.confidence if ocr_record else None}",
                f"- ocr_text_excerpt: {excerpt}",
                "",
            ]
        )
    report_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return report_path


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()


def _looks_like_screenshot(image: ImageAsset) -> bool:
    text = " ".join(filter(None, [image.before_text, image.after_text, image.image_type, image.source_url]))
    lowered = text.casefold()
    return any(token in lowered for token in ("截图", "chart", "k线", "分时", "table", "screen"))
