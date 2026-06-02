"""Comment crawling and filtering tasks."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from tgb_pipeline.config import CrawlConfig, TargetConfig
from tgb_pipeline.crawler.comment_checkpoint import (
    bootstrap_comment_page_states_from_snapshots,
    build_comment_article_state,
    comment_page_state_id,
    compute_next_comment_page,
    count_records_by_article,
    load_comment_article_states,
    load_fetched_comment_pages,
    reconcile_comment_article_states,
)
from tgb_pipeline.crawler.fetch import Fetcher
from tgb_pipeline.crawler.parse_comments import (
    build_comment_page_url,
    find_comment_last_page_num,
    find_comment_next_page_url,
    parse_comments_page,
)
from tgb_pipeline.filters.aoch_filter import select_aoch_comments
from tgb_pipeline.filters.author_filter import annotate_comment_author_role
from tgb_pipeline.filters.interaction_filter import filter_comments_for_corpus
from tgb_pipeline.models import (
    ArticleIndex,
    Comment,
    CommentArticleState,
    CommentPageState,
    CrawlError,
    ImageAsset,
    Interaction,
)
from tgb_pipeline.storage import JSONLStore


@dataclass(frozen=True)
class CrawlCommentsResult:
    appended_comments: int
    appended_images: int
    fetched_pages: int
    skipped_pages: int
    failed_pages: int
    completed_articles: int
    max_limit_articles: int

    def __iter__(self):
        """Keep the original two-value unpacking API working."""

        yield self.appended_comments
        yield self.appended_images


def crawl_comments(
    target_config: TargetConfig,
    crawl_config: CrawlConfig,
    *,
    fetcher: Fetcher | None = None,
    article_id: str | None = None,
    start_page: int | None = None,
    max_pages: int | None = None,
    force_comments: bool = False,
) -> CrawlCommentsResult:
    raw_root = crawl_config.storage.raw_dir / "tgb"
    html_root = raw_root / "html"
    index_store = JSONLStore(raw_root / "articles_index.jsonl", ArticleIndex, "article_id")
    comments_store = JSONLStore(raw_root / "comments_all.jsonl", Comment, "comment_id")
    images_store = JSONLStore(raw_root / "images.jsonl", ImageAsset, "image_id")
    error_store = JSONLStore(raw_root / "comment_crawl_errors.jsonl", CrawlError, "error_id")
    page_state_store = JSONLStore(
        raw_root / "comment_page_states.jsonl",
        CommentPageState,
        "state_id",
    )
    article_state_store = JSONLStore(
        raw_root / "comment_article_states.jsonl",
        CommentArticleState,
        "article_id",
    )
    client = fetcher or Fetcher(crawl_config.crawl)
    comment_count = 0
    image_count = 0
    fetched_page_count = 0
    skipped_page_count = 0
    failed_page_count = 0
    completed_article_count = 0
    max_limit_article_count = 0
    if crawl_config.crawl.resume_comment_pages_from_snapshots:
        bootstrap_comment_page_states_from_snapshots(raw_root)
        reconcile_comment_article_states(
            raw_root,
            max_pages_limit=max_pages or crawl_config.crawl.max_comment_pages_per_article,
        )
    fetched_pages_by_article = load_fetched_comment_pages(
        raw_root,
        include_snapshots=crawl_config.crawl.resume_comment_pages_from_snapshots,
    )
    article_states = load_comment_article_states(raw_root)
    page_states_by_article: dict[str, list[CommentPageState]] = {}
    for state in page_state_store.read_all():
        page_states_by_article.setdefault(state.article_id, []).append(state)

    for article in index_store.read_all():
        if article_id and article.article_id != article_id:
            continue
        existing_article_state = article_states.get(article.article_id)
        if existing_article_state and existing_article_state.completed and not force_comments:
            completed_article_count += 1
            continue
        page_limit = max_pages or crawl_config.crawl.max_comment_pages_per_article
        known_fetched_pages = fetched_pages_by_article.get(article.article_id, set())
        next_page_num = start_page or compute_next_comment_page(
            article,
            known_fetched_pages,
            existing_article_state,
        )
        article_page_states = page_states_by_article.setdefault(article.article_id, [])
        discovered_last_page = (
            existing_article_state.discovered_last_page
            if existing_article_state
            else None
        )
        while next_page_num <= page_limit and (
            discovered_last_page is None or next_page_num <= discovered_last_page
        ):
            if next_page_num in known_fetched_pages and not force_comments:
                skipped_page_count += 1
                next_page_num += 1
                continue
            page_url = build_comment_page_url(article.mobile_url, next_page_num)
            try:
                html = client.get_text(page_url)
                snapshot_path = html_root / f"{article.article_id}_comments_page_{next_page_num}.html"
                _save_snapshot(snapshot_path, html)
                page_comments, page_images = parse_comments_page(
                    html,
                    article_id=article.article_id,
                    article_title=article.title,
                    page_url=page_url,
                    page_num=next_page_num,
                    target_author=target_config.target.author_name,
                )
                comment_count += comments_store.append_many(page_comments)
                image_count += images_store.append_many(page_images)
                discovered_last_page = (
                    discovered_last_page
                    or find_comment_last_page_num(html, page_url)
                )
                next_page_url = find_comment_next_page_url(html, page_url)
                page_state = CommentPageState(
                    state_id=comment_page_state_id(article.article_id, next_page_num),
                    article_id=article.article_id,
                    page_num=next_page_num,
                    page_url=page_url,
                    status="empty" if not page_comments else "fetched",
                    comments_count=len(page_comments),
                    images_count=len(page_images),
                    discovered_last_page=discovered_last_page,
                    has_next_page=bool(next_page_url),
                    fetched_at=datetime.now(UTC),
                    raw={
                        "snapshot_path": snapshot_path.as_posix(),
                        "next_page_url": next_page_url,
                        "last_page_link": discovered_last_page,
                    },
                )
                page_state_store.upsert_many([page_state])
                article_page_states = _upsert_page_state(article_page_states, page_state)
                known_fetched_pages.add(next_page_num)
                fetched_page_count += 1
                if not next_page_url or not page_comments:
                    break
                next_page_num += 1
            except PermissionError:
                raise
            except Exception as exc:
                error_store.append(
                    _build_crawl_error(
                        stage="crawl_comments.page",
                        article_id=article.article_id,
                        url=page_url,
                        error=exc,
                        raw={"page_num": next_page_num, "mobile_url": article.mobile_url},
                    )
                )
                page_state = CommentPageState(
                    state_id=comment_page_state_id(article.article_id, next_page_num),
                    article_id=article.article_id,
                    page_num=next_page_num,
                    page_url=page_url,
                    status="failed",
                    fetched_at=datetime.now(UTC),
                    raw={"mobile_url": article.mobile_url},
                )
                page_state_store.upsert_many([page_state])
                article_page_states = _upsert_page_state(article_page_states, page_state)
                failed_page_count += 1
                break
        article_comments = comments_store.read_all()
        article_images = images_store.read_all()
        state = build_comment_article_state(
            article,
            article_page_states,
            count_records_by_article(article_comments).get(article.article_id, 0),
            count_records_by_article(article_images).get(article.article_id, 0),
            page_limit,
        )
        if known_fetched_pages and state.max_fetched_page < max(known_fetched_pages):
            state.max_fetched_page = max(known_fetched_pages)
            state.fetched_pages = len(known_fetched_pages)
            state.next_page_to_fetch = state.max_fetched_page + 1
            state.max_limit_reached = (
                not state.completed and state.max_fetched_page >= page_limit
            )
        article_state_store.upsert_many([state])
        article_states[article.article_id] = state
        completed_article_count += int(state.completed)
        max_limit_article_count += int(state.max_limit_reached)
    return CrawlCommentsResult(
        appended_comments=comment_count,
        appended_images=image_count,
        fetched_pages=fetched_page_count,
        skipped_pages=skipped_page_count,
        failed_pages=failed_page_count,
        completed_articles=completed_article_count,
        max_limit_articles=max_limit_article_count,
    )


def filter_comments(
    target_config: TargetConfig,
    crawl_config: CrawlConfig,
) -> tuple[int, int, int]:
    raw_root = crawl_config.storage.raw_dir / "tgb"
    comments_all_store = JSONLStore(raw_root / "comments_all.jsonl", Comment, "comment_id")
    filtered_store = JSONLStore(raw_root / "comments.jsonl", Comment, "comment_id")
    aoch_store = JSONLStore(raw_root / "aoch_discussions.jsonl", Comment, "comment_id")
    interactions_store = JSONLStore(raw_root / "interactions.jsonl", Interaction, "interaction_id")

    annotated_comments = [
        annotate_comment_author_role(comment, target_config)
        for comment in comments_all_store.read_all()
    ]
    focus_aliases = []
    if target_config.aoch is not None:
        focus_aliases = [target_config.aoch.name, *target_config.aoch.aliases]

    kept_comments, interactions = filter_comments_for_corpus(
        annotated_comments,
        target_author=target_config.target.author_name,
        focus_member_aliases=focus_aliases,
    )
    aoch_comments = select_aoch_comments(annotated_comments)
    filtered_count = filtered_store.append_many(kept_comments)
    aoch_count = aoch_store.append_many(aoch_comments)
    interaction_count = interactions_store.append_many(interactions)
    return filtered_count, aoch_count, interaction_count


def _save_snapshot(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def _upsert_page_state(
    states: list[CommentPageState],
    replacement: CommentPageState,
) -> list[CommentPageState]:
    by_id = {state.state_id: state for state in states}
    by_id[replacement.state_id] = replacement
    return list(by_id.values())


def _build_crawl_error(
    *,
    stage: str,
    article_id: str | None,
    url: str | None,
    error: Exception,
    raw: dict[str, object] | None = None,
) -> CrawlError:
    payload = {
        "stage": stage,
        "article_id": article_id,
        "url": url,
        "error_type": type(error).__name__,
        "error_message": str(error),
    }
    digest = hashlib.sha1(repr(sorted(payload.items())).encode("utf-8")).hexdigest()[:16]
    return CrawlError(
        error_id=f"{stage}:{digest}",
        raw=raw or {},
        **payload,
    )
