# Package Audit

## Summary
- files: 12
- rules: 16
- evidence mappings: 74
- warnings: 0

## Checks

| check | status | details |
| --- | --- | --- |
| SKILL.md | ok | required file SKILL.md |
| README.md | ok | required file README.md |
| MANIFEST.json | ok | required file MANIFEST.json |
| methodology_rules.jsonl | ok | required file methodology_rules.jsonl |
| rule_evidence_map.jsonl | ok | required file rule_evidence_map.jsonl |
| uncertainty_policy.md | ok | required file uncertainty_policy.md |
| review_summary.md | ok | required file review_summary.md |
| skill_quality_report.md | ok | required file skill_quality_report.md |
| rules_count | ok | 16 rules |
| evidence_map_count | ok | 74 evidence mappings |
| raw_excerpt_in_skill | ok | overlap_count=0 |
| investment_advice_language | ok | hits=[] |
| excluded_artifacts | ok | forbidden_paths=[] |
| encoding | ok | corrupted_files=0 |
| manifest_has_source_commit | ok | source_commit=97c6ca8221be1b7ef3a76ee2240e0b308c125e07 |
| manifest_has_package_build_commit | ok | package_build_commit=97c6ca8221be1b7ef3a76ee2240e0b308c125e07 |
| manifest_has_generated_from | ok | generated_from=dict |
| manifest_has_review_state | ok | review_state_keys=['accepted_claims', 'needs_edit_claims', 'rejected_claims', 'unreviewed_claims'] |
| manifest_counts_match_current_package | ok | accepted/needs_edit/rejected/unreviewed/rules counts match current package |
| manifest_quality_matches_quality_report | ok | quality counters match skill_quality_report.md |
| manifest_rules_count | ok | manifest=16 actual=16 |
| manifest_accepted_count | ok | manifest=222 summary=222 |
| manifest_needs_edit_count | ok | manifest=122 summary=122 |
| manifest_review_state_counts | ok | review_state={'accepted_claims': 222, 'needs_edit_claims': 122, 'rejected_claims': 95, 'unreviewed_claims': 6113} |
| manifest_quality_direct_excerpt | ok | manifest=0 quality=0 |
| manifest_quality_warnings | ok | manifest=0 quality=0 |

## Boundaries
- package excludes raw crawl data
- package excludes review decision files
- package excludes HTML snapshots
- package uses accepted claims only for core rules
- package keeps needs_edit as uncertain evidence only

## Traceability Notes
- `source_commit` identifies the pipeline commit associated with the skill output used as package source.
- `package_build_commit` identifies the current pipeline commit when `package-skill-v0` was executed.
- `package_commit` remains null inside the package and can be filled only after the package itself is committed elsewhere.
