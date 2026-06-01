from tgb_pipeline.filters.interaction_filter import filter_comments_for_corpus
from tgb_pipeline.models import AuthorRole, Comment


def make_comment(
    comment_id: str,
    author_name: str,
    author_role: AuthorRole,
    text: str,
    page_position: int,
) -> Comment:
    return Comment(
        comment_id=comment_id,
        article_id="article-1",
        author_name=author_name,
        author_role=author_role,
        raw_content=text,
        content_text=text,
        page_num=1,
        page_position=page_position,
    )


def test_filter_comments_for_corpus_builds_interactions_and_low_value_flags() -> None:
    comments = [
        make_comment("c1", "普通成员甲", AuthorRole.MEMBER, "谢谢", 1),
        make_comment("c2", "普通成员乙", AuthorRole.MEMBER, "等主人的猫，这里怎么看？", 2),
        make_comment("c3", "等主人的猫", AuthorRole.TARGET, "看市场合力。", 3),
        make_comment("c4", "Aoch", AuthorRole.AOCH, "Aoch 专项讨论。", 4),
        make_comment("c5", "普通成员丙", AuthorRole.MEMBER, "这个问题还有后续吗？", 5),
        make_comment("c6", "等主人的猫", AuthorRole.TARGET, "后续看量能。", 6),
    ]

    kept_comments, interactions = filter_comments_for_corpus(
        comments,
        target_author="等主人的猫",
        focus_member_aliases=["Aoch"],
    )

    kept_ids = [comment.comment_id for comment in kept_comments]
    assert "c1" not in kept_ids
    assert "c2" in kept_ids
    assert "c3" in kept_ids
    assert "c4" not in kept_ids
    assert "c5" in kept_ids
    assert "c6" in kept_ids
    assert any(comment.keep_reason == "target_author_comment" for comment in kept_comments)
    assert any(comment.keep_reason == "mentions_target_author" for comment in kept_comments)
    assert any(comment.keep_reason == "question_answer_window" for comment in kept_comments)
    assert interactions
    assert interactions[0].keep_reason == "target_author_interaction_window"
    assert "普通成员乙" in interactions[0].member_names

