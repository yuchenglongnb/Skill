from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from tgb_pipeline.models import (
    Article,
    ArticleIndex,
    AuthorRole,
    Comment,
    ImageAsset,
    Interaction,
    InteractionType,
)
from tgb_pipeline.storage import JSONLStore


def build_sample_corpus(base_dir: Path, *, include_aoch: bool = False) -> tuple[Path, Path, Path]:
    raw_dir = base_dir / "data" / "raw" / "tgb"
    processed_dir = base_dir / "data" / "processed" / "tgb"
    reports_dir = base_dir / "reports"
    html_dir = raw_dir / "html"
    html_dir.mkdir(parents=True, exist_ok=True)
    (html_dir / "a1_comments_page_1.html").write_text("<html>page 1</html>", encoding="utf-8")
    (html_dir / "a1_comments_page_2.html").write_text("<html>page 2</html>", encoding="utf-8")

    article_index = ArticleIndex(
        article_id="a1",
        title="情绪周期是否可靠的思考",
        published_date=date(2023, 1, 15),
        reply_count=10,
        url="https://www.tgb.cn/a/1Vgsye6eK36",
        mobile_url="https://m.tgb.cn/a/1Vgsye6eK36",
    )
    article = Article(
        article_id="a1",
        title="情绪周期是否可靠的思考",
        author_name="等主人的猫",
        published_at=datetime(2023, 1, 15, 14, 18, tzinfo=UTC),
        url="https://www.tgb.cn/a/1Vgsye6eK36",
        mobile_url="https://m.tgb.cn/a/1Vgsye6eK36",
        raw_content="主帖正文 [IMAGE: image-article-1]",
        content_text="主帖正文 [IMAGE: image-article-1]",
        image_asset_ids=["image-article-1"],
    )
    comments_all = [
        Comment(
            comment_id="comment-target-1",
            article_id="a1",
            author_name="等主人的猫",
            author_role=AuthorRole.TARGET,
            published_at=datetime(2023, 1, 16, 9, 0, tzinfo=UTC),
            page_num=1,
            page_position=1,
            keep_reason="target_author_comment",
            raw_content="目标作者评论",
            content_text="目标作者评论",
            raw={"filter_reason": "target_author_comment"},
        ),
        Comment(
            comment_id="comment-member-1",
            article_id="a1",
            author_name="普通成员乙",
            author_role=AuthorRole.MEMBER,
            published_at=datetime(2023, 1, 16, 9, 1, tzinfo=UTC),
            page_num=1,
            page_position=2,
            target_author_interacted=True,
            keep_reason="mentions_target_author",
            raw_content="等主人的猫，这里怎么看？ [IMAGE: image-comment-1]",
            content_text="等主人的猫，这里怎么看？ [IMAGE: image-comment-1]",
            image_asset_ids=["image-comment-1"],
            raw={"filter_reason": "mentions_target_author"},
        ),
        Comment(
            comment_id="comment-member-2",
            article_id="a1",
            author_name="普通成员甲",
            author_role=AuthorRole.MEMBER,
            published_at=datetime(2023, 1, 16, 9, 2, tzinfo=UTC),
            page_num=2,
            page_position=1,
            raw_content="谢谢",
            content_text="谢谢",
            raw={"filter_reason": "low_value", "low_value": True},
        ),
    ]
    if include_aoch:
        comments_all.append(
            Comment(
                comment_id="comment-aoch-1",
                article_id="a1",
                author_name="Aoch",
                author_role=AuthorRole.AOCH,
                published_at=datetime(2023, 1, 16, 9, 3, tzinfo=UTC),
                page_num=2,
                page_position=2,
                keep_reason="aoch_focus_member",
                raw_content="Aoch 专项观点",
                content_text="Aoch 专项观点",
                raw={"filter_reason": "aoch_focus_member"},
            )
        )

    comments_kept = [comment for comment in comments_all if comment.keep_reason in {"target_author_comment", "mentions_target_author"}]
    aoch_comments = [comment for comment in comments_all if comment.author_role == AuthorRole.AOCH]
    interactions = [
        Interaction(
            interaction_id="interaction-1",
            article_id="a1",
            interaction_type=InteractionType.REPLY,
            actor_name="普通成员乙",
            target_name="等主人的猫",
            comment_id="comment-member-1",
            related_comment_id="comment-target-1",
            member_names=["普通成员乙", "等主人的猫"],
            comment_ids=["comment-member-1", "comment-target-1"],
            keep_reason="target_author_interaction_window",
            occurred_at=datetime(2023, 1, 16, 9, 1, tzinfo=UTC),
            raw_content="普通成员乙: 等主人的猫，这里怎么看？\n等主人的猫: 目标作者评论",
        )
    ]
    images = [
        ImageAsset(
            image_id="image-article-1",
            article_id="a1",
            source_url="https://image.tgb.cn/article.png",
            page_url="https://m.tgb.cn/a/1Vgsye6eK36",
            source_type="article_body",
            position_index=1,
            before_text="主帖正文",
            after_text="后文",
            keep_reason="target_author_article_image",
            image_type="contentImage",
        ),
        ImageAsset(
            image_id="image-comment-1",
            article_id="a1",
            comment_id="comment-member-1",
            source_url="https://image.tgb.cn/comment.png",
            page_url="https://m.tgb.cn/a/1Vgsye6eK36",
            source_type="comment",
            position_index=1,
            before_text="这里怎么看",
            after_text="请看图",
            image_type="contentImage",
            raw={"page_num": 1},
        ),
        ImageAsset(
            image_id="image-review-1",
            article_id="a1",
            comment_id="comment-member-2",
            source_url="https://image.tgb.cn/avatar_icon.png",
            page_url="https://m.tgb.cn/a/1Vgsye6eK36",
            source_type="comment",
            position_index=1,
            raw={"page_num": 2},
        ),
    ]

    JSONLStore(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id").append(article_index)
    JSONLStore(raw_dir / "articles.jsonl", Article, "article_id").append(article)
    JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").append_many(comments_all)
    JSONLStore(raw_dir / "comments.jsonl", Comment, "comment_id").append_many(comments_kept)
    JSONLStore(raw_dir / "interactions.jsonl", Interaction, "interaction_id").append_many(interactions)
    JSONLStore(raw_dir / "images.jsonl", ImageAsset, "image_id").append_many(images)
    if include_aoch:
        JSONLStore(raw_dir / "aoch_discussions.jsonl", Comment, "comment_id").append_many(aoch_comments)
    return raw_dir, processed_dir, reports_dir

