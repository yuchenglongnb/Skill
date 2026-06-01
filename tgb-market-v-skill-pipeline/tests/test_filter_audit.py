from tgb_pipeline.audit.filter_audit import build_filter_quality_report
from tests.export_fixture_data import build_sample_corpus


def test_build_filter_quality_report_lists_keep_and_filter_reasons(tmp_path) -> None:
    raw_dir, _, reports_dir = build_sample_corpus(tmp_path)

    report = build_filter_quality_report(raw_dir, reports_dir / "filter_quality_report.md")

    assert report["raw_comment_count"] == 3
    assert report["kept_comment_count"] == 2
    assert report["interaction_count"] == 1
    text = (reports_dir / "filter_quality_report.md").read_text(encoding="utf-8")
    assert "target_author_comment" in text
    assert "low_value" in text
    assert "interaction-1" in text

