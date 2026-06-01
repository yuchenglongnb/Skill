from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from tgb_pipeline.models import AuthorRole, ClaimSourceType, Comment, ImageAsset, ImageOCR, MethodologyClaim


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
    assert comment.eligible_for_aoch_corpus is True


def test_image_asset_supports_structured_evidence_fields() -> None:
    image = ImageAsset(
        image_id="image-structured",
        article_id="article-1",
        source_url="https://example.test/image.png",
        page_url="https://example.test/article",
        source_type="article_body",
        position_index=2,
        before_text="前文片段",
        after_text="后文片段",
        keep_reason="target_author_article_image",
        review_status="unreviewed",
    )

    assert image.source_type == "article_body"
    assert image.position_index == 2
    assert image.before_text == "前文片段"
    assert image.after_text == "后文片段"
    assert image.keep_reason == "target_author_article_image"
    assert image.review_status == "unreviewed"


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


def test_methodology_claim_supports_extended_fields() -> None:
    claim = MethodologyClaim(
        claim_id="claim-1",
        claim_text="情绪周期切换要结合成交额。",
        raw_excerpt="情绪周期切换要结合成交额。",
        source_type=ClaimSourceType.ARTICLE,
        source_ids=["a1"],
        article_id="a1",
        source_author="等主人的猫",
        method_tags=["情绪周期", "成交额"],
        mentioned_tickers=["300750"],
        mentioned_sectors=["机器人"],
        mentioned_concepts=["情绪周期"],
        confidence_level="candidate",
        evidence_text="情绪周期切换要结合成交额。",
    )

    assert claim.review_status == "unreviewed"
    assert claim.evidence_level == "text_raw"
    assert claim.method_tags == ["情绪周期", "成交额"]
