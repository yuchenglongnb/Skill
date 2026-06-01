"""Comment crawling and filtering tasks."""

from __future__ import annotations

import hashlib
from pathlib import Path

from tgb_pipeline.config import CrawlConfig, TargetConfig
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
from tgb_pipeline.models import ArticleIndex, Comment, CrawlError, ImageAsset, Interaction
from tgb_pipeline.storage import JSONLStore


def crawl_comments(
    target_config: TargetConfig,
    crawl_config: CrawlConfig,
    *,
    fetcher: Fetcher | None = None,
) -> tuple[int, int]:
    raw_root = crawl_config.storage.raw_dir / "tgb"
    html_root = raw_root / "html"
    index_store = JSONLStore(raw_root / "articles_index.jsonl", ArticleIndex, "article_id")
    comments_store = JSONLStore(raw_root / "comments_all.jsonl", Comment, "comment_id")
    images_store = JSONLStore(raw_root / "images.jsonl", ImageAsset, "image_id")
    error_store = JSONLStore(raw_root / "comment_crawl_errors.jsonl", CrawlError, "error_id")
    client = fetcher or Fetcher(crawl_config.crawl)
    comment_count = 0
    image_count = 0

    for article in index_store.read_all():
        max_pages = crawl_config.crawl.max_comment_pages_per_article
        next_page_num = 1
        discovered_last_page = None
        while next_page_num <= max_pages and (
            discovered_last_page is None or next_page_num <= discovered_last_page
        ):
            page_url = build_comment_page_url(article.mobile_url, next_page_num)
            try:
                html = client.get_text(page_url)
                _save_snapshot(
                    html_root / f"{article.article_id}_comments_page_{next_page_num}.html",
                    html,
                )
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
                discovered_last_page = discovered_last_page or find_comment_last_page_num(html, page_url)
                next_page_url = find_comment_next_page_url(html, page_url)
                if not next_page_url:
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
                break
    return comment_count, image_count


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
