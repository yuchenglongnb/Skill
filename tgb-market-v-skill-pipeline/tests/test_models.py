from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from tgb_pipeline.models import AuthorRole, Comment, ImageAsset, ImageOCR


def test_member_comment_requires_target_interaction_for_corpus() -> None:
    comment = Comment(
        comment_id="comment-1",
        article_id="article-1",
        author_name="普通成员",
        author_role=AuthorRole.MEMBER,
        raw_content="原始评论",
    )

    assert comment.eligible_for_corpus is False

    comment.target_author_interacted = True
    assert comment.eligible_for_corpus is True


def test_aoch_has_dedicated_model_marker() -> None:
    comment = Comment(
        comment_id="comment-aoch",
        article_id="article-1",
        author_name="Aoch",
        author_role=AuthorRole.AOCH,
        published_at=datetime(2023, 1, 15, tzinfo=UTC),
        raw_content="Aoch 原始评论",
    )

    assert comment.is_aoch is True
    assert comment.eligible_for_corpus is False


def test_image_requires_parent_and_ocr_remains_separate() -> None:
    with pytest.raises(ValidationError):
        ImageAsset(
            image_id="image-1",
            source_url="https://example.test/image.png",
            page_url="https://example.test/article",
        )

    ocr = ImageOCR(
        ocr_id="ocr-1",
        image_id="image-1",
        engine="test-engine",
        raw_text="图片原始识别文本",
        normalized_text="图片识别文本",
    )
    assert ocr.raw_text != ocr.normalized_text

