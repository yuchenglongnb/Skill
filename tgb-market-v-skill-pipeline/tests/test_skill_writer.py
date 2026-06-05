from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tgb_pipeline.skill.skill_writer import (
    write_review_summary,
    write_skill_markdown,
    write_uncertainty_policy,
)
from tests.skill_fixture_data import make_claim


def test_skill_writer_outputs_scope_uncertainty_and_rules(tmp_path) -> None:
    accepted = [
        make_claim("claim-a", "量化会改变短线反馈速度。", tag="量化影响"),
        make_claim("claim-b", "弱市要先收缩仓位。", tag="风控"),
    ]
    needs_edit = [
        make_claim(
            "claim-c",
            "像牛市又不像牛市。",
            tag="牛熊切换",
            review_status="needs_edit",
        )
    ]
    rejected = [
        make_claim(
            "claim-d",
            "今天市场一般。",
            tag="指数环境",
            review_status="rejected",
        )
    ]
    rules = build_methodology_rules(accepted, max_rules_per_theme=2)

    skill_path = write_skill_markdown(rules, tmp_path)
    uncertainty_path = write_uncertainty_policy(tmp_path)
    summary_path = write_review_summary(
        accepted,
        needs_edit,
        rejected,
        rules,
        tmp_path,
        reviewed_packs=["quant_impact_top100"],
        unreviewed_count=10,
    )

    skill_text = skill_path.read_text(encoding="utf-8")
    uncertainty_text = uncertainty_path.read_text(encoding="utf-8")
    summary_text = summary_path.read_text(encoding="utf-8")

    assert "不用于生成具体买卖建议" in skill_text
    assert "Core Methodology Rules" in skill_text
    assert "Rule quant-impact-overview" in skill_text
    assert "Sarcasm / Joke / Deliberate Misstatement" in uncertainty_text
    assert "do not automatically invert it" in uncertainty_text
    assert "quant_impact_top100" in summary_text
    assert "execution_rule_top100" in summary_text
