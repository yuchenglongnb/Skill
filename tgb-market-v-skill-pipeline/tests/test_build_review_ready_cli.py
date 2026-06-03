from datetime import UTC, datetime
from pathlib import Path

from tgb_pipeline.cli import main
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
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


def test_build_review_ready_claims_cli_generates_outputs(tmp_path, monkeypatch) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    JSONLStore(processed_dir / "methodology_claims.jsonl", MethodologyClaim, "claim_id").append(
        MethodologyClaim(
            claim_id="claim-1",
            claim_text="情绪周期不是失效，而是成交额和量化改变了反馈速度。",
            raw_excerpt="情绪周期不是失效，而是成交额和量化改变了反馈速度。",
            source_type=ClaimSourceType.COMMENT,
            source_ids=["c1"],
            article_id="2jbi0efIsof",
            source_time=datetime(2024, 1, 1, tzinfo=UTC),
            source_author="等主人的猫",
            method_tags=["情绪周期", "成交额", "量化影响"],
            raw={"quality": {"reason": "strong_methodology_statement", "score": 8, "flags": []}},
        )
    )
    target_path, crawl_path = write_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert main(
        [
            "build-review-ready-claims",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
        ]
    ) == 0
    assert (tmp_path / "data" / "processed" / "tgb" / "review_ready_claims.jsonl").is_file()
    assert (tmp_path / "data" / "processed" / "tgb" / "low_priority_methodology_claims.jsonl").is_file()
    assert (tmp_path / "reports" / "claim_sampling_report.md").is_file()
    assert (tmp_path / "reports" / "review_ready_claims_report.md").is_file()
