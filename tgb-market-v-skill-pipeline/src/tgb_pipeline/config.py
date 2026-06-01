"""YAML-backed configuration for crawl commands."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class StartArticleConfig(BaseModel):
    title: str
    published_date: date
    url: str | None = None


class TargetDetails(BaseModel):
    platform: str
    author_name: str
    author_slug: str | None = None
    blog_url: str | None = None
    start_article: StartArticleConfig
    include_after_start_article: bool = True


class PriorityMemberConfig(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)
    dedicated_index: bool = False


class TargetConfig(BaseModel):
    target: TargetDetails
    priority_members: list[PriorityMemberConfig] = Field(default_factory=list)
    corpus_policy: dict[str, bool] = Field(default_factory=dict)

    @property
    def aoch(self) -> PriorityMemberConfig | None:
        return next(
            (
                member
                for member in self.priority_members
                if member.name.casefold() == "aoch"
            ),
            None,
        )


class CrawlSettings(BaseModel):
    user_agent: str
    request_interval_seconds: float = Field(ge=0)
    request_timeout_seconds: float = Field(gt=0)
    max_retries: int = Field(default=3, ge=0)
    max_index_pages: int = Field(default=100, ge=1)
    concurrency: int = Field(default=1, ge=1)
    respect_robots_txt: bool = True
    resume: bool = True
    allow_seed_article_fallback: bool = True
    seed_only_when_index_missing_start: bool = True
    max_comment_pages_per_article: int = Field(default=100, ge=1)


class StorageSettings(BaseModel):
    raw_dir: Path
    interim_dir: Path
    processed_dir: Path
    jsonl_encoding: str = "utf-8"


class CrawlConfig(BaseModel):
    crawl: CrawlSettings
    storage: StorageSettings


def load_target_config(path: str | Path) -> TargetConfig:
    return TargetConfig.parse_obj(_read_yaml(path))


def load_crawl_config(path: str | Path) -> CrawlConfig:
    return CrawlConfig.parse_obj(_read_yaml(path))


def _read_yaml(path: str | Path) -> dict:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"config must contain a YAML mapping: {config_path}")
    return payload
