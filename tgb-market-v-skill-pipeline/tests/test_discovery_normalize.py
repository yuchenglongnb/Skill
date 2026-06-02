from datetime import date

from tgb_pipeline.discovery.normalize import (
    build_article_seed_candidate,
    normalize_article_url,
)


def test_normalize_article_url_collapses_comment_page_to_article_url() -> None:
    article_id, url, mobile_url = normalize_article_url(
        "https://www.tgb.cn/a/1Vgsye6eK36-2?type="
    )

    assert article_id == "1Vgsye6eK36"
    assert url == "https://www.tgb.cn/a/1Vgsye6eK36"
    assert mobile_url == "https://m.tgb.cn/a/1Vgsye6eK36"


def test_build_article_seed_candidate_keeps_audit_raw_fields() -> None:
    candidate = build_article_seed_candidate(
        {
            "url": "/Article/4588439/1",
            "title": "情绪周期是否可靠的思考",
            "published_date": date(2023, 1, 15),
        },
        "manual_notes",
    )

    assert candidate.candidate_id == "candidate-4588439"
    assert candidate.confidence == "high"
    assert candidate.raw["original_url"] == "/Article/4588439/1"
    assert candidate.raw["source_name"] == "manual_notes"
    assert candidate.raw["extracted_date"] == "2023-01-15"
