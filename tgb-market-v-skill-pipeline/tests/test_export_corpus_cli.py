from pathlib import Path

from tgb_pipeline.cli import main
from tests.export_fixture_data import build_sample_corpus


def write_configs(tmp_path: Path) -> tuple[Path, Path]:
    target_path = tmp_path / "target.yaml"
    target_path.write_text(
        """
target:
  platform: taoguba
  author_name: 等主人的猫
  start_article:
    title: 情绪周期是否可靠的思考
    published_date: "2023-01-15"
priority_members:
  - name: Aoch
    aliases: [aoch]
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
    return target_path, crawl_path


def test_export_corpus_cli_generates_reports_and_markdown(tmp_path, monkeypatch) -> None:
    build_sample_corpus(tmp_path)
    target_path, crawl_path = write_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(
        [
            "export-corpus",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
        ]
    ) == 0
    assert (tmp_path / "reports" / "comment_coverage_report.md").is_file()
    assert (tmp_path / "data" / "processed" / "tgb" / "target_author_corpus.md").is_file()
