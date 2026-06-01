from tgb_pipeline.audit.comment_audit import build_comment_coverage_report
from tests.export_fixture_data import build_sample_corpus


def test_build_comment_coverage_report_generates_markdown(tmp_path) -> None:
    raw_dir, _, reports_dir = build_sample_corpus(tmp_path)

    report = build_comment_coverage_report(raw_dir, reports_dir / "comment_coverage_report.md")

    assert report["article_count"] == 1
    assert report["total_raw_comments"] == 3
    assert report["total_comment_images"] == 2
    assert report["per_article"][0]["needs_review"] is True
    assert (reports_dir / "comment_coverage_report.md").read_text(encoding="utf-8").startswith(
        "# Comment Coverage Report"
    )

