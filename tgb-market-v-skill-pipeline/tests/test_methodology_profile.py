from datetime import UTC, datetime

from tgb_pipeline.extraction.profile import build_methodology_profile_draft
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def test_build_methodology_profile_draft(tmp_path) -> None:
    processed_dir = tmp_path / "data" / "processed" / "tgb"
    reports_dir = tmp_path / "reports"
    JSONLStore(processed_dir / "methodology_claims.jsonl", MethodologyClaim, "claim_id").append_many(
        [
            MethodologyClaim(
                claim_id="claim-1",
                claim_text="情绪周期切换要结合成交额。",
                raw_excerpt="情绪周期切换要结合成交额。",
                source_type=ClaimSourceType.ARTICLE,
                source_ids=["a1"],
                source_time=datetime(2023, 1, 15, tzinfo=UTC),
                source_author="等主人的猫",
                method_tags=["情绪周期", "成交额"],
            ),
            MethodologyClaim(
                claim_id="claim-2",
                claim_text="量化会影响市场结构。",
                raw_excerpt="量化会影响市场结构。",
                source_type=ClaimSourceType.COMMENT,
                source_ids=["c1"],
                source_time=datetime(2023, 1, 16, tzinfo=UTC),
                source_author="等主人的猫",
                method_tags=["量化影响", "市场结构"],
            ),
        ]
    )

    report_path = build_methodology_profile_draft(processed_dir, reports_dir)
    report = report_path.read_text(encoding="utf-8")

    assert "Methodology Profile Draft" in report
    assert "情绪周期" in report
    assert "量化影响" in report
    assert "不是最终 Skill" in report

