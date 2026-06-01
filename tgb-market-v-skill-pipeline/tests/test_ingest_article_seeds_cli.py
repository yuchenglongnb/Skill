from datetime import date
from pathlib import Path

from tgb_pipeline.cli import main
from tgb_pipeline.models import ArticleIndex
from tgb_pipeline.storage import JSONLStore


def _write_configs(tmp_path: Path) -> tuple[Path, Path, Path]:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
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
    crawl_path = tmp_path / "crawl.yaml"
    crawl_path.write_text(
        f"""
crawl:
  user_agent: fixture-agent
  request_interval_seconds: 0
  request_timeout_seconds: 10
storage:
  raw_dir: {tmp_path.as_posix()}/data/raw
  interim_dir: {tmp_path.as_posix()}/data/interim
  processed_dir: {tmp_path.as_posix()}/data/processed
""",
        encoding="utf-8",
    )
    seeds_path = tmp_path / "article_seeds.yaml"
    seeds_path.write_text(
        """
version: 1
articles:
  - title: Start article
    published_date: "2023-01-15"
    url: https://www.tgb.cn/a/1Vgsye6eK36
  - title: Later article
    published_date: "2023-01-25"
    url: /Article/5000001/1
""",
        encoding="utf-8",
    )
    return target_path, crawl_path, seeds_path


def test_ingest_article_seeds_cli_merges_and_deduplicates(tmp_path: Path, capsys) -> None:
    target_path, crawl_path, seeds_path = _write_configs(tmp_path)
    raw_dir = tmp_path / "data" / "raw" / "tgb"
    JSONLStore(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id").append(
        ArticleIndex(
            article_id="5000001",
            title="Later article",
            published_date=date(2023, 1, 25),
            view_count=88,
            reply_count=9,
            url="https://www.tgb.cn/Article/5000001/1",
            mobile_url="https://m.tgb.cn/Article/5000001/1",
            raw={"source": "public_index"},
        )
    )

    assert main(
        [
            "ingest-article-seeds",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
            "--article-seeds",
            str(seeds_path),
        ]
    ) == 0
    assert main(
        [
            "ingest-article-seeds",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
            "--article-seeds",
            str(seeds_path),
        ]
    ) == 0

    records = JSONLStore(raw_dir / "articles_index.jsonl", ArticleIndex, "article_id").read_all()
    assert len(records) == 2
    assert records[1].view_count == 88
    assert "duplicates" in capsys.readouterr().out
