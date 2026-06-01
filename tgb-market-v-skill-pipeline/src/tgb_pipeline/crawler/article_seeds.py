"""Helpers for manual article seed ingestion."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin, urlsplit

from tgb_pipeline.config import (
    ArticleSeedItem,
    TargetConfig,
    load_article_seeds_config,
)
from tgb_pipeline.crawler.parse_blog import to_mobile_url
from tgb_pipeline.crawler.seed import extract_article_id_from_url
from tgb_pipeline.models import ArticleIndex


def build_article_index_from_seed(
    seed: ArticleSeedItem,
    target_config: TargetConfig,
) -> ArticleIndex:
    url = _absolute_url(seed.url)
    return ArticleIndex(
        article_id=extract_article_id_from_url(url),
        title=seed.title,
        tag=seed.tag,
        published_date=seed.published_date,
        view_count=0,
        reply_count=0,
        url=url,
        mobile_url=to_mobile_url(url),
        raw={
            "source": "configs/article_seeds.yaml",
            "manual_seed": True,
            "note": seed.note,
            "target_start_date": target_config.target.start_article.published_date.isoformat(),
        },
    )


def load_article_seed_indexes(
    path: Path,
    target_config: TargetConfig,
) -> tuple[list[ArticleIndex], int]:
    config = load_article_seeds_config(path)
    start_date = target_config.target.start_article.published_date
    indexes: list[ArticleIndex] = []
    skipped_before_start_count = 0
    for seed in config.articles:
        if seed.published_date < start_date:
            skipped_before_start_count += 1
            continue
        indexes.append(build_article_index_from_seed(seed, target_config))
    return indexes, skipped_before_start_count


def _absolute_url(url: str) -> str:
    if urlsplit(url).scheme:
        return url
    return urljoin("https://www.tgb.cn", url)
