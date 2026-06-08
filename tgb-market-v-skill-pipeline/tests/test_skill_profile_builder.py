from tgb_pipeline.skill.profile_builder import build_methodology_profile_v0
from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tests.skill_fixture_data import make_claim


def test_build_methodology_profile_v0_shows_rules_evidence_and_recheck(tmp_path) -> None:
    accepted = [
        make_claim("claim-a", "量化会改变短线盘中的反馈速度。", tag="量化影响", review_bucket="trading_mechanism"),
        make_claim("claim-b", "量化趋同交易会改变流动性分布。", tag="量化影响", review_bucket="market_environment"),
    ]
    needs_edit = [
        make_claim(
            "claim-c",
            "像牛市又不像牛市，先别激动。",
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
    rules = build_methodology_rules(accepted, max_rules_per_theme=4)

    path = build_methodology_profile_v0(
        accepted,
        needs_edit,
        rejected,
        rules,
        tmp_path,
        reviewed_packs=["quant_impact_top100"],
        unreviewed_count=10,
        accepted_recheck_candidates=[
            {
                "claim_id": "claim-z",
                "theme": "量化影响",
                "article_id": "a1",
                "source_type": "comment",
                "raw_excerpt": "低纬战高维，我们都是虫子。",
                "review_notes": "需要回看",
                "recheck_reason": ["colloquial_or_exaggerated"],
            }
        ],
        max_claims_per_theme=1,
        max_rules_per_theme=2,
    )

    text = path.read_text(encoding="utf-8")
    assert "accepted claims: 2" in text
    assert "reviewed packs: quant_impact_top100" in text
    assert "## Rule Summary" in text
    assert "## Representative Accepted Evidence" in text
    assert "## Accepted Claims Recheck Candidates" in text
    assert "## Needs-edit Worklist" in text
    assert "泛句、碎句、反讽、上下文不足不进入核心方法论" in text
