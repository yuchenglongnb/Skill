from tgb_pipeline.models import MethodologyRule
from tgb_pipeline.skill.skill_audit import audit_skill_outputs
from tgb_pipeline.skill.skill_writer import write_skill_markdown, write_uncertainty_policy, write_review_summary
from tests.skill_fixture_data import make_claim


def test_skill_audit_flags_direct_excerpt_in_rule_text(tmp_path) -> None:
    accepted = [
        make_claim("claim-a", "量化会改变短线盘中的反馈速度，并重塑追涨和抛压的时间结构。", tag="量化影响"),
        make_claim("claim-b", "量化趋同交易会改变流动性分布，并影响盘中承接和回封节奏。", tag="量化影响"),
    ]
    bad_rule = MethodologyRule(
        rule_id="quant-impact-bad",
        theme="量化影响",
        title="量化影响需要纳入短线市场结构判断",
        rule_text="量化会改变短线盘中的反馈速度，并重塑追涨和抛压的时间结构。",
        evidence_claim_ids=["claim-a", "claim-b"],
        evidence_article_ids=["a1"],
    )
    write_skill_markdown([bad_rule], tmp_path)
    write_uncertainty_policy(tmp_path)
    write_review_summary(accepted, [], [], [bad_rule], tmp_path, reviewed_packs=["quant_impact_top100"], unreviewed_count=0)
    (tmp_path / "methodology_profile.md").write_text("# profile\n", encoding="utf-8")
    (tmp_path / "methodology_rules.jsonl").write_text('{"rule_id":"r1"}\n', encoding="utf-8")
    (tmp_path / "rule_evidence_map.jsonl").write_text('{"claim_id":"claim-a"}\n', encoding="utf-8")

    summary = audit_skill_outputs(
        tmp_path,
        rules=[bad_rule],
        accepted_claims=accepted,
        accepted_claim_ids={"claim-a", "claim-b"},
        needs_edit_claim_ids=set(),
        rejected_claim_ids=set(),
        unreviewed_claim_ids=set(),
        accepted_claims_count=2,
        needs_edit_claims_count=0,
        rejected_claims_count=0,
        unreviewed_claims_count=0,
    )

    assert summary["rule_abstraction_checks"]["direct_excerpt_in_rule_text"] > 0
