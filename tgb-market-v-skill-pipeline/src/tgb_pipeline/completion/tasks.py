"""Tasks for comment-completion planning and explicit execution."""

from __future__ import annotations

import json
from pathlib import Path

from tgb_pipeline.completion.comment_plan import build_comment_completion_plan
from tgb_pipeline.completion.report import build_comment_completion_plan_report
from tgb_pipeline.config import CrawlConfig, TargetConfig
from tgb_pipeline.crawler.comment_tasks import crawl_comments
from tgb_pipeline.models import CommentCompletionPlan


def generate_comment_completion_plan_bundle(
    crawl_config: CrawlConfig,
    *,
    article_id: str | None = None,
    pages_per_article: int | None = None,
    max_total_pages: int | None = None,
) -> list[Path]:
    raw_dir = crawl_config.storage.raw_dir / "tgb"
    interim_dir = crawl_config.storage.interim_dir / "tgb"
    plan = build_comment_completion_plan(
        raw_dir,
        crawl_config,
        article_id=article_id,
        pages_per_article=pages_per_article,
        max_total_pages=max_total_pages,
    )
    plan_path = interim_dir / "comment_completion_plan.json"
    _write_plan(plan_path, plan)
    report_path = build_comment_completion_plan_report(plan, Path("reports"))
    return [plan_path, report_path]


def execute_comment_completion_plan(
    target_config: TargetConfig,
    crawl_config: CrawlConfig,
    *,
    plan_path: Path,
) -> tuple[int, int, int]:
    plan = _read_plan(plan_path)
    total_comments = 0
    total_images = 0
    total_pages = 0
    for item in plan.items:
        result = crawl_comments(
            target_config,
            crawl_config,
            article_id=item.article_id,
            start_page=item.next_page_to_fetch,
            max_pages=item.target_max_page,
        )
        total_comments += result.appended_comments
        total_images += result.appended_images
        total_pages += result.fetched_pages
    return total_comments, total_images, total_pages


def _write_plan(path: Path, plan: CommentCompletionPlan) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        plan.model_dump(mode="json")
        if hasattr(plan, "model_dump")
        else json.loads(plan.json())
    )
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _read_plan(path: Path) -> CommentCompletionPlan:
    text = path.read_text(encoding="utf-8")
    if hasattr(CommentCompletionPlan, "model_validate_json"):
        return CommentCompletionPlan.model_validate_json(text)
    return CommentCompletionPlan.parse_raw(text)
