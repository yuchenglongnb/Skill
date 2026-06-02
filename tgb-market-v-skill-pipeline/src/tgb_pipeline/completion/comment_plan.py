"""Build bounded batches for comment-page backfill."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from tgb_pipeline.config import CrawlConfig
from tgb_pipeline.models import (
    ArticleIndex,
    CommentArticleState,
    CommentCompletionPlan,
    CommentCompletionPlanItem,
    CrawlError,
)
from tgb_pipeline.storage import JSONLStore


def build_comment_completion_plan(
    raw_dir: Path,
    crawl_config: CrawlConfig,
    *,
    article_id: str | None = None,
    pages_per_article: int | None = None,
    max_total_pages: int | None = None,
) -> CommentCompletionPlan:
    settings = crawl_config.comment_completion
    pages_per_item = pages_per_article or settings.default_pages_per_article
    total_page_limit = max_total_pages or settings.max_total_pages_per_run
    articles = _read_optional(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id")
    states = {
        state.article_id: state
        for state in _read_optional(
            raw_dir / "comment_article_states.jsonl",
            CommentArticleState,
            "article_id",
        )
    }
    active_error_ids = {
        error.article_id
        for error in _read_optional(
            raw_dir / "comment_crawl_errors.jsonl",
            CrawlError,
            "error_id",
        )
        if not error.resolved and error.article_id
    }
    priority_ids = {
        value: len(settings.priority_article_ids) - index
        for index, value in enumerate(settings.priority_article_ids)
    }
    candidates: list[CommentCompletionPlanItem] = []
    for article in articles:
        if article_id and article.article_id != article_id:
            continue
        state = states.get(article.article_id) or CommentArticleState(
            article_id=article.article_id,
            title=article.title,
        )
        inconsistent_completed_state = _has_inconsistent_completed_state(state)
        if settings.skip_completed and state.completed and not inconsistent_completed_state:
            continue
        if settings.skip_active_errors and article.article_id in active_error_ids:
            continue
        item = _build_plan_item(
            article,
            state,
            pages_per_item,
            priority=priority_ids.get(article.article_id, 0),
            has_active_error=article.article_id in active_error_ids,
            inconsistent_completed_state=inconsistent_completed_state,
        )
        if item is not None:
            candidates.append(item)

    candidates.sort(
        key=lambda item: (
            -item.priority,
            -(item.remaining_known_pages or 0),
            item.next_page_to_fetch,
            item.article_id,
        )
    )
    planned_items = _limit_total_pages(candidates, total_page_limit)
    generated_at = datetime.now(UTC)
    return CommentCompletionPlan(
        plan_id=f"comment-completion-{generated_at.strftime('%Y%m%dT%H%M%SZ')}",
        generated_at=generated_at,
        total_items=len(planned_items),
        total_planned_pages=sum(item.planned_pages for item in planned_items),
        items=planned_items,
        raw={
            "pages_per_article": pages_per_item,
            "max_total_pages": total_page_limit,
            "article_id": article_id,
        },
    )


def _build_plan_item(
    article: ArticleIndex,
    state: CommentArticleState,
    pages_per_article: int,
    *,
    priority: int,
    has_active_error: bool,
    inconsistent_completed_state: bool,
) -> CommentCompletionPlanItem | None:
    next_page = max(1, state.next_page_to_fetch)
    if inconsistent_completed_state:
        next_page = max(1, state.max_fetched_page + 1)
    last_page = state.discovered_last_page
    if last_page is not None and next_page > last_page:
        return None
    target_max_page = next_page + pages_per_article - 1
    if last_page is not None:
        target_max_page = min(target_max_page, last_page)
    planned_pages = target_max_page - next_page + 1
    if planned_pages <= 0:
        return None
    remaining_pages = last_page - next_page + 1 if last_page is not None else None
    reasons = []
    if priority:
        reasons.append("priority_article")
    if state.max_limit_reached:
        reasons.append("resume_after_limit")
    if has_active_error:
        reasons.append("active_error_retry")
    if inconsistent_completed_state:
        reasons.append("inconsistent_completed_state")
    return CommentCompletionPlanItem(
        article_id=article.article_id,
        title=article.title,
        next_page_to_fetch=next_page,
        target_max_page=target_max_page,
        discovered_last_page=last_page,
        remaining_known_pages=remaining_pages,
        planned_pages=planned_pages,
        priority=priority,
        reason=", ".join(reasons) or "incomplete_article",
        raw={
            "max_fetched_page": state.max_fetched_page,
            "max_limit_reached": state.max_limit_reached,
            "has_active_error": has_active_error,
            "state_warnings": state.raw.get("state_warnings", []),
        },
    )


def _limit_total_pages(
    items: list[CommentCompletionPlanItem],
    max_total_pages: int,
) -> list[CommentCompletionPlanItem]:
    limited: list[CommentCompletionPlanItem] = []
    remaining = max_total_pages
    for item in items:
        if remaining <= 0:
            break
        if item.planned_pages > remaining:
            item.target_max_page = item.next_page_to_fetch + remaining - 1
            item.planned_pages = remaining
        limited.append(item)
        remaining -= item.planned_pages
    return limited


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()


def _has_inconsistent_completed_state(state: CommentArticleState) -> bool:
    return bool(
        state.completed
        and state.discovered_last_page is not None
        and state.max_fetched_page < state.discovered_last_page
    )
