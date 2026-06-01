from tgb_pipeline.audit.image_audit import build_image_inventory
from tests.export_fixture_data import build_sample_corpus


def test_build_image_inventory_includes_article_and_comment_images(tmp_path) -> None:
    raw_dir, _, reports_dir = build_sample_corpus(tmp_path)

    report = build_image_inventory(raw_dir, reports_dir / "image_inventory_report.md")

    assert report["total_images"] == 3
    assert report["article_body_images"] == 1
    assert report["comment_images"] == 2
    inventory_text = (reports_dir / "image_inventory_report.md").read_text(encoding="utf-8")
    candidates_text = (reports_dir / "image_review_candidates.md").read_text(encoding="utf-8")
    assert "# Image Inventory Report" in inventory_text
    assert "image-review-1" in candidates_text

