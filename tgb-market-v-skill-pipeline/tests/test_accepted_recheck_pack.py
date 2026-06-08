import yaml

from tgb_pipeline.skill.recheck_pack import build_accepted_recheck_pack, detect_accepted_recheck_flags
from tests.skill_fixture_data import make_claim


def test_detect_accepted_recheck_flags_marks_colloquial_and_context_claims() -> None:
    claim = make_claim(
        "claim-a",
        "今天低纬战高维，我们都是虫子？",
        tag="牛熊切换",
        review_notes="待确认：疑似反讽，需要结合上下文。",
    )
    flags = detect_accepted_recheck_flags(claim)
    assert "colloquial_or_exaggerated" in flags
    assert "rhetorical_or_question" in flags
    assert "strong_context_dependency" in flags
    assert "review_note_uncertainty" in flags


def test_build_accepted_recheck_pack_outputs_yaml_and_report(tmp_path) -> None:
    accepted = [
        make_claim("claim-a", "今天低纬战高维，我们都是虫子？", tag="牛熊切换"),
        make_claim("claim-b", "量化会改变短线盘中的资金反馈速度与流动性结构分布。", tag="量化影响"),
    ]
    pack_path, report_path, count = build_accepted_recheck_pack(
        accepted,
        tmp_path / "data" / "processed" / "tgb",
        tmp_path / "reports",
    )

    payload = yaml.safe_load(pack_path.read_text(encoding="utf-8"))
    assert count == 1
    assert payload["pack_id"] == "accepted_recheck_v0_2"
    assert payload["items"][0]["claim_id"] == "claim-a"
    assert "recheck_reason" in payload["items"][0]
    assert report_path.is_file()
