"""Segment corpus records into claim-sized text windows."""

from __future__ import annotations

import re
from typing import Any

from tgb_pipeline.models import Article, Comment, ImageAsset, ImageOCR, Interaction
from tgb_pipeline.utils.text_cleaning import clean_text

SPLIT_RE = re.compile(r"(?<=[。！？!?；;\n])")
MEANINGFUL_RE = re.compile(r"[\u4e00-\u9fffA-Za-z]")
DIGIT_ONLY_RE = re.compile(r"^[\d\W_]+$")
IMAGE_PLACEHOLDER_RE = re.compile(r"^\[IMAGE:\s*[^\]]+\]$", re.IGNORECASE)
KEYWORD_HINTS = (
    "情绪",
    "周期",
    "成交额",
    "量化",
    "指数",
    "市场",
    "结构",
    "龙头",
    "风控",
    "仓位",
    "买入",
    "卖出",
    "反核",
    "赚钱",
    "亏钱",
)


def segment_article(article: Article) -> list[dict[str, Any]]:
    return _segment_text(
        text=article.content_text or article.raw_content,
        source_type="article",
        source_id=article.article_id,
        article_id=article.article_id,
        author_name=article.author_name,
        source_time=article.published_at,
        source_title=article.title,
        evidence_level="article_text",
    )


def segment_comment(comment: Comment) -> list[dict[str, Any]]:
    evidence_level = "target_comment_text" if comment.author_role.value == "target" else "comment_text"
    return _segment_text(
        text=comment.content_text or comment.raw_content,
        source_type="comment",
        source_id=comment.comment_id,
        article_id=comment.article_id,
        author_name=comment.author_name,
        source_time=comment.published_at,
        source_title=None,
        evidence_level=evidence_level,
    )


def segment_interaction(
    interaction: Interaction,
    comments_by_id: dict[str, Comment],
) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    if interaction.raw_content:
        segments.extend(
            _segment_text(
                text=interaction.raw_content,
                source_type="interaction",
                source_id=interaction.interaction_id,
                article_id=interaction.article_id,
                author_name=interaction.actor_name,
                source_time=interaction.occurred_at,
                source_title=None,
                evidence_level="interaction_text",
            )
        )
    for comment_id in interaction.comment_ids:
        comment = comments_by_id.get(comment_id)
        if comment is None:
            continue
        segments.extend(
            _segment_text(
                text=comment.content_text or comment.raw_content,
                source_type="interaction",
                source_id=f"{interaction.interaction_id}:{comment.comment_id}",
                article_id=comment.article_id,
                author_name=comment.author_name,
                source_time=comment.published_at,
                source_title=None,
                evidence_level="interaction_text",
            )
        )
    return _dedupe_segments(segments)


def segment_ocr(ocr: ImageOCR, image: ImageAsset | None = None) -> list[dict[str, Any]]:
    return _segment_text(
        text=ocr.normalized_text or ocr.raw_text,
        source_type="image_ocr",
        source_id=ocr.ocr_id,
        article_id=image.article_id if image else None,
        author_name=None,
        source_time=None,
        source_title=None,
        evidence_level="image_ocr_unreviewed",
    )


def _segment_text(
    *,
    text: str | None,
    source_type: str,
    source_id: str,
    article_id: str | None,
    author_name: str | None,
    source_time,
    source_title: str | None,
    evidence_level: str,
) -> list[dict[str, Any]]:
    normalized = clean_text(text or "")
    if not normalized:
        return []
    parts = [clean_text(part) for part in SPLIT_RE.split(normalized) if clean_text(part)]
    segments: list[dict[str, Any]] = []
    for part in parts:
        if _should_skip_segment(part):
            continue
        segments.append(
            {
                "source_type": source_type,
                "source_id": source_id,
                "article_id": article_id,
                "author_name": author_name,
                "text": part,
                "source_time": source_time,
                "source_title": source_title,
                "evidence_level": evidence_level,
            }
        )
    return segments


def _should_skip_segment(text: str) -> bool:
    compact = text.strip()
    if not compact:
        return True
    if IMAGE_PLACEHOLDER_RE.match(compact):
        return True
    if len(compact) <= 2 and not any(keyword in compact for keyword in KEYWORD_HINTS):
        return True
    if DIGIT_ONLY_RE.match(compact) and not any(keyword in compact for keyword in KEYWORD_HINTS):
        return True
    if not MEANINGFUL_RE.search(compact):
        return True
    if len(compact) < 6 and not any(keyword in compact for keyword in KEYWORD_HINTS):
        return True
    return False


def _dedupe_segments(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for segment in segments:
        key = (segment["source_id"], segment["text"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(segment)
    return deduped
