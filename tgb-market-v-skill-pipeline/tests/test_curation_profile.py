from datetime import UTC, datetime

from tgb_pipeline.curation.profile import build_curated_methodology_profile
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim


def make_claim(claim_id: str, source_type: ClaimSourceType) -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text="情绪周期切换要结合成交额。",
        raw_excerpt="情绪周期切换要结合成交额。",
        source_type=source_type,
        source_ids=["a1"],
        article_id="a1",
        source_time=datetime(2023, 1, 15, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["情绪周期", "成交额"],
    )


def test_curated_profile_only_uses_accepted_and_needs_edit(tmp_path) -> None:
    report_path = build_curated_methodology_profile(
        [make_claim("claim-a", ClaimSourceType.ARTICLE)],
        [make_claim("claim-b", ClaimSourceType.INTERACTION)],
        tmp_path,
    )
    report = report_path.read_text(encoding="utf-8")

    assert "Curated Methodology Profile" in report
    assert "claim-a" in report
    assert "claim-b" in report
    assert "This is not investment advice." in report

