from datetime import UTC, datetime

from tgb_pipeline.images.review_queue import build_image_review_queue
from tgb_pipeline.models import Article, AuthorRole, Comment, ImageAsset, ImageOCR
from tgb_pipeline.storage import JSONLStore


def test_build_image_review_queue_includes_low_confidence_and_article_images(tmp_path) -> None:
    raw_dir = tmp_path / "data" / "raw" / "tgb"
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    local_path = tmp_path / "img.png"
    local_path.write_bytes(b"placeholder")

    JSONLStore(raw_dir / "articles.jsonl", Article, "article_id").append(
        Article(
            article_id="a1",
            title="title",
            author_name="target",
            published_at=datetime(2023, 1, 15, tzinfo=UTC),
            url="https://example.test/a1",
            raw_content="[IMAGE: img-1]",
            content_text="[IMAGE: img-1]",
        )
    )
    JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").append(
        Comment(
            comment_id="c1",
            article_id="a1",
            author_name="target",
            author_role=AuthorRole.TARGET,
            published_at=datetime(2023, 1, 16, tzinfo=UTC),
            raw_content="[IMAGE: img-2]",
            content_text="[IMAGE: img-2]",
        )
    )
    JSONLStore(raw_dir / "images_downloaded.jsonl", ImageAsset, "image_id").append_many(
        [
            ImageAsset(
                image_id="img-1",
                article_id="a1",
                source_url="https://example.test/chart.png",
                page_url="https://example.test/a1",
                local_path=local_path.as_posix(),
                source_type="article_body",
                before_text="chart",
            ),
            ImageAsset(
                image_id="img-2",
                article_id="a1",
                comment_id="c1",
                source_url="https://example.test/comment.png",
                page_url="https://example.test/a1",
                local_path=local_path.as_posix(),
                source_type="comment",
            ),
        ]
    )
    JSONLStore(processed_dir / "image_ocr.jsonl", ImageOCR, "ocr_id").append(
        ImageOCR(
            ocr_id="ocr-img-2-rapidocr",
            image_id="img-2",
            engine="rapidocr",
            raw_text="low confidence",
            normalized_text="low confidence",
            confidence=0.5,
            raw={"need_manual_review": True},
        )
    )

    report_path = build_image_review_queue(raw_dir, processed_dir, reports_dir)
    report = report_path.read_text(encoding="utf-8")

    assert "img-1" in report
    assert "article_body_image" in report
    assert "img-2" in report
    assert "low_confidence_ocr" in report
    assert "target_author_comment_image" in report
