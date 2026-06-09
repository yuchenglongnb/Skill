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
- `evidence_index.jsonl`: accepted evidence index for traceability.
- `needs_edit_evidence_index.jsonl`: uncertain evidence that still requires manual confirmation.
- `needs_edit_worklist.md`: recheck worklist; not part of core methodology rules.

## Evidence Policy

Core rules come from accepted claims only.
Needs-edit claims are uncertain and must be manually checked.
Rejected and unreviewed claims are excluded from core methodology.
The `needs_edit_*` files are included only as uncertain review material and must not be treated as core rules.

## Current Coverage

- accepted claims: 222
- rules: 16
- reviewed packs: quant_impact_top100, turnover_top100, short_term_base_top100, risk_control_top80, bull_bear_top80, accepted_recheck_v0_2
- known gaps: 4
