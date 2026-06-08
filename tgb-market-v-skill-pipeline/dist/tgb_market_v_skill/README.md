# TGB Market V Skill

This is a packaged Skill v0.2 generated from reviewed methodology claims.

## What this skill does

- Summarizes the target author's reviewed market methodology.
- Helps analyze future posts/comments from the same author.
- Provides rule-level themes and evidence claim IDs.

## What this skill does not do

- It does not provide investment advice.
- It does not predict stock prices.
- It does not generate buy/sell recommendations.
- It does not treat sarcasm or jokes as literal methodology.

## Files

- `SKILL.md`: main skill instructions.
- `methodology_rules.jsonl`: abstract rules.
- `rule_evidence_map.jsonl`: evidence mapping for accepted claims.
- `uncertainty_policy.md`: uncertainty and sarcasm handling.
- `review_summary.md`: review status and corpus coverage.
- `skill_quality_report.md`: package quality report.

## Evidence Policy

Core rules come from accepted claims only.
Needs-edit claims are uncertain and must be manually checked.
Rejected and unreviewed claims are excluded from core methodology.

## Current Coverage

- accepted claims: 248
- rules: 16
- reviewed packs: quant_impact_top100, turnover_top100, short_term_base_top100, risk_control_top80, bull_bear_top80
- known gaps: 4
