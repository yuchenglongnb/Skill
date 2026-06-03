from datetime import UTC, datetime

from tgb_pipeline.extraction.claim_extract import (
    extract_claims_from_corpus,
    extract_claims_from_segments,
)
from tgb_pipeline.models import (
    Article,
    AuthorRole,
    Comment,
    ImageAsset,
    ImageOCR,
    Interaction,
    InteractionType,
    MethodologyClaim,
)
from tgb_pipeline.storage import JSONLStore


def test_extract_claims_from_segments_is_stable_and_deduped() -> None:
    segments = [
        {
            "source_type": "article",
            "source_id": "a1",
            "article_id": "a1",
            "author_name": "等主人的猫",
            "text": "情绪周期切换要结合成交额看市场结构。",
            "source_time": datetime(2023, 1, 15, tzinfo=UTC),
            "source_title": "情绪周期思考",
            "evidence_level": "article_text",
        },
        {
            "source_type": "article",
            "source_id": "a1",
            "article_id": "a1",
            "author_name": "等主人的猫",
            "text": "情绪周期切换要结合成交额看市场结构。",
            "source_time": datetime(2023, 1, 15, tzinfo=UTC),
            "source_title": "情绪周期思考",
            "evidence_level": "article_text",
        },
    ]

    claims = extract_claims_from_segments(segments)

    assert len(claims) == 1
    assert claims[0].claim_id.startswith("claim-")
    assert claims[0].method_tags[:2] == ["情绪周期", "成交额"]
    assert claims[0].raw["quality"]["reason"] == "strong_methodology_statement"


def test_extract_claims_skips_noise_and_keeps_strong_methodology() -> None:
    segments = [
        {
            "source_type": "article",
            "source_id": "a1",
            "article_id": "a1",
            "author_name": "等主人的猫",
            "text": "[IMAGE: image-1234567890abcdef]",
            "source_time": datetime(2023, 1, 15, tzinfo=UTC),
            "source_title": "情绪周期思考",
            "evidence_level": "article_text",
        },
        {
            "source_type": "article",
            "source_id": "a2",
            "article_id": "a2",
            "author_name": "等主人的猫",
            "text": "春夏秋冬本来就是自然规律。",
            "source_time": datetime(2023, 1, 15, tzinfo=UTC),
            "source_title": "情绪周期思考",
            "evidence_level": "article_text",
        },
        {
            "source_type": "comment",
            "source_id": "c1",
            "article_id": "a2",
            "author_name": "等主人的猫",
            "text": "今天太难了，服了。",
            "source_time": datetime(2023, 1, 16, tzinfo=UTC),
            "source_title": "机械纪元",
            "evidence_level": "target_comment_text",
        },
        {
            "source_type": "comment",
            "source_id": "c2",
            "article_id": "a2",
            "author_name": "等主人的猫",
            "text": "明天怎么看？",
            "source_time": datetime(2023, 1, 16, tzinfo=UTC),
            "source_title": "机械纪元",
            "evidence_level": "target_comment_text",
        },
        {
            "source_type": "comment",
            "source_id": "c3",
            "article_id": "a2",
            "author_name": "等主人的猫",
            "text": "市场就是这样。",
            "source_time": datetime(2023, 1, 16, tzinfo=UTC),
            "source_title": "机械纪元",
            "evidence_level": "target_comment_text",
        },
        {
            "source_type": "comment",
            "source_id": "c4",
            "article_id": "a2",
            "author_name": "等主人的猫",
            "text": "情绪周期不是失效，而是成交额和量化改变了反馈速度。",
            "source_time": datetime(2023, 1, 16, tzinfo=UTC),
            "source_title": "机械纪元",
            "evidence_level": "target_comment_text",
        },
    ]

    claims = extract_claims_from_segments(segments)

    assert len(claims) == 1
    assert claims[0].claim_text == "情绪周期不是失效，而是成交额和量化改变了反馈速度。"
    assert claims[0].raw["quality"]["reason"] == "strong_methodology_statement"
    assert "[IMAGE:" not in claims[0].raw_excerpt


