from datetime import UTC, datetime

from tgb_pipeline.extraction.claim_extract import extract_claims_from_corpus
from tgb_pipeline.models import AuthorRole, Comment, Interaction, InteractionType
from tgb_pipeline.models import Article, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def test_interaction_claims_only_use_target_author_text(tmp_path) -> None:
    raw_dir = tmp_path / "data" / "raw" / "tgb"
    processed_dir = tmp_path / "data" / "processed" / "tgb"

    JSONLStore(raw_dir / "articles.jsonl", Article, "article_id").append(
        Article(
            article_id="a1",
            title="情绪周期思考",
            author_name="等主人的猫",
            published_at=datetime(2023, 1, 15, tzinfo=UTC),
            url="https://example.test/a1",
            raw_content="正文",
            content_text="正文",
        )
    )
    member = Comment(
        comment_id="member-1",
        article_id="a1",
        author_name="普通成员",
        author_role=AuthorRole.MEMBER,
        published_at=datetime(2023, 1, 16, 9, 0, tzinfo=UTC),
        raw_content="老师怎么看量化？",
        content_text="老师怎么看量化？",
    )
    target = Comment(
        comment_id="target-1",
        article_id="a1",
        author_name="等主人的猫",
        author_role=AuthorRole.TARGET,
        published_at=datetime(2023, 1, 16, 9, 1, tzinfo=UTC),
        raw_content="量化会影响市场结构，所以短线要看成交额。",
        content_text="量化会影响市场结构，所以短线要看成交额。",
    )
    interaction = Interaction(
        interaction_id="i1",
        article_id="a1",
        interaction_type=InteractionType.REPLY,
        actor_name="普通成员",
        comment_ids=["member-1", "target-1"],
        raw_content="普通成员: 老师怎么看量化？\n等主人的猫: 量化会影响市场结构，所以短线要看成交额。",
    )

    JSONLStore(raw_dir / "comments.jsonl", Comment, "comment_id").append(target)
    JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").append_many([member, target])
    JSONLStore(raw_dir / "interactions.jsonl", Interaction, "interaction_id").append(interaction)

    claims = extract_claims_from_corpus(raw_dir, processed_dir)
    interaction_claims = [claim for claim in claims if claim.source_type.value == "interaction"]

    assert interaction_claims
    assert all("老师怎么看量化" not in claim.claim_text for claim in interaction_claims)
    assert any("量化会影响市场结构" in claim.claim_text for claim in interaction_claims)
    assert any(
        "普通成员: 老师怎么看量化？" in "\n".join(claim.raw["source_segment"].get("interaction_context", []))
        for claim in interaction_claims
    )

