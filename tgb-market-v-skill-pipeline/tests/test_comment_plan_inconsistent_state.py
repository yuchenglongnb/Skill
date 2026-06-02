from datetime import date
from pathlib import Path

from tgb_pipeline.completion.comment_plan import build_comment_completion_plan
from tgb_pipeline.config import load_crawl_config
from tgb_pipeline.models import ArticleIndex, CommentArticleState
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
  max_total_pages_per_run: 300
  priority_article_ids: [a1]
  skip_completed: true
  skip_active_errors: false
""",
        encoding="utf-8",
    )
    return load_crawl_config(path)


def test_plan_keeps_article_with_inconsistent_completed_state(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw" / "tgb"
    JSONLStore(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id").append(
        ArticleIndex(
            article_id="a1",
            title="A1",
            published_date=date(2023, 1, 15),
            url="https://www.tgb.cn/a/a1",
            mobile_url="https://m.tgb.cn/a/a1",
        )
    )
    JSONLStore(raw_dir / "comment_article_states.jsonl", CommentArticleState, "article_id").append(
        CommentArticleState(
            article_id="a1",
            title="A1",
            discovered_last_page=749,
            max_fetched_page=500,
            next_page_to_fetch=500,
            completed=True,
        )
    )

    plan = build_comment_completion_plan(raw_dir, _crawl_config(tmp_path))

    assert len(plan.items) == 1
    assert plan.items[0].next_page_to_fetch == 501
    assert "inconsistent_completed_state" in (plan.items[0].reason or "")
