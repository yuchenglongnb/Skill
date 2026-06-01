from datetime import UTC, datetime

from tgb_pipeline.extraction.review_queue import build_claim_review_queue
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def test_build_claim_review_queue(tmp_path) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    JSONLStore(processed_dir / "methodology_claims.jsonl", MethodologyClaim, "claim_id").append(
        MethodologyClaim(
            claim_id="claim-1",
            claim_text="情绪周期切换要结合成交额。",
            raw_excerpt="情绪周期切换要结合成交额。",
            source_type=ClaimSourceType.ARTICLE,
            source_ids=["a1"],
            article_id="a1",
            source_time=datetime(2023, 1, 15, tzinfo=UTC),
            source_author="等主人的猫",
            method_tags=["情绪周期", "成交额"],
        )
    )

    report_path = build_claim_review_queue(processed_dir, reports_dir)
    report = report_path.read_text(encoding="utf-8")

    assert "Claim Review Queue" in report
    assert "claim-1" in report
    assert "情绪周期" in report

