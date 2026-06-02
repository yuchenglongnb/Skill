from pathlib import Path

from tgb_pipeline.config import (
    load_article_discovery_config,
    load_article_seeds_config,
    load_crawl_config,
    load_ocr_config,
    load_target_config,
)


def test_load_configs_from_explicit_paths(tmp_path: Path) -> None:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: 等主人的猫
  blog_url: https://www.tgb.cn/blog/123
  start_article:
    title: 情绪周期是否可靠的思考
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/1Vgsye6eK36
priority_members:
  - name: Aoch
    aliases: [aoch]
    dedicated_index: true
""",
        encoding="utf-8",
    )
    crawl_path = tmp_path / "crawl.yaml"
    crawl_path.write_text(
        """
crawl:
  user_agent: fixture-agent
  request_interval_seconds: 1.5
  request_timeout_seconds: 10
  allow_seed_article_fallback: true
  seed_only_when_index_missing_start: true
  max_comment_pages_per_article: 12
storage:
  raw_dir: fixture/raw
  interim_dir: fixture/interim
  processed_dir: fixture/processed
""",
        encoding="utf-8",
    )

    target = load_target_config(target_path)
    crawl = load_crawl_config(crawl_path)

    assert target.target.author_name == "等主人的猫"
    assert target.target.start_article.published_date.isoformat() == "2023-01-15"
    assert target.target.start_article.url == "https://www.tgb.cn/a/1Vgsye6eK36"
    assert target.aoch is not None
    assert target.aoch.dedicated_index is True
    assert crawl.crawl.user_agent == "fixture-agent"
    assert crawl.crawl.request_interval_seconds == 1.5
    assert crawl.crawl.allow_seed_article_fallback is True
    assert crawl.crawl.seed_only_when_index_missing_start is True
    assert crawl.crawl.max_comment_pages_per_article == 12
    assert crawl.storage.raw_dir == Path("fixture/raw")
    assert crawl.storage.processed_dir == Path("fixture/processed")


def test_load_ocr_config_from_explicit_path(tmp_path: Path) -> None:
    config_path = tmp_path / "ocr.yaml"
    config_path.write_text(
        """
ocr:
  enabled: true
  engine: rapidocr
  languages: [chi_sim, eng]
  preserve_raw_text: true
  normalize_text: true
  min_confidence: 0.9
  skip_if_engine_missing: true
images:
  download_dir: data/raw/tgb/images
  compute_sha256: true
  keep_original_files: true
  request_interval_seconds: 1.0
  request_timeout_seconds: 20
  max_retries: 3
  skip_existing: true
  allowed_extensions: [.jpg, .png]
""",
        encoding="utf-8",
    )

    config = load_ocr_config(config_path)

    assert config.ocr.engine == "rapidocr"
    assert config.ocr.min_confidence == 0.9
    assert config.images.download_dir == Path("data/raw/tgb/images")
    assert config.images.allowed_extensions == [".jpg", ".png"]


def test_load_article_seeds_config_and_crawl_defaults(tmp_path: Path) -> None:
    seeds_path = tmp_path / "article_seeds.yaml"
    seeds_path.write_text(
        """
version: 1
source: manual_article_seed_list
description: seed list
articles:
  - title: Start article
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/1Vgsye6eK36
    note: start article
""",
        encoding="utf-8",
    )
    crawl_path = tmp_path / "crawl.yaml"
    crawl_path.write_text(
        """
crawl:
  user_agent: fixture-agent
  request_interval_seconds: 1.0
  request_timeout_seconds: 10
storage:
  raw_dir: data/raw
  interim_dir: data/interim
  processed_dir: data/processed
""",
        encoding="utf-8",
    )

    seeds = load_article_seeds_config(seeds_path)
    crawl = load_crawl_config(crawl_path)

    assert seeds.articles[0].title == "Start article"
    assert seeds.articles[0].published_date.isoformat() == "2023-01-15"
    assert seeds.articles[0].note == "start article"
    assert crawl.crawl.allow_seed_article_fallback is True
    assert crawl.crawl.seed_only_when_index_missing_start is True


def test_load_article_discovery_config(tmp_path: Path) -> None:
    path = tmp_path / "article_discovery.yaml"
    path.write_text(
        """
version: 1
start_date: "2023-01-15"
sources:
  - name: manual_notes
    type: text_file
    path: data/interim/tgb/manual_article_links.txt
""",
        encoding="utf-8",
    )

    config = load_article_discovery_config(path)

    assert config.start_date.isoformat() == "2023-01-15"
    assert config.sources[0].type == "text_file"
