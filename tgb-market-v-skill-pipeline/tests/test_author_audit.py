from tgb_pipeline.audit.author_audit import build_author_inventory
from tgb_pipeline.config import TargetConfig
from tests.export_fixture_data import build_sample_corpus


def make_target_config() -> TargetConfig:
    return TargetConfig.parse_obj(
        {
            "target": {
                "platform": "taoguba",
                "author_name": "等主人的猫",
                "start_article": {"title": "情绪周期是否可靠的思考", "published_date": "2023-01-15"},
            },
            "priority_members": [{"name": "Aoch", "aliases": ["aoch"]}],
        }
    )


def test_build_author_inventory_reports_aoch_zero_without_error(tmp_path) -> None:
    raw_dir, _, reports_dir = build_sample_corpus(tmp_path, include_aoch=False)

    report = build_author_inventory(raw_dir, reports_dir / "author_inventory.md", make_target_config())

    assert report["unique_author_count"] == 3
    assert report["target_author_comment_count"] == 1
    assert report["aoch_comment_count"] == 0
    text = (reports_dir / "author_inventory.md").read_text(encoding="utf-8")
    assert "no exact Aoch alias match" in text

