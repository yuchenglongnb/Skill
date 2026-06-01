from pathlib import Path

from tgb_pipeline.config import load_article_seeds_config, load_target_config
from tgb_pipeline.crawler.article_seeds import (
    build_article_index_from_seed,
    load_article_seed_indexes,
)
from tgb_pipeline.crawler.seed import extract_article_id_from_url


def _write_target_config(tmp_path: Path) -> Path:
    path = tmp_path / "target.yaml"
    path.write_text(
        """
target:
  platform: taoguba
  author_name: Target Author
  start_article:
    title: Start article
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/1Vgsye6eK36
""",
        encoding="utf-8",
    )
    return path


def test_extract_article_id_from_multiple_url_patterns() -> None:
    assert extract_article_id_from_url("https://www.tgb.cn/a/1Vgsye6eK36") == "1Vgsye6eK36"
    assert extract_article_id_from_url("https://m.tgb.cn/a/1Vgsye6eK36") == "1Vgsye6eK36"
    assert extract_article_id_from_url("/Article/4588439/1") == "4588439"


def test_load_article_seed_indexes_filters_before_start_date(tmp_path: Path) -> None:
    target = load_target_config(_write_target_config(tmp_path))
    seeds_path = tmp_path / "article_seeds.yaml"
    seeds_path.write_text(
        """
version: 1
articles:
  - title: Too early
    published_date: "2023-01-14"
    url: https://www.tgb.cn/Article/100/1
  - title: Start article
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/1Vgsye6eK36
    note: start article
""",
        encoding="utf-8",
    )

    indexes, skipped_count = load_article_seed_indexes(seeds_path, target)

    assert skipped_count == 1
    assert len(indexes) == 1
    assert indexes[0].article_id == "1Vgsye6eK36"
    assert indexes[0].mobile_url == "https://m.tgb.cn/a/1Vgsye6eK36"
    assert indexes[0].raw["manual_seed"] is True
    assert indexes[0].raw["source"] == "configs/article_seeds.yaml"


def test_build_article_index_from_seed_defaults_optional_fields(tmp_path: Path) -> None:
    target = load_target_config(_write_target_config(tmp_path))
    seeds_path = tmp_path / "article_seeds.yaml"
    seeds_path.write_text(
        """
version: 1
articles:
  - title: Start article
    published_date: "2023-01-15"
    url: https://www.tgb.cn/Article/4588439/1
""",
        encoding="utf-8",
    )
    seed_item = load_article_seeds_config(seeds_path).articles[0]
    seed = build_article_index_from_seed(seed_item, target)

    assert seed.article_id == "4588439"
    assert seed.mobile_url == "https://m.tgb.cn/Article/4588439/1"
    assert seed.view_count == 0
    assert seed.reply_count == 0
