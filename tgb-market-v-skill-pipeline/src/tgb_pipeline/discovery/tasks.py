"""CLI tasks for article discovery and seed promotion."""

from __future__ import annotations

from pathlib import Path

import yaml

from tgb_pipeline.config import (
    ArticleDiscoveryConfig,
    ArticleSeedItem,
    ArticleSeedsConfig,
    TargetConfig,
    load_article_seeds_config,
)
from tgb_pipeline.discovery.discover_articles import (
    discover_article_candidates,
    write_article_seed_candidates,
)
from tgb_pipeline.discovery.report import build_article_seed_candidate_report
from tgb_pipeline.models import ArticleSeedCandidate
from tgb_pipeline.storage import JSONLStore


def discover_article_seeds_task(
    discovery_config: ArticleDiscoveryConfig,
    target_config: TargetConfig,
    *,
    output_path: Path,
    reports_dir: Path,
) -> tuple[int, Path]:
    candidates = discover_article_candidates(discovery_config, target_config)
    write_article_seed_candidates(candidates, output_path)
    report_path = build_article_seed_candidate_report(candidates, reports_dir)
    return len(candidates), report_path


def promote_candidates_to_article_seeds(
    candidates_path: Path,
    seeds_path: Path,
    *,
    only_selected: bool = True,
    min_confidence: str = "medium",
    dry_run: bool = False,
) -> tuple[int, int]:
    candidates = JSONLStore(candidates_path, ArticleSeedCandidate, "candidate_id").read_all()
    seeds_config = _load_or_default_seeds(seeds_path)
    existing_by_id = {
        _seed_article_id(item): item
        for item in seeds_config.articles
    }
    eligible = [
        candidate
        for candidate in candidates
        if _is_candidate_eligible(
            candidate,
            only_selected=only_selected,
            min_confidence=min_confidence,
        )
    ]
    added_count = 0
    for candidate in eligible:
        if candidate.article_id in existing_by_id:
            continue
        if candidate.title is None or candidate.published_date is None:
            continue
        seeds_config.articles.append(
            ArticleSeedItem(
                title=candidate.title,
                published_date=candidate.published_date,
                url=candidate.url,
                tag=candidate.tag,
                note=candidate.note,
            )
        )
        existing_by_id[candidate.article_id] = seeds_config.articles[-1]
        added_count += 1
    seeds_config.articles = sorted(
        seeds_config.articles,
        key=lambda item: (item.published_date, item.title),
    )
    if not dry_run:
        _write_article_seeds_config(seeds_path, seeds_config)
    return added_count, len(seeds_config.articles)


def _is_candidate_eligible(
    candidate: ArticleSeedCandidate,
    *,
    only_selected: bool,
    min_confidence: str,
) -> bool:
    if only_selected and not candidate.selected:
        return False
    return _confidence_rank(candidate.confidence) >= _confidence_rank(min_confidence)


def _confidence_rank(value: str) -> int:
    return {"candidate": 0, "medium": 1, "high": 2}.get(value, 0)


def _load_or_default_seeds(seeds_path: Path) -> ArticleSeedsConfig:
    if not seeds_path.exists():
        return ArticleSeedsConfig(
            version=1,
            source="manual_article_seed_list",
            description="Promoted article seed candidates",
        )
    return load_article_seeds_config(seeds_path)


def _write_article_seeds_config(path: Path, config: ArticleSeedsConfig) -> None:
    payload = {
        "version": config.version,
        "source": config.source,
        "description": config.description,
        "articles": [
            {
                "title": item.title,
                "published_date": item.published_date.isoformat(),
                "url": item.url,
                "tag": item.tag,
                "note": item.note,
            }
            for item in config.articles
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _seed_article_id(item: ArticleSeedItem) -> str:
    from tgb_pipeline.crawler.seed import extract_article_id_from_url

    return extract_article_id_from_url(item.url)
