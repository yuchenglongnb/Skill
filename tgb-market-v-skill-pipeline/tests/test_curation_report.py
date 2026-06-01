from datetime import UTC, datetime

from tgb_pipeline.curation.report import build_claim_curation_report, suggest_review_reason
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim


def make_claim(
    claim_id: str,
    *,
    source_type: ClaimSourceType = ClaimSourceType.ARTICLE,
    method_tags: list[str] | None = None,
    raw_excerpt: str = "情绪周期切换要结合成交额。",
) -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text=raw_excerpt,
        raw_excerpt=raw_excerpt,
        source_type=source_type,
        source_ids=["a1"],
        article_id="a1",
        source_time=datetime(2023, 1, 15, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=method_tags or ["情绪周期", "成交额"],
    )


def test_suggest_review_reason_is_conservative() -> None:
    accepted_decision = suggest_review_reason(make_claim("claim-a"))
    rejected_decision = suggest_review_reason(make_claim("claim-b", method_tags=[], raw_excerpt="这里能看出什么？"))

    assert accepted_decision == ("accepted", "core_methodology")
    assert rejected_decision == ("rejected", "pure_question")


def test_build_claim_curation_report(tmp_path) -> None:
    accepted = [make_claim("claim-a")]
    rejected = [make_claim("claim-b", method_tags=["情绪周期"], raw_excerpt="四季变化说明周期。")]
    rejected[0].raw["review_reason"] = "analogy_or_background"
    rejected[0].raw["review_decision"] = "rejected"
    needs_edit = [make_claim("claim-c", source_type=ClaimSourceType.INTERACTION)]
    needs_edit[0].raw["review_reason"] = "needs_human_check"
    needs_edit[0].raw["review_decision"] = "needs_edit"
    accepted[0].raw["review_reason"] = "core_methodology"
    accepted[0].raw["review_decision"] = "accepted"

    report_path = build_claim_curation_report(
        [*accepted, *rejected, *needs_edit],
        accepted,
        rejected,
        needs_edit,
        tmp_path,
    )
    report = report_path.read_text(encoding="utf-8")

    assert "accepted_count: 1" in report
    assert "rejected_count: 1" in report
    assert "needs_edit_count: 1" in report
    assert "by_reason" in report

