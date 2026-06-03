from datetime import UTC, datetime

from tgb_pipeline.extraction.review_ready_report import build_review_ready_report
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def test_build_review_ready_report(tmp_path) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    all_store = JSONLStore(processed_dir / "methodology_claims.jsonl", MethodologyClaim, "claim_id")
    ready_store = JSONLStore(processed_dir / "review_ready_claims.jsonl", MethodologyClaim, "claim_id")
    low_store = JSONLStore(processed_dir / "low_priority_methodology_claims.jsonl", MethodologyClaim, "claim_id")
    review_ready_claim = MethodologyClaim(
        claim_id="claim-1",
        claim_text="弱市风控比进攻更重要。",
        raw_excerpt="弱市风控比进攻更重要。",
        source_type=ClaimSourceType.COMMENT,
        source_ids=["c1"],
        article_id="2ohHCnLXtP8",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["风控"],
        review_priority="high",
        review_bucket="risk_control",
    )
    low_claim = MethodologyClaim(
        claim_id="claim-2",
        claim_text="市场就是这样。",
        raw_excerpt="市场就是这样。",
        source_type=ClaimSourceType.COMMENT,
        source_ids=["c2"],
        article_id="a2",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        review_priority="low",
        review_bucket="generic_market",
    )
    all_store.append_many([review_ready_claim, low_claim])
    ready_store.append(review_ready_claim)
    low_store.append(low_claim)

    report_path = build_review_ready_report(processed_dir, reports_dir)
    report = report_path.read_text(encoding="utf-8")

    assert "Review Ready Claims Report" in report
    assert "methodology_claims: 2" in report
    assert "review_ready_claims: 1" in report
    assert "generic_market" in report
