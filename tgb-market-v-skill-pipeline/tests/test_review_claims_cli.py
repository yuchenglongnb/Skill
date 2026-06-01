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


def test_review_claims_cli_generates_template_and_apply_outputs(tmp_path, monkeypatch) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    JSONLStore(processed_dir / "methodology_claims.jsonl", MethodologyClaim, "claim_id").append_many(
        [
            MethodologyClaim(
                claim_id="claim-a",
                claim_text="情绪周期切换要结合成交额。",
                raw_excerpt="情绪周期切换要结合成交额。",
                source_type=ClaimSourceType.ARTICLE,
                source_ids=["a1"],
                article_id="a1",
                source_time=datetime(2023, 1, 15, tzinfo=UTC),
                source_author="等主人的猫",
                method_tags=["情绪周期", "成交额"],
            ),
            MethodologyClaim(
                claim_id="claim-b",
                claim_text="这里能看出什么？",
                raw_excerpt="这里能看出什么？",
                source_type=ClaimSourceType.INTERACTION,
                source_ids=["i1"],
                article_id="a1",
                source_time=datetime(2023, 1, 16, tzinfo=UTC),
                source_author="等主人的猫",
                method_tags=[],
            ),
        ]
    )
    target_path, crawl_path = write_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    decisions_path = tmp_path / "data" / "processed" / "tgb" / "claim_review_decisions.yaml"
    assert main(
        [
            "review-claims",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
            "--decisions",
            str(decisions_path),
        ]
    ) == 0
    assert decisions_path.is_file()

    decisions_path.write_text(
        """
version: 1
generated_from: data/processed/tgb/methodology_claims.jsonl
defaults:
  decision: unreviewed
decisions:
  claim-a:
    decision: accepted
    reason: core_methodology
    edited_claim_text: null
    review_notes: 保留
  claim-b:
    decision: rejected
    reason: pure_question
    edited_claim_text: null
    review_notes: 问句不保留
""",
        encoding="utf-8",
    )

    assert main(
        [
            "review-claims",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
            "--decisions",
            str(decisions_path),
            "--apply",
        ]
    ) == 0
    assert (processed_dir / "accepted_methodology_claims.jsonl").is_file()
    assert (processed_dir / "rejected_methodology_claims.jsonl").is_file()
    assert (tmp_path / "reports" / "curated_methodology_profile.md").is_file()
    assert (tmp_path / "reports" / "claim_curation_report.md").is_file()