def test_extract_claims_from_corpus_respects_source_boundaries(tmp_path) -> None:
    raw_dir = tmp_path / "data" / "raw" / "tgb"
    processed_dir = tmp_path / "data" / "processed" / "tgb"

    article = Article(
        article_id="a1",
        title="情绪周期思考",
        author_name="等主人的猫",
        published_at=datetime(2023, 1, 15, tzinfo=UTC),
        url="https://example.test/a1",
        raw_content="情绪周期切换时，要结合成交额看市场结构。",
        content_text="情绪周期切换时，要结合成交额看市场结构。",
    )
    target_comment = Comment(
        comment_id="c-target",
        article_id="a1",
        author_name="等主人的猫",
        author_role=AuthorRole.TARGET,
        published_at=datetime(2023, 1, 16, tzinfo=UTC),
        keep_reason="target_author_comment",
        raw_content="量化会强化市场结构，所以仓位要控制。",
        content_text="量化会强化市场结构，所以仓位要控制。",
    )
    member_comment = Comment(
        comment_id="c-member",
        article_id="a1",
        author_name="普通成员",
        author_role=AuthorRole.MEMBER,
        published_at=datetime(2023, 1, 16, tzinfo=UTC),
        keep_reason="mentions_target_author",
        target_author_interacted=True,
        raw_content="我觉得今天很强。",
        content_text="我觉得今天很强。",
    )
    aoch_comment = Comment(
        comment_id="c-aoch",
        article_id="a1",
        author_name="Aoch",
        author_role=AuthorRole.AOCH,
        published_at=datetime(2023, 1, 16, tzinfo=UTC),
        keep_reason="aoch_focus_member",
        raw_content="Aoch 观点不应该进入主 claim。",
        content_text="Aoch 观点不应该进入主 claim。",
    )
    interaction = Interaction(
        interaction_id="i1",
        article_id="a1",
        interaction_type=InteractionType.REPLY,
        actor_name="普通成员",
        comment_ids=["c-member", "c-target"],
        raw_content="普通成员 我觉得今天很强。\n等主人的猫 成交额回到万亿上方才有短线基础行情。",
    )
    image = ImageAsset(
        image_id="img-1",
        article_id="a1",
        source_url="https://example.test/image.png",
        page_url="https://example.test/a1",
        source_type="article_body",
    )
    ocr = ImageOCR(
        ocr_id="ocr-img-1-rapidocr",
        image_id="img-1",
        engine="rapidocr",
        raw_text="机器人方向有持续性",
        normalized_text="机器人方向有持续性",
        raw={"need_manual_review": True},
    )

    JSONLStore(raw_dir / "articles.jsonl", Article, "article_id").append(article)
    JSONLStore(raw_dir / "comments.jsonl", Comment, "comment_id").append_many(
        [target_comment, member_comment, aoch_comment]
    )
    JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").append_many(
        [target_comment, member_comment, aoch_comment]
    )
    JSONLStore(raw_dir / "interactions.jsonl", Interaction, "interaction_id").append(interaction)
    JSONLStore(raw_dir / "images.jsonl", ImageAsset, "image_id").append(image)
    JSONLStore(processed_dir / "image_ocr.jsonl", ImageOCR, "ocr_id").append(ocr)

    claims = extract_claims_from_corpus(raw_dir, processed_dir)
    stored = JSONLStore(
        processed_dir / "methodology_claims.jsonl",
        MethodologyClaim,
        "claim_id",
    ).read_all()

    assert claims
    assert stored
    assert any("情绪周期" in claim.method_tags for claim in claims)
    assert any(
        "量化影响" in claim.method_tags or "市场结构" in claim.method_tags
        for claim in claims
    )
    assert all("Aoch" not in (claim.source_author or "") for claim in claims)
    assert all(
        "普通成员" not in (claim.source_author or "")
        for claim in claims
        if claim.source_type.value != "interaction"
    )
    assert any(claim.evidence_level == "image_ocr_unreviewed" for claim in claims)
    assert all("[IMAGE:" not in claim.raw_excerpt for claim in claims)
    assert all("quality" in claim.raw for claim in claims)
