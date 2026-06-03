from datetime import UTC, datetime

from tgb_pipeline.curation.review_ready_profile import build_review_ready_curated_profile
from tgb_pipeline.models import ClaimSourceType, MethodologyClaim


def make_claim(claim_id: str, *, source_type: ClaimSourceType) -> MethodologyClaim:
    return MethodologyClaim(
        claim_id=claim_id,
        claim_text="数字化/标准化的目标是把活跃度转成统一可比较指标。",
        raw_excerpt="数字化/标准化的目标是把活跃度转成统一可比较指标。",
        source_type=source_type,
        source_ids=[claim_id],
        article_id="a1",
        source_time=datetime(2024, 1, 1, tzinfo=UTC),
        source_author="等主人的猫",
        method_tags=["数字化/标准化", "量化影响"],
        review_priority="high" if source_type == ClaimSourceType.COMMENT else "normal",
        review_bucket="trading_mechanism",
        raw={},
    )


def test_build_review_ready_curated_profile_prefers_article_then_high_priority_comments(tmp_path) -> None:
    accepted = [make_claim("article-1", source_type=ClaimSourceType.ARTICLE)]
    needs_edit = [make_claim("comment-1", source_type=ClaimSourceType.COMMENT)]

    report_path = build_review_ready_curated_profile(accepted, needs_edit, tmp_path)
    text = report_path.read_text(encoding="utf-8")

    assert report_path.is_file()
    assert "accepted_claims: 1" in text
    assert "needs_edit_claims: 1" in text
    assert "### 数字化/标准化" in text
    assert text.index("article-1") < text.index("comment-1")
