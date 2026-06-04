from datetime import UTC, datetime
from pathlib import Path

import yaml

from tgb_pipeline.cli import main
from tgb_pipeline.curation.review_encoding_audit import (
    audit_review_file_encoding,
    has_corrupted_review_text,
)
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


def make_claim(claim_id: str, review_notes: str) -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text="量化影响改变了短线反馈速度。",
        raw_excerpt="量化影响改变了短线反馈速度。",
        source_type=ClaimSourceType.COMMENT,
        source_ids=[claim_id],
        article_id="2jbi0efIsof",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["量化影响"],
        review_priority="high",
        review_bucket="trading_mechanism",
        review_notes=review_notes,
        raw={"review_notes": review_notes},
    )


def test_has_corrupted_review_text_detects_question_mark_runs() -> None:
    assert has_corrupted_review_text("????????")
    assert has_corrupted_review_text("保留：??????")
    assert not has_corrupted_review_text("正常中文备注")
    assert not has_corrupted_review_text("What?")
    assert not has_corrupted_review_text(None)


def test_audit_review_file_encoding_detects_corruption_in_yaml_and_jsonl(tmp_path: Path) -> None:
    yaml_path = tmp_path / "pack.yaml"
    yaml_path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "pack_id": "quant_impact_top100",
                "title": "量化影响 Top 100",
                "source_path": "data/processed/tgb/review_ready_claims.jsonl",
                "items": [
                    {
                        "claim_id": "claim-a",
                        "decision": "accepted",
                        "reason": "trading_mechanism",
                        "edited_claim_text": None,
                        "review_notes": "保留：属于量化影响下的交易机制或市场结构判断。",
                    },
                    {
                        "claim_id": "claim-b",
                        "decision": "needs_edit",
                        "reason": "needs_human_check",
                        "edited_claim_text": "??????",
                        "review_notes": "??????",
                    },
                ],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    yaml_stats = audit_review_file_encoding(yaml_path)
    assert yaml_stats["reviewed_items"] == 2
    assert yaml_stats["corrupted_review_notes_count"] == 1
    assert yaml_stats["corrupted_edited_claim_text_count"] == 1
    assert yaml_stats["sample_claim_ids"] == ["claim-b"]

    jsonl_path = tmp_path / "accepted_review_ready_claims.jsonl"
    JSONLStore(jsonl_path, MethodologyClaim, "claim_id").rewrite_all(
        [
            make_claim("claim-a", "正常中文备注"),
            make_claim("claim-b", "????????"),
        ]
    )
    jsonl_stats = audit_review_file_encoding(jsonl_path)
    assert jsonl_stats["reviewed_items"] == 2
    assert jsonl_stats["corrupted_review_notes_count"] == 1


def test_audit_review_encoding_cli_returns_nonzero_when_corrupted(tmp_path: Path, monkeypatch) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    packs_dir = processed_dir / "review_packs"
    packs_dir.mkdir(parents=True, exist_ok=True)
    (processed_dir / "review_ready_decisions.yaml").write_text(
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
                        "review_notes": "??????",
                    }
                },
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (packs_dir / "quant_impact_top100.yaml").write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "pack_id": "quant_impact_top100",
                "title": "量化影响 Top 100",
                "source_path": "data/processed/tgb/review_ready_claims.jsonl",
                "items": [],
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    target_path, crawl_path = write_configs(tmp_path)
    monkeypatch.chdir(tmp_path)

    assert (
        main(
            [
                "audit-review-encoding",
                "--target-config",
                str(target_path),
                "--crawl-config",
                str(crawl_path),
            ]
        )
        == 1
    )
    assert (tmp_path / "reports" / "review_encoding_audit.md").is_file()
