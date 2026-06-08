from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tgb_pipeline.skill.skill_writer import (
    write_review_summary,
    write_skill_markdown,
    write_uncertainty_policy,
)
from tests.skill_fixture_data import make_claim


def test_skill_writer_outputs_abstract_rules_without_raw_excerpt(tmp_path) -> None:
    accepted = [
        make_claim("claim-a", "量化会改变短线盘中的反馈速度。", tag="量化影响", review_bucket="trading_mechanism"),
        make_claim("claim-b", "量化趋同交易会改变流动性分布。", tag="量化影响", review_bucket="market_environment"),
        make_claim("claim-c", "弱市要先收缩仓位。", tag="风控", review_bucket="risk_control"),
        make_claim("claim-d", "买入前提不成立时先减少交易。", tag="风控", review_bucket="execution_rule"),
    ]
    needs_edit = [
        make_claim(
            "claim-e",
            "像牛市又不像牛市。",
            tag="牛熊切换",
            review_status="needs_edit",
        )
    ]
    rejected = [
        make_claim(
            "claim-f",
            "今天市场一般。",
            tag="指数环境",
            review_status="rejected",
        )
    ]
    rules = build_methodology_rules(accepted, max_rules_per_theme=4)

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
        accepted_recheck_count=2,
    )

    skill_text = skill_path.read_text(encoding="utf-8")
    uncertainty_text = uncertainty_path.read_text(encoding="utf-8")
    summary_text = summary_path.read_text(encoding="utf-8")

    assert "不用于生成具体买卖建议" in skill_text
    assert "Core Methodology Rules" in skill_text
    assert "Rule quant-impact-" in skill_text
    assert "量化会改变短线盘中的反馈速度。" not in skill_text
    assert "Sarcasm / Joke / Deliberate Misstatement" in uncertainty_text
    assert "do not automatically invert it" in uncertainty_text
    assert "quant_impact_top100" in summary_text
    assert "accepted_recheck_candidates: 2" in summary_text
