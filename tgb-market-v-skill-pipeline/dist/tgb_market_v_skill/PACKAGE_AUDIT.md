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
| manifest_rules_count | ok | manifest=16 actual=16 |
| manifest_accepted_count | ok | manifest=222 summary=222 |
| manifest_needs_edit_count | ok | manifest=122 summary=122 |
| manifest_quality_direct_excerpt | ok | manifest=0 quality=0 |
| manifest_quality_warnings | ok | manifest=0 quality=0 |

## Boundaries
- package excludes raw crawl data
- package excludes review decision files
- package excludes HTML snapshots
- package uses accepted claims only for core rules
- package keeps needs_edit as uncertain evidence only
