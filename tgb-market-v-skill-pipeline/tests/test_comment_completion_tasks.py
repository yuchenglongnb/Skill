from datetime import UTC, datetime
from pathlib import Path

from tgb_pipeline.completion import tasks
from tgb_pipeline.config import load_crawl_config, load_target_config
from tgb_pipeline.crawler.comment_tasks import CrawlCommentsResult
from tgb_pipeline.models import CommentCompletionPlan, CommentCompletionPlanItem


def _configs(tmp_path: Path):
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: Target
  start_article:
    title: Article
    published_date: "2023-01-15"
""",
        encoding="utf-8",
    )
    crawl_path = tmp_path / "crawl.yaml"
    crawl_path.write_text(
        f"""
crawl:
  user_agent: fixture
  request_interval_seconds: 0
  request_timeout_seconds: 10
storage:
  raw_dir: {tmp_path.as_posix()}/raw
  interim_dir: {tmp_path.as_posix()}/interim
  processed_dir: {tmp_path.as_posix()}/processed
""",
        encoding="utf-8",
    )
    return load_target_config(target_path), load_crawl_config(crawl_path)


def test_execute_completion_plan_calls_crawl_comments_with_item_bounds(tmp_path, monkeypatch) -> None:
    target, crawl = _configs(tmp_path)
    plan = CommentCompletionPlan(
        plan_id="plan-1",
        generated_at=datetime.now(UTC),
        total_items=1,
        total_planned_pages=20,
        items=[
            CommentCompletionPlanItem(
                article_id="a1",
                next_page_to_fetch=101,
                target_max_page=120,
                planned_pages=20,
            )
        ],
    )
    plan_path = tmp_path / "plan.json"
    tasks._write_plan(plan_path, plan)
    calls = []

    def fake_crawl_comments(target_config, crawl_config, **kwargs):
        calls.append(kwargs)
        return CrawlCommentsResult(10, 2, 20, 0, 0, 0, 1)

    monkeypatch.setattr(tasks, "crawl_comments", fake_crawl_comments)

    assert tasks.execute_comment_completion_plan(target, crawl, plan_path=plan_path) == (10, 2, 20)
    assert calls == [{"article_id": "a1", "start_page": 101, "max_pages": 120}]
