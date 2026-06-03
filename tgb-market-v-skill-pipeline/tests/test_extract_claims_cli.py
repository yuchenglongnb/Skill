from datetime import UTC, datetime
from pathlib import Path

from tgb_pipeline.cli import main
from tgb_pipeline.models import Article, AuthorRole, Comment, Interaction, InteractionType
from tgb_pipeline.storage import JSONLStore


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


def test_extract_claims_cli_generates_outputs(tmp_path, monkeypatch) -> None:
    raw_dir = tmp_path / "data" / "raw" / "tgb"
    JSONLStore(raw_dir / "articles.jsonl", Article, "article_id").append(
        Article(
            article_id="a1",
            title="情绪周期思考",
            author_name="等主人的猫",
            published_at=datetime(2023, 1, 15, tzinfo=UTC),
            url="https://example.test/a1",
            raw_content="情绪周期切换要结合成交额。",
            content_text="情绪周期切换要结合成交额。",
        )
    )
    JSONLStore(raw_dir / "comments.jsonl", Comment, "comment_id").append(
        Comment(
            comment_id="c1",
            article_id="a1",
            author_name="等主人的猫",
            author_role=AuthorRole.TARGET,
            published_at=datetime(2023, 1, 16, tzinfo=UTC),
            raw_content="量化影响市场结构。",
            content_text="量化影响市场结构。",
        )
    )
    JSONLStore(raw_dir / "comments_all.jsonl", Comment, "comment_id").append(
        Comment(
            comment_id="c1",
            article_id="a1",
            author_name="等主人的猫",
            author_role=AuthorRole.TARGET,
            published_at=datetime(2023, 1, 16, tzinfo=UTC),
            raw_content="量化影响市场结构。",
            content_text="量化影响市场结构。",
        )
    )
    JSONLStore(raw_dir / "interactions.jsonl", Interaction, "interaction_id").append(
        Interaction(
            interaction_id="i1",
            article_id="a1",
            interaction_type=InteractionType.REPLY,
            actor_name="等主人的猫",
            raw_content="成交额回升后短线基础行情会更稳定。",
        )
    )
    target_path, crawl_path = write_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(
        [
            "extract-claims",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
        ]
    ) == 0
    assert (tmp_path / "data" / "processed" / "tgb" / "methodology_claims.jsonl").is_file()
    assert (tmp_path / "reports" / "claim_noise_report.md").is_file()
    assert (tmp_path / "reports" / "claim_review_queue.md").is_file()
    assert (tmp_path / "reports" / "methodology_profile_draft.md").is_file()
