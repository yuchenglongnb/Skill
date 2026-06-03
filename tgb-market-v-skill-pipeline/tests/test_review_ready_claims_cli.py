from datetime import UTC, datetime
from pathlib import Path

import yaml

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


def make_claim(claim_id: str) -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text="量化影响不是单一因子，而是改变了短线反馈速度。",
        raw_excerpt="量化影响不是单一因子，而是改变了短线反馈速度。",
        source_type=ClaimSourceType.COMMENT,
        source_ids=[claim_id],
        article_id="2jbi0efIsof",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["量化影响", "短线基础行情"],
        review_priority="high",
        review_bucket="trading_mechanism",
        raw={"ranking": {"reason": "high_value_tags", "score": 9}},
    )


def test_review_ready_claims_cli_generates_template_and_apply_outputs(tmp_path, monkeypatch) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    raw_dir = tmp_path / "data" / "raw" / "tgb"
    JSONLStore(processed_dir / "review_ready_claims.jsonl", MethodologyClaim, "claim_id").append_many(
        [make_claim("claim-a"), make_claim("claim-b")]
    )
    (raw_dir / "articles.jsonl").parent.mkdir(parents=True, exist_ok=True)
    target_path, crawl_path = write_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    decisions_path = processed_dir / "review_ready_decisions.yaml"
    assert main(
        [
            "review-ready-claims",
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
        yaml.safe_dump(
            {
                "version": 1,
                "generated_from": "data/processed/tgb/review_ready_claims.jsonl",
                "defaults": {"decision": "unreviewed"},
                "decisions": {
                    "claim-a": {
                        "decision": "accepted",
                        "reason": "trading_mechanism",
                        "edited_claim_text": None,
                        "review_notes": "keep",
                    },
                    "claim-b": {
                        "decision": "needs_edit",
                        "reason": "needs_human_check",
                        "edited_claim_text": "量化改变了短线反馈速度。",
                        "review_notes": "compress",
                    },
                },
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    assert main(
        [
            "review-ready-claims",
            "--target-config",
            str(target_path),
            "--crawl-config",
            str(crawl_path),
            "--decisions",
            str(decisions_path),
            "--apply",
        ]
    ) == 0

    assert (processed_dir / "accepted_review_ready_claims.jsonl").is_file()
    assert (processed_dir / "rejected_review_ready_claims.jsonl").is_file()
    assert (processed_dir / "needs_edit_review_ready_claims.jsonl").is_file()
    assert (tmp_path / "reports" / "review_ready_curated_profile.md").is_file()
    assert (tmp_path / "reports" / "review_ready_curation_report.md").is_file()
