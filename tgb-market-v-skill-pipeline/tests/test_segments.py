from datetime import UTC, datetime

from tgb_pipeline.extraction.segments import (
    segment_article,
    segment_comment,
    segment_interaction,
    segment_ocr,
)
from tgb_pipeline.models import Article, AuthorRole, Comment, ImageAsset, ImageOCR, Interaction, InteractionType


def test_segment_article_and_comment_preserve_meaningful_sentences() -> None:
    article = Article(
        article_id="a1",
        title="情绪周期思考",
        author_name="等主人的猫",
        published_at=datetime(2023, 1, 15, tzinfo=UTC),
        url="https://example.test/a1",
        raw_content="情绪周期切换时，要结合成交额看市场结构。谢谢",
        content_text="情绪周期切换时，要结合成交额看市场结构。谢谢",
    )
    comment = Comment(
        comment_id="c1",
        article_id="a1",
        author_name="等主人的猫",
        author_role=AuthorRole.TARGET,
        published_at=datetime(2023, 1, 16, tzinfo=UTC),
        raw_content="量化会放大波动；仓位要控制。",
        content_text="量化会放大波动；仓位要控制。",
    )

    article_segments = segment_article(article)
    comment_segments = segment_comment(comment)

    assert any("情绪周期" in segment["text"] for segment in article_segments)
    assert all(segment["source_type"] == "article" for segment in article_segments)
    assert any("量化" in segment["text"] for segment in comment_segments)
    assert all(segment["evidence_level"] == "target_comment_text" for segment in comment_segments)


def test_segment_interaction_and_ocr() -> None:
    target_comment = Comment(
        comment_id="c-target",
        article_id="a1",
        author_name="等主人的猫",
        author_role=AuthorRole.TARGET,
        published_at=datetime(2023, 1, 16, tzinfo=UTC),
        raw_content="我更看重成交额和情绪周期。",
        content_text="我更看重成交额和情绪周期。",
    )
    member_comment = Comment(
        comment_id="c-member",
        article_id="a1",
        author_name="普通成员",
        author_role=AuthorRole.MEMBER,
        published_at=datetime(2023, 1, 16, tzinfo=UTC),
        raw_content="收到",
        content_text="收到",
    )
    interaction = Interaction(
        interaction_id="i1",
        article_id="a1",
        interaction_type=InteractionType.REPLY,
        actor_name="普通成员",
        comment_ids=["c-member", "c-target"],
        raw_content="普通成员: 收到\n等主人的猫: 我更看重成交额和情绪周期。",
    )
    ocr = ImageOCR(
        ocr_id="ocr-1",
        image_id="img-1",
        engine="rapidocr",
        raw_text="机器人方向走强",
        normalized_text="机器人方向走强",
    )
    image = ImageAsset(
        image_id="img-1",
        article_id="a1",
        source_url="https://example.test/image.png",
        page_url="https://example.test/a1",
    )

    interaction_segments = segment_interaction(
        interaction,
        {target_comment.comment_id: target_comment, member_comment.comment_id: member_comment},
    )
    ocr_segments = segment_ocr(ocr, image)

    assert any("情绪周期" in segment["text"] for segment in interaction_segments)
    assert ocr_segments[0]["evidence_level"] == "image_ocr_unreviewed"

