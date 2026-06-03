from datetime import UTC, datetime

from tgb_pipeline.extraction.sampling_report import build_claim_sampling_report
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def test_build_claim_sampling_report(tmp_path) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    claim = MethodologyClaim(
        claim_id="claim-1",
        claim_text="情绪周期不是失效，而是成交额和量化改变了反馈速度。",
        raw_excerpt="情绪周期不是失效，而是成交额和量化改变了反馈速度。",
        source_type=ClaimSourceType.COMMENT,
        source_ids=["c1"],
        article_id="2jbi0efIsof",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["量化影响"],
        review_priority="high",
        review_bucket="trading_mechanism",
        raw={"ranking": {"reason": "strong_structure", "score": 8, "flags": []}},
    )
    JSONLStore(processed_dir / "methodology_claims.jsonl", MethodologyClaim, "claim_id").append(claim)
    JSONLStore(processed_dir / "review_ready_claims.jsonl", MethodologyClaim, "claim_id").append(claim)

    report_path = build_claim_sampling_report(processed_dir, reports_dir, sample_per_bucket=20)
    report = report_path.read_text(encoding="utf-8")

    assert "Claim Sampling Report" in report
    assert "review_ready_claims: 1" in report
    assert "trading_mechanism" in report
    assert "claim-1" in report
