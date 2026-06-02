from datetime import date
from pathlib import Path

from tgb_pipeline.crawler.comment_checkpoint import (
    bootstrap_comment_page_states_from_snapshots,
    build_comment_article_state,
    comment_page_state_id,
    compute_next_comment_page,
    load_fetched_comment_pages,
)
from tgb_pipeline.models import ArticleIndex, CommentPageState


def _article() -> ArticleIndex:
    return ArticleIndex(
        article_id="a1",
        title="Article",
        published_date=date(2023, 1, 15),
        url="https://www.tgb.cn/a/a1",
        mobile_url="https://m.tgb.cn/a/a1",
    )


def test_comment_checkpoint_resumes_after_max_fetched_page(tmp_path: Path) -> None:
    assert comment_page_state_id("a1", 2) == "comment-page-a1-2"
    assert compute_next_comment_page(_article(), {1, 2}, None) == 3


def test_bootstrap_comment_page_states_from_snapshots(tmp_path: Path) -> None:
    html_dir = tmp_path / "html"
    html_dir.mkdir()
    (html_dir / "a1_comments_page_1.html").write_text("<html></html>", encoding="utf-8")

    assert bootstrap_comment_page_states_from_snapshots(tmp_path) == 1
    assert bootstrap_comment_page_states_from_snapshots(tmp_path) == 0
    assert load_fetched_comment_pages(tmp_path) == {"a1": {1}}


def test_comment_article_state_marks_limit_and_completion() -> None:
    article = _article()
    limit_state = build_comment_article_state(
        article,
        [
            CommentPageState(
                state_id="comment-page-a1-100",
                article_id="a1",
                page_num=100,
                page_url="https://m.tgb.cn/a/a1-100?type=",
                discovered_last_page=749,
                has_next_page=True,
            )
        ],
        comments_count=1000,
        images_count=10,
        max_pages_limit=100,
    )
    assert limit_state.max_limit_reached is True
    assert limit_state.completed is False
    assert limit_state.next_page_to_fetch == 101

    complete_state = build_comment_article_state(
        article,
        [
            CommentPageState(
                state_id="comment-page-a1-2",
                article_id="a1",
                page_num=2,
                page_url="https://m.tgb.cn/a/a1-2?type=",
                discovered_last_page=2,
                has_next_page=False,
            )
        ],
        comments_count=20,
        images_count=1,
        max_pages_limit=100,
    )
    assert complete_state.completed is True
