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
    resume_comment_pages_from_snapshots: bool = True


class StorageSettings(BaseModel):
    raw_dir: Path
    interim_dir: Path
    processed_dir: Path
    jsonl_encoding: str = "utf-8"


class CommentCompletionSettings(BaseModel):
    default_pages_per_article: int = Field(default=100, ge=1)
    max_total_pages_per_run: int = Field(default=300, ge=1)
    priority_article_ids: list[str] = Field(default_factory=list)
    skip_completed: bool = True
    skip_active_errors: bool = False


class CrawlConfig(BaseModel):
    crawl: CrawlSettings
    storage: StorageSettings
    comment_completion: CommentCompletionSettings = Field(
        default_factory=CommentCompletionSettings
    )


class OCRSettings(BaseModel):
    enabled: bool = True
    engine: str | None = "rapidocr"
    languages: list[str] = Field(default_factory=lambda: ["chi_sim", "eng"])
    preserve_raw_text: bool = True
    normalize_text: bool = True
    min_confidence: float | None = Field(default=0.85, ge=0, le=1)
    skip_if_engine_missing: bool = True


class ImageDownloadSettings(BaseModel):
    download_dir: Path = Path("data/raw/tgb/images")
    compute_sha256: bool = True
    keep_original_files: bool = True
    request_interval_seconds: float = Field(default=1.0, ge=0)
    request_timeout_seconds: float = Field(default=20.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    skip_existing: bool = True
    allowed_extensions: list[str] = Field(
        default_factory=lambda: [".jpg", ".jpeg", ".png", ".webp"],
    )
    allow_noise_images_for_ocr: bool = False


class OCRConfig(BaseModel):
    ocr: OCRSettings = Field(default_factory=OCRSettings)
    images: ImageDownloadSettings = Field(default_factory=ImageDownloadSettings)


class ArticleSeedItem(BaseModel):
    title: str
    published_date: date
    url: str
    tag: str | None = None
    note: str | None = None


class ArticleSeedsConfig(BaseModel):
    version: int = 1
    source: str | None = None
    description: str | None = None
    articles: list[ArticleSeedItem] = Field(default_factory=list)


class ArticleDiscoverySource(BaseModel):
    name: str
    type: str
    path: str


class ArticleDiscoveryConfig(BaseModel):
    version: int = 1
    start_date: date
    sources: list[ArticleDiscoverySource] = Field(default_factory=list)


def load_target_config(path: str | Path) -> TargetConfig:
    return TargetConfig.parse_obj(_read_yaml(path))


def load_crawl_config(path: str | Path) -> CrawlConfig:
    return CrawlConfig.parse_obj(_read_yaml(path))


def load_ocr_config(path: str | Path) -> OCRConfig:
    return OCRConfig.parse_obj(_read_yaml(path))


def load_article_seeds_config(path: str | Path) -> ArticleSeedsConfig:
    return ArticleSeedsConfig.parse_obj(_read_yaml(path))


def load_article_discovery_config(path: str | Path) -> ArticleDiscoveryConfig:
    return ArticleDiscoveryConfig.parse_obj(_read_yaml(path))


def _read_yaml(path: str | Path) -> dict:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"config must contain a YAML mapping: {config_path}")
    return payload
