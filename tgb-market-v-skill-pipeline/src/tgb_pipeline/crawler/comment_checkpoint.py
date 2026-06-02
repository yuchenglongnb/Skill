"""Checkpoint helpers for resumable comment crawling."""

from __future__ import annotations

import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from bs4 import BeautifulSoup

from tgb_pipeline.crawler.parse_comments import (
    find_comment_last_page_num,
    find_comment_next_page_url,
)
from tgb_pipeline.models import (
    ArticleIndex,
    Comment,
    CommentArticleState,
    CommentPageState,
    ImageAsset,
)
from tgb_pipeline.storage import JSONLStore

SNAPSHOT_PATTERN = re.compile(r"^(?P<article_id>.+)_comments_page_(?P<page_num>\d+)\.html$")


def comment_page_state_id(article_id: str, page_num: int) -> str:
    return f"comment-page-{article_id}-{page_num}"


def load_fetched_comment_pages(
    raw_dir: Path,
    *,
    include_snapshots: bool = True,
) -> dict[str, set[int]]:
    pages: dict[str, set[int]] = {}
    state_path = raw_dir / "comment_page_states.jsonl"
    if state_path.exists():
        states = JSONLStore(state_path, CommentPageState, "state_id").read_all()
        for state in states:
            if state.status in {"fetched", "empty", "max_limit_reached"}:
                pages.setdefault(state.article_id, set()).add(state.page_num)
    if include_snapshots:
        for snapshot in (raw_dir / "html").glob("*_comments_page_*.html"):
            match = SNAPSHOT_PATTERN.match(snapshot.name)
            if match:
                pages.setdefault(match.group("article_id"), set()).add(
                    int(match.group("page_num"))
                )
    return pages


def load_comment_article_states(raw_dir: Path) -> dict[str, CommentArticleState]:
    path = raw_dir / "comment_article_states.jsonl"
    if not path.exists():
        return {}
    return {
        state.article_id: state
        for state in JSONLStore(path, CommentArticleState, "article_id").read_all()
    }


def bootstrap_comment_page_states_from_snapshots(raw_dir: Path) -> int:
    html_dir = raw_dir / "html"
    state_store = JSONLStore(
        raw_dir / "comment_page_states.jsonl",
        CommentPageState,
        "state_id",
    )
    existing_ids = {state.state_id for state in state_store.read_all()}
    migrated: list[CommentPageState] = []
    for snapshot in html_dir.glob("*_comments_page_*.html"):
        match = SNAPSHOT_PATTERN.match(snapshot.name)
        if not match:
            continue
        article_id = match.group("article_id")
        page_num = int(match.group("page_num"))
        state_id = comment_page_state_id(article_id, page_num)
        if state_id in existing_ids:
            continue
        html = snapshot.read_text(encoding="utf-8")
        page_url = _snapshot_page_url(article_id, page_num)
        soup = BeautifulSoup(html, "lxml")
        comments_count = len(soup.select(".plContent .plItem"))
        next_page_url = find_comment_next_page_url(html, page_url)
        migrated.append(
            CommentPageState(
                state_id=state_id,
                article_id=article_id,
                page_num=page_num,
                page_url=page_url,
                status="empty" if not comments_count else "fetched",
                comments_count=comments_count,
                discovered_last_page=find_comment_last_page_num(html, page_url),
                has_next_page=bool(next_page_url),
                raw={
                    "snapshot_path": snapshot.as_posix(),
                    "migrated_from_snapshot": True,
                    "next_page_url": next_page_url,
                },
            )
        )
    return state_store.append_many(migrated)


def reconcile_comment_article_states(
    raw_dir: Path,
    *,
    max_pages_limit: int = 100,
) -> int:
    article_index_path = raw_dir / "articles_index.jsonl"
    if not article_index_path.exists():
        return 0
    articles = JSONLStore(article_index_path, ArticleIndex, "article_id").read_all()
    page_states = _group_page_states(raw_dir)
    comments_by_article = count_records_by_article(
        _read_optional(raw_dir / "comments_all.jsonl", Comment, "comment_id")
    )
    images_by_article = count_records_by_article(
        _read_optional(raw_dir / "images.jsonl", ImageAsset, "image_id")
    )
    states = [
        build_comment_article_state(
            article,
            page_states.get(article.article_id, []),
            comments_by_article.get(article.article_id, 0),
            images_by_article.get(article.article_id, 0),
            max_pages_limit,
        )
        for article in articles
    ]
    return JSONLStore(
        raw_dir / "comment_article_states.jsonl",
        CommentArticleState,
        "article_id",
    ).rewrite_all(states)


def compute_next_comment_page(
    article: ArticleIndex,
    fetched_pages: set[int],
    existing_state: CommentArticleState | None,
) -> int:
    if existing_state and existing_state.completed:
        return existing_state.next_page_to_fetch
    if existing_state and existing_state.next_page_to_fetch > 1:
        return existing_state.next_page_to_fetch
    if fetched_pages:
        return max(fetched_pages) + 1
    return 1


def build_comment_article_state(
    article: ArticleIndex,
    page_states: list[CommentPageState],
    comments_count: int,
    images_count: int,
    max_pages_limit: int,
) -> CommentArticleState:
    successful_states = [
        state
        for state in page_states
        if state.status in {"fetched", "empty", "max_limit_reached"}
    ]
    fetched_pages = {state.page_num for state in successful_states}
    max_fetched_page = max(fetched_pages, default=0)
    discovered_values = [
        state.discovered_last_page
        for state in page_states
        if state.discovered_last_page is not None
    ]
    discovered_last_page = max(discovered_values, default=None)
    latest = max(page_states, key=lambda state: state.page_num, default=None)
    completed = bool(
        latest
        and (
            latest.status == "empty"
            or latest.has_next_page is False
            or (
                discovered_last_page is not None
                and max_fetched_page >= discovered_last_page
            )
        )
    )
    max_limit_reached = bool(
        not completed
        and max_fetched_page >= max_pages_limit
        and (
            discovered_last_page is None
            or discovered_last_page > max_fetched_page
        )
    )
    return CommentArticleState(
        article_id=article.article_id,
        title=article.title,
        indexed_reply_count=article.reply_count,
        discovered_last_page=discovered_last_page,
        fetched_pages=len(fetched_pages),
        max_fetched_page=max_fetched_page,
        next_page_to_fetch=max_fetched_page + 1 if not completed else max_fetched_page,
        completed=completed,
        max_limit_reached=max_limit_reached,
        comments_count=comments_count,
        images_count=images_count,
        updated_at=datetime.now(UTC),
        raw={
            "failed_pages": [
                state.page_num for state in page_states if state.status == "failed"
            ],
        },
    )


def count_records_by_article(records) -> Counter[str]:
    return Counter(record.article_id for record in records if record.article_id)


def _group_page_states(raw_dir: Path) -> dict[str, list[CommentPageState]]:
    grouped: dict[str, list[CommentPageState]] = {}
    states = _read_optional(
        raw_dir / "comment_page_states.jsonl",
        CommentPageState,
        "state_id",
    )
    for state in states:
        grouped.setdefault(state.article_id, []).append(state)
    return grouped


def _snapshot_page_url(article_id: str, page_num: int) -> str:
    if page_num == 1:
        return f"https://m.tgb.cn/a/{article_id}"
    return f"https://m.tgb.cn/a/{article_id}-{page_num}?type="


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()
