from tgb_pipeline.skill.profile_builder import build_methodology_profile_v0
from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tests.skill_fixture_data import make_claim


def test_build_methodology_profile_v0_uses_rules_and_separates_needs_edit(tmp_path) -> None:
    accepted = [
        make_claim("claim-a", "量化会改变短线反馈速度。", tag="量化影响"),
        make_claim("claim-b", "弱市先收缩仓位。", tag="风控"),
    ]
    needs_edit = [
        make_claim(
            "claim-c",
            "像牛市又不像牛市，先别急。",
            tag="牛熊切换",
            review_status="needs_edit",
            review_notes="待确认",
        )
    ]
    rejected = [
        make_claim(
            "claim-d",
            "今天市场一般。",
            tag="指数环境",
            review_status="rejected",
            review_notes="拒绝：表述偏泛，不能独立构成方法论。",
        )
    ]
    rules = build_methodology_rules(accepted, max_rules_per_theme=2)

    path = build_methodology_profile_v0(
        accepted,
        needs_edit,
        rejected,
        rules,
        tmp_path,
        reviewed_packs=["quant_impact_top100"],
        unreviewed_count=10,
        max_claims_per_theme=1,
        max_rules_per_theme=2,
    )

    text = path.read_text(encoding="utf-8")
    assert "accepted claims: 2" in text
    assert "needs_edit claims: 1" in text
    assert "reviewed packs: quant_impact_top100" in text
    assert "Rule Summary" in text
    assert "Representative Accepted Evidence" in text
    assert "Needs-edit / Caveats" in text
    assert "泛句、碎句、反讽、上下文不足不进入核心方法论" in text
