"""Merge and normalize article inventory records."""

from __future__ import annotations

from typing import Any

from tgb_pipeline.models import ArticleIndex


def merge_article_indexes(
    existing: list[ArticleIndex],
    new_records: list[ArticleIndex],
) -> list[ArticleIndex]:
    merged: dict[str, ArticleIndex] = {record.article_id: record for record in existing}
    for record in new_records:
        current = merged.get(record.article_id)
        if current is None:
            merged[record.article_id] = record
            continue
        merged[record.article_id] = _merge_two(current, record)
    return sorted(
        merged.values(),
        key=lambda record: (record.published_date, record.article_id),
    )


def _merge_two(left: ArticleIndex, right: ArticleIndex) -> ArticleIndex:
    preferred = _prefer_more_complete(left, right)
    fallback = right if preferred is left else left
    return ArticleIndex(
        article_id=preferred.article_id,
        title=_pick_text(preferred.title, fallback.title),
        tag=_pick_text(preferred.tag, fallback.tag),
        published_date=preferred.published_date or fallback.published_date,
        view_count=max(left.view_count, right.view_count),
        reply_count=max(left.reply_count, right.reply_count),
        url=_pick_text(preferred.url, fallback.url),
        mobile_url=_pick_text(preferred.mobile_url, fallback.mobile_url),
        raw=_merge_raw(left.raw, right.raw),
    )


def _prefer_more_complete(left: ArticleIndex, right: ArticleIndex) -> ArticleIndex:
    left_score = _completeness_score(left)
    right_score = _completeness_score(right)
    if right_score > left_score:
        return right
    return left


def _completeness_score(record: ArticleIndex) -> int:
    score = 0
    score += int(bool(record.title))
    score += int(bool(record.url))
    score += int(bool(record.mobile_url))
    score += int(record.view_count > 0)
    score += int(record.reply_count > 0)
    score += int(bool(record.tag))
    return score


def _pick_text(primary: str | None, secondary: str | None) -> str | None:
    return primary or secondary


def _merge_raw(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    raw: dict[str, Any] = {}
    raw.update(left)
    raw.update(right)
    raw["sources"] = _collect_sources(left, right)
    return raw


def _collect_sources(*payloads: dict[str, Any]) -> list[str]:
    sources: list[str] = []
    for payload in payloads:
        for source in payload.get("sources", []):
            if source not in sources:
                sources.append(source)
        source = payload.get("source")
        if source and source not in sources:
            sources.append(source)
    return sources
