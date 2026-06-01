from tgb_pipeline.config import TargetConfig
from tgb_pipeline.filters.author_filter import (
    annotate_comment_author_role,
    classify_author_role,
    normalize_author_name,
)
from tgb_pipeline.models import AuthorRole, Comment


def make_target_config() -> TargetConfig:
    return TargetConfig.parse_obj(
        {
            "target": {
                "platform": "taoguba",
                "author_name": "等主人的猫",
                "start_article": {
                    "title": "情绪周期是否可靠的思考",
                    "published_date": "2023-01-15",
                },
            },
            "priority_members": [{"name": "Aoch", "aliases": ["aoch", "A O C H"]}],
        }
    )


def test_author_classification_and_annotation() -> None:
    target_config = make_target_config()
    comment = Comment(
        comment_id="comment-1",
        article_id="article-1",
        author_name=" A O C H ",
        raw_content="原始评论",
    )

    assert normalize_author_name(" 等 主人的猫 ") == "等主人的猫"
    assert classify_author_role("等主人的猫", target_config) == AuthorRole.TARGET
    assert classify_author_role(" A O C H ", target_config) == AuthorRole.AOCH
    assert classify_author_role("普通成员", target_config) == AuthorRole.MEMBER
    assert annotate_comment_author_role(comment, target_config).author_role == AuthorRole.AOCH

