from datetime import UTC, datetime

from tgb_pipeline.extraction.noise_report import build_claim_noise_report
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim


def test_build_claim_noise_report(tmp_path) -> None:
    reports_dir = tmp_path / "reports"
    claims = [
        MethodologyClaim(
            claim_id="claim-1",
            claim_text="情绪周期不是失效，而是成交额和量化改变了反馈速度。",
            raw_excerpt="情绪周期不是失效，而是成交额和量化改变了反馈速度。",
            source_type=ClaimSourceType.ARTICLE,
            source_ids=["a1"],
            article_id="a1",
            source_time=datetime(2023, 1, 15, tzinfo=UTC),
            source_author="等主人的猫",
            method_tags=["情绪周期", "成交额", "量化影响"],
            raw={"quality": {"reason": "strong_methodology_statement", "score": 8, "flags": []}},
        ),
        MethodologyClaim(
            claim_id="claim-2",
            claim_text="如果指数环境太差，短线基础行情会压制个股高度。",
            raw_excerpt="如果指数环境太差，短线基础行情会压制个股高度。",
            source_type=ClaimSourceType.COMMENT,
            source_ids=["c1"],
            article_id="a1",
            source_time=datetime(2023, 1, 16, tzinfo=UTC),
            source_author="等主人的猫",
            method_tags=["指数环境", "短线基础行情"],
            raw={"quality": {"reason": "strong_methodology_statement", "score": 7, "flags": []}},
        ),
    ]

    report_path = build_claim_noise_report(
        before_count=10,
        after_claims=claims,
        reports_dir=reports_dir,
    )
    report = report_path.read_text(encoding="utf-8")

    assert "Claim Noise Report" in report
    assert "before_count: 10" in report
    assert "after_count: 2" in report
    assert "reduction: 8" in report
    assert "strong_methodology_statement" in report
