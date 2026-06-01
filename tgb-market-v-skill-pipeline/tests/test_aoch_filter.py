from tgb_pipeline.filters.aoch_filter import select_aoch_comments
from tgb_pipeline.models import AuthorRole, Comment


def test_select_aoch_comments_returns_only_aoch_records() -> None:
    comments = [
        Comment(
            comment_id="c1",
            article_id="article-1",
            author_name="Aoch",
            author_role=AuthorRole.AOCH,
            raw_content="Aoch 评论",
            image_asset_ids=["image-1"],
        ),
        Comment(
            comment_id="c2",
            article_id="article-1",
            author_name="等主人的猫",
            author_role=AuthorRole.TARGET,
            raw_content="目标作者评论",
        ),
    ]

    aoch_comments = select_aoch_comments(comments)

    assert len(aoch_comments) == 1
    assert aoch_comments[0].comment_id == "c1"
    assert aoch_comments[0].keep_reason == "aoch_focus_member"
    assert aoch_comments[0].raw["image_asset_ids"] == ["image-1"]
    assert aoch_comments[0].eligible_for_aoch_corpus is True
    assert aoch_comments[0].eligible_for_corpus is False

