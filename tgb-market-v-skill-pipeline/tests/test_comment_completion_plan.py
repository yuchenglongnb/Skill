from datetime import date
from pathlib import Path

from tgb_pipeline.completion.comment_plan import build_comment_completion_plan
from tgb_pipeline.config import load_crawl_config
from tgb_pipeline.models import ArticleIndex, CommentArticleState, CrawlError
from tgb_pipeline.storage import JSONLStore


def _crawl_config(tmp_path: Path):
    path = tmp_path / "crawl.yaml"
    path.write_text(
        f"""
crawl:
  user_agent: fixture
  request_interval_seconds: 0
  request_timeout_seconds: 10
storage:
  raw_dir: {tmp_path.as_posix()}/raw
  interim_dir: {tmp_path.as_posix()}/interim
  processed_dir: {tmp_path.as_posix()}/processed
comment_completion:
  default_pages_per_article: 100
  max_total_pages_per_run: 150
  priority_article_ids: [priority]
  skip_completed: true
  skip_active_errors: false
""",
        encoding="utf-8",
    )
    return load_crawl_config(path)


def _write_data(raw_dir: Path) -> None:
    articles = JSONLStore(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id")
    states = JSONLStore(raw_dir / "comment_article_states.jsonl", CommentArticleState, "article_id")
    for article_id in ["priority", "regular", "done"]:
        articles.append(
            ArticleIndex(
                article_id=article_id,
                title=article_id,
                published_date=date(2023, 1, 15),
                url=f"https://www.tgb.cn/a/{article_id}",
                mobile_url=f"https://m.tgb.cn/a/{article_id}",
            )
        )
    states.append_many(
        [
            CommentArticleState(
                article_id="priority",
                next_page_to_fetch=101,
                max_fetched_page=100,
                discovered_last_page=319,
                max_limit_reached=True,
            ),
            CommentArticleState(
                article_id="regular",
                next_page_to_fetch=32,
                max_fetched_page=31,
                discovered_last_page=298,
            ),
            CommentArticleState(
                article_id="done",
                next_page_to_fetch=14,
                max_fetched_page=14,
                discovered_last_page=14,
                completed=True,
            ),
        ]
    )


def test_completion_plan_prioritizes_and_applies_global_limit(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "tgb"
    _write_data(raw_dir)

    plan = build_comment_completion_plan(raw_dir, _crawl_config(tmp_path))

    assert [item.article_id for item in plan.items] == ["priority", "regular"]
    assert plan.items[0].target_max_page == 200
    assert plan.items[1].planned_pages == 50
    assert plan.total_planned_pages == 150


def test_completion_plan_can_target_article_and_skip_active_errors(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "tgb"
    _write_data(raw_dir)
    config = _crawl_config(tmp_path)
    config.comment_completion.skip_active_errors = True
    JSONLStore(raw_dir / "comment_crawl_errors.jsonl", CrawlError, "error_id").append(
        CrawlError(
            error_id="error-1",
            stage="crawl_comments.page",
            article_id="priority",
            error_type="ConnectionError",
            error_message="failed",
        )
    )

    plan = build_comment_completion_plan(raw_dir, config, article_id="priority")

    assert plan.items == []
