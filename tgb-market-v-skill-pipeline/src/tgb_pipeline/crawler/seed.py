"""Seed fallback helpers for explicit start article URLs."""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlsplit

from tgb_pipeline.config import TargetConfig
from tgb_pipeline.crawler.parse_blog import to_mobile_url
from tgb_pipeline.models import ArticleIndex

ARTICLE_PATH = re.compile(r"/(?:Article|article)/(?P<id>\d+)(?:/|$)")
SHORT_PATH = re.compile(r"/a/(?P<id>[A-Za-z0-9]+)(?:/|$)")


def build_seed_article_index(target_config: TargetConfig) -> ArticleIndex:
    start_article = target_config.target.start_article
    if not start_article.url:
        raise ValueError("target.start_article.url must be configured for seed fallback")
    url = _absolute_url(start_article.url)
    return ArticleIndex(
        article_id=extract_article_id_from_url(url),
        title=start_article.title,
        published_date=start_article.published_date,
        tag=None,
        view_count=0,
        reply_count=0,
        url=url,
        mobile_url=to_mobile_url(url),
        raw={
            "source": "target_config.start_article.url",
            "seed_fallback": True,
        },
    )


def extract_article_id_from_url(url: str) -> str:
    path = urlsplit(_absolute_url(url)).path
    match = SHORT_PATH.search(path) or ARTICLE_PATH.search(path)
    if not match:
        raise ValueError(f"could not extract article_id from start article url: {url}")
    return match.group("id")


def _absolute_url(url: str) -> str:
    if urlsplit(url).scheme:
        return url
    return urljoin("https://www.tgb.cn", url)
