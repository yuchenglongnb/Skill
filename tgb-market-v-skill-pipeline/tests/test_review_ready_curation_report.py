from datetime import UTC, datetime

from tgb_pipeline.curation.review_ready_report import build_review_ready_curation_report
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim


def make_claim(claim_id: str, *, source_type: ClaimSourceType = ClaimSourceType.COMMENT) -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text="风控不是口号，而是交易边界。",
        raw_excerpt="风控不是口号，而是交易边界。",
        source_type=source_type,
        source_ids=[claim_id],
        article_id="2ohHCnLXtP8",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["风控"],
        raw={"review_reason": "risk_control", "review_decision": "accepted"},
    )


def test_build_review_ready_curation_report(tmp_path) -> None:
    all_claims = [make_claim("a"), make_claim("b"), make_claim("c")]
    accepted = [make_claim("a", source_type=ClaimSourceType.ARTICLE)]
    rejected = [make_claim("b")]
    rejected[0].raw["review_reason"] = "too_generic"
    rejected[0].raw["review_decision"] = "rejected"
    needs_edit = [make_claim("c")]
    needs_edit[0].raw["review_reason"] = "needs_human_check"
    needs_edit[0].raw["review_decision"] = "needs_edit"

    report_path = build_review_ready_curation_report(all_claims, accepted, rejected, needs_edit, tmp_path)
    text = report_path.read_text(encoding="utf-8")

    assert report_path.is_file()
    assert "accepted_count: 1" in text
    assert "rejected_count: 1" in text
    assert "needs_edit_count: 1" in text
    assert "source_type_distribution" in text
