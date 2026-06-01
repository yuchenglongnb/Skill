from pathlib import Path

from tgb_pipeline.config import load_crawl_config, load_target_config


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
    assert target.aoch is not None
    assert target.aoch.dedicated_index is True
    assert crawl.crawl.user_agent == "fixture-agent"
    assert crawl.crawl.request_interval_seconds == 1.5
    assert crawl.storage.raw_dir == Path("fixture/raw")
    assert crawl.storage.processed_dir == Path("fixture/processed")

