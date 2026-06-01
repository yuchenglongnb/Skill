"""Rule-based methodology claim extraction from the processed corpus."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from tgb_pipeline.extraction.entities import (
    extract_sectors_or_concepts,
    extract_tickers,
    infer_direction,
    infer_horizon,
)
from tgb_pipeline.extraction.segments import (
    segment_article,
    segment_comment,
    segment_interaction,
    segment_ocr,
)
from tgb_pipeline.extraction.tags import detect_method_tags
from tgb_pipeline.models import (
    Article,
    AuthorRole,
    Comment,
    ImageAsset,
    ImageOCR,
    MethodologyClaim,
)
from tgb_pipeline.models import ClaimSourceType, ClaimStatus, Interaction
from tgb_pipeline.storage import JSONLStore
from tgb_pipeline.utils.text_cleaning import clean_text

REASONING_HINTS = ("因为", "所以", "如果", "但是", "本质", "规律", "标准", "周期", "成交额", "量化")
MARKET_HINTS = ("市场", "指数", "板块", "题材", "个股", "龙头", "情绪", "周期")


def extract_claims_from_segments(segments: list[dict[str, Any]]) -> list[MethodologyClaim]:
    claims: list[MethodologyClaim] = []
    seen: set[tuple[str, str]] = set()
    claim_ids: set[str] = set()
    for segment in segments:
        text = clean_text(segment["text"])
        normalized = _normalize_for_dedupe(text)
        key = (segment["source_id"], normalized)
        if key in seen:
            continue
        seen.add(key)

        method_tags = detect_method_tags(text)
        tickers = extract_tickers(text)
        sectors, concepts = extract_sectors_or_concepts(text)
        if not _should_make_claim(segment, text, method_tags, tickers, sectors, concepts):
            continue

        source_type = ClaimSourceType(segment["source_type"])
        claim_id = _build_claim_id(source_type.value, segment["source_id"], normalized)
        if claim_id in claim_ids:
            continue
        claim_ids.add(claim_id)
        claims.append(
            MethodologyClaim(
                claim_id=claim_id,
                claim_text=text,
                raw_excerpt=text,
                source_type=source_type,
                source_ids=[segment["source_id"]],
                article_id=segment.get("article_id"),
                source_title=segment.get("source_title"),
                source_time=segment.get("source_time"),
                source_author=segment.get("author_name"),
                method_tags=method_tags,
                mentioned_tickers=tickers,
                mentioned_sectors=sectors,
                mentioned_concepts=concepts,
                direction=infer_direction(text),
                horizon=infer_horizon(text),
                confidence_level="candidate",
                evidence_text=text,
                evidence_level=segment.get("evidence_level", "text_raw"),
                review_status="unreviewed",
                evidence_image_ids=list(segment.get("evidence_image_ids", [])),
                evidence_ocr_ids=list(segment.get("evidence_ocr_ids", [])),
                author_name=segment.get("author_name"),
                status=ClaimStatus.CANDIDATE,
                tags=list(method_tags),
                raw={"source_segment": segment},
            )
        )
    return claims


def extract_claims_from_corpus(raw_dir: Path, processed_dir: Path) -> list[MethodologyClaim]:
    articles = JSONLStore(raw_dir / "articles.jsonl", Article, "article_id").read_all()
    comments = JSONLStore(raw_dir / "comments.jsonl", Comment, "comment_id").read_all()
    interactions = JSONLStore(raw_dir / "interactions.jsonl", Interaction, "interaction_id").read_all()
    comments_all = _read_optional(raw_dir / "comments_all.jsonl", Comment, "comment_id")
    images = _read_optional(raw_dir / "images.jsonl", ImageAsset, "image_id")
    image_ocr = _read_optional(processed_dir / "image_ocr.jsonl", ImageOCR, "ocr_id")

    comments_by_id = {comment.comment_id: comment for comment in comments_all}
    images_by_comment_id = _index_images_by_comment(images)
    images_by_article_id = _index_images_by_article(images)
    images_by_image_id = {image.image_id: image for image in images}

    segments: list[dict[str, Any]] = []
    for article in articles:
        article_segments = segment_article(article)
        for segment in article_segments:
            segment["evidence_image_ids"] = list(images_by_article_id.get(article.article_id, []))
        segments.extend(article_segments)

    for comment in comments:
        if comment.author_role == AuthorRole.AOCH:
            continue
        if comment.author_role != AuthorRole.TARGET:
            continue
        comment_segments = segment_comment(comment)
        for segment in comment_segments:
            segment["evidence_image_ids"] = list(images_by_comment_id.get(comment.comment_id, []))
        segments.extend(comment_segments)

    for interaction in interactions:
        interaction_segments = segment_interaction(interaction, comments_by_id)
        filtered = [
            segment for segment in interaction_segments
            if segment.get("author_name") and _is_target_text_segment(segment, comments_by_id)
        ]
        segments.extend(filtered)

    for ocr in image_ocr:
        image = images_by_image_id.get(ocr.image_id)
        ocr_segments = segment_ocr(ocr, image)
        for segment in ocr_segments:
            segment["evidence_ocr_ids"] = [ocr.ocr_id]
            segment["evidence_image_ids"] = [ocr.image_id]
        segments.extend(ocr_segments)

    claims = extract_claims_from_segments(segments)
    output_path = processed_dir / "methodology_claims.jsonl"
    JSONLStore(output_path, MethodologyClaim, "claim_id").rewrite_all(claims)
    return claims


def _should_make_claim(
    segment: dict[str, Any],
    text: str,
    method_tags: list[str],
    tickers: list[str],
    sectors: list[str],
    concepts: list[str],
) -> bool:
    if method_tags:
        return True
    if tickers or sectors or concepts:
        return True
    if segment["source_type"] in {"article", "comment", "interaction"} and any(hint in text for hint in REASONING_HINTS):
        return True
    if any(hint in text for hint in MARKET_HINTS):
        return True
    return False


def _build_claim_id(source_type: str, source_id: str, normalized_excerpt: str) -> str:
    digest = hashlib.sha256(f"{source_type}|{source_id}|{normalized_excerpt}".encode("utf-8")).hexdigest()
    return f"claim-{digest[:16]}"


def _normalize_for_dedupe(text: str) -> str:
    return re.sub(r"\s+", "", text).casefold()


def _is_target_text_segment(segment: dict[str, Any], comments_by_id: dict[str, Comment]) -> bool:
    source_id = str(segment["source_id"])
    if ":" in source_id:
        comment_id = source_id.split(":")[-1]
        comment = comments_by_id.get(comment_id)
        return comment is not None and comment.author_role == AuthorRole.TARGET
    return segment.get("author_name") is not None and "猫" in str(segment.get("author_name"))


def _read_optional(path: Path, model_type, key_field: str):
    if not path.exists():
        return []
    return JSONLStore(path, model_type, key_field).read_all()


def _index_images_by_comment(images: list[ImageAsset]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for image in images:
        if image.comment_id:
            index.setdefault(image.comment_id, []).append(image.image_id)
    return index


def _index_images_by_article(images: list[ImageAsset]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for image in images:
        if image.article_id and image.source_type == "article_body":
            index.setdefault(image.article_id, []).append(image.image_id)
    return index

