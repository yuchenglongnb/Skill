from datetime import UTC, datetime
from pathlib import Path

import yaml

from tgb_pipeline.curation.review_ready_decisions import (
    load_review_ready_decisions,
    sync_review_ready_decisions,
    write_review_ready_decision_template,
)
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def make_claim(claim_id: str = "claim-1") -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text="量化影响不是单一因子，而是改变了短线反馈速度。",
        raw_excerpt="量化影响不是单一因子，而是改变了短线反馈速度。",
        source_type=ClaimSourceType.COMMENT,
        source_ids=[f"{claim_id}-source"],
        article_id="2jbi0efIsof",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["量化影响", "数字化/标准化"],
        review_priority="high",
        review_bucket="trading_mechanism",
        raw={"ranking": {"reason": "high_value_tags", "score": 9}},
    )


def test_write_review_ready_decision_template_and_load(tmp_path: Path) -> None:
    path = tmp_path / "review_ready_decisions.yaml"
    write_review_ready_decision_template([make_claim()], path)
    payload = load_review_ready_decisions(path)

    assert path.is_file()
    decision = payload["decisions"]["claim-1"]
    assert decision["decision"] == "unreviewed"
    assert decision["review_priority"] == "high"
    assert decision["review_bucket"] == "trading_mechanism"
    assert decision["ranking_score"] == 9


def test_existing_review_ready_template_is_not_overwritten_by_default(tmp_path: Path) -> None:
    path = tmp_path / "review_ready_decisions.yaml"
    path.write_text("version: 1\ncustom: true\n", encoding="utf-8")

    write_review_ready_decision_template([make_claim()], path, overwrite=False)

    assert "custom: true" in path.read_text(encoding="utf-8")


def test_sync_review_ready_decisions_preserves_adds_and_archives(tmp_path: Path) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    claims_path = processed_dir / "review_ready_claims.jsonl"
    JSONLStore(claims_path, MethodologyClaim, "claim_id").rewrite_all(
        [make_claim("claim-1"), make_claim("claim-2")]
    )
    decisions_path = processed_dir / "review_ready_decisions.yaml"
    decisions_path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "generated_from": "old.jsonl",
                "defaults": {"decision": "unreviewed"},
                "decisions": {
                    "claim-1": {
                        "decision": "accepted",
                        "reason": "trading_mechanism",
                        "edited_claim_text": None,
                        "review_notes": "keep",
                    },
                    "claim-old": {
                        "decision": "rejected",
                        "reason": "too_generic",
                        "edited_claim_text": None,
                        "review_notes": "archive me",
                    },
                },
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    stats = sync_review_ready_decisions(claims_path, decisions_path)
    payload = load_review_ready_decisions(decisions_path)

    assert stats == {
        "preserved": 1,
        "new_added": 1,
        "archived": 1,
        "total_current_claims": 2,
    }
    assert payload["decisions"]["claim-1"]["decision"] == "accepted"
    assert payload["decisions"]["claim-2"]["decision"] == "unreviewed"
    assert "claim-old" in payload["archived_decisions"]
