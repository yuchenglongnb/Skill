"""Discover article seed candidates from offline sources."""

from __future__ import annotations
from pathlib import Path

from tgb_pipeline.config import (
    ArticleDiscoveryConfig,
    TargetConfig,
    load_article_seeds_config,
)
from tgb_pipeline.discovery.extract_links import (
    extract_article_links_from_html,
    extract_article_links_from_text,
)
from tgb_pipeline.discovery.normalize import build_article_seed_candidate
from tgb_pipeline.models import ArticleIndex, ArticleSeedCandidate
from tgb_pipeline.storage import JSONLStore

NOISE_TITLE_TOKENS = {
    "下一页",
    "末页",
    "首页",
    "登录",
    "注册",
    "设置",
    "打赏",
}


def discover_article_candidates(
    discovery_config: ArticleDiscoveryConfig,
    target_config: TargetConfig,
) -> list[ArticleSeedCandidate]:
    start_date = max(discovery_config.start_date, target_config.target.start_article.published_date)
    discovered: list[ArticleSeedCandidate] = []
    base_dir = Path.cwd()
    for source in discovery_config.sources:
        source_path = Path(source.path)
        if not source_path.is_absolute():
            source_path = base_dir / source_path
        discovered.extend(
            _load_source_candidates(
                source_type=source.type,
                source_name=source.name,
                source_path=source_path,
            )
        )

    filtered = [
        candidate
        for candidate in discovered
        if not candidate.published_date or candidate.published_date >= start_date
    ]
    filtered = [
        candidate
        for candidate in filtered
        if not candidate.title or not _looks_like_noise_title(candidate.title)
    ]
    return _merge_candidates(filtered)


def write_article_seed_candidates(
    candidates: list[ArticleSeedCandidate],
    output_path: Path,
) -> int:
    return JSONLStore(output_path, ArticleSeedCandidate, "candidate_id").rewrite_all(candidates)


def _load_source_candidates(
    *,
    source_type: str,
    source_name: str,
    source_path: Path,
) -> list[ArticleSeedCandidate]:
    if source_type == "text_file":
        if not source_path.exists():
            return []
        raw_items = extract_article_links_from_text(source_path.read_text(encoding="utf-8"))
    elif source_type == "html_file":
        if not source_path.exists():
            return []
        raw_items = extract_article_links_from_html(
            source_path.read_text(encoding="utf-8"),
            page_url=None,
        )
    elif source_type == "html_glob":
        raw_items = []
        for file_path in sorted(source_path.parent.glob(source_path.name)):
            raw_items.extend(
                extract_article_links_from_html(
                    file_path.read_text(encoding="utf-8"),
                    page_url=None,
                )
            )
    elif source_type == "article_seeds":
        if not source_path.exists():
            return []
        config = load_article_seeds_config(source_path)
        raw_items = [
            {
                "url": item.url,
                "title": item.title,
                "published_date": item.published_date,
                "tag": item.tag,
                "note": item.note,
                "selected": True,
            }
            for item in config.articles
        ]
    elif source_type == "raw_jsonl_index":
        if not source_path.exists():
            return []
        raw_items = [
            {
                "url": item.url,
                "title": item.title,
                "published_date": item.published_date,
                "tag": item.tag,
                "selected": True,
                "raw_index": True,
            }
            for item in JSONLStore(source_path, ArticleIndex, "article_id").read_all()
        ]
    else:
        raise ValueError(f"unsupported discovery source type: {source_type}")
    return [build_article_seed_candidate(item, source_name) for item in raw_items]


def _looks_like_noise_title(value: str) -> bool:
    normalized = " ".join(value.split()).strip().casefold()
    return normalized in {token.casefold() for token in NOISE_TITLE_TOKENS}


def _merge_candidates(candidates: list[ArticleSeedCandidate]) -> list[ArticleSeedCandidate]:
    merged: dict[str, ArticleSeedCandidate] = {}
    for candidate in candidates:
        current = merged.get(candidate.article_id)
        if current is None:
            merged[candidate.article_id] = candidate
            continue
        merged[candidate.article_id] = _merge_two_candidates(current, candidate)
    return sorted(
        merged.values(),
        key=lambda item: (item.published_date is None, item.published_date or item.article_id, item.article_id),
    )


def _merge_two_candidates(left: ArticleSeedCandidate, right: ArticleSeedCandidate) -> ArticleSeedCandidate:
    preferred = right if _completeness_score(right) > _completeness_score(left) else left
    fallback = left if preferred is right else right
    raw_sources = list(
        dict.fromkeys(
            [
                *preferred.raw.get("sources", []),
                preferred.source,
                *fallback.raw.get("sources", []),
                fallback.source,
            ]
        )
    )
    confidence = _best_confidence(left.confidence, right.confidence)
    return ArticleSeedCandidate(
        candidate_id=preferred.candidate_id,
        article_id=preferred.article_id,
        title=preferred.title or fallback.title,
        published_date=preferred.published_date or fallback.published_date,
        url=preferred.url or fallback.url,
        mobile_url=preferred.mobile_url or fallback.mobile_url,
        tag=preferred.tag or fallback.tag,
        source=", ".join(source for source in raw_sources if source) or preferred.source or fallback.source,
        confidence=confidence,
        selected=left.selected or right.selected,
        note=preferred.note or fallback.note,
        raw={
            **fallback.raw,
            **preferred.raw,
            "sources": [source for source in raw_sources if source],
        },
    )


def _completeness_score(candidate: ArticleSeedCandidate) -> int:
    score = 0
    score += int(bool(candidate.title))
    score += int(candidate.published_date is not None)
    score += int(candidate.confidence == "high") * 2
    score += int(candidate.confidence == "medium")
    return score


def _best_confidence(left: str, right: str) -> str:
    order = {"candidate": 0, "medium": 1, "high": 2}
    return left if order.get(left, 0) >= order.get(right, 0) else right
