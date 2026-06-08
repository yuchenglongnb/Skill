# Review Encoding Audit

## Summary
- total_files: 13
- corrupted_files: 0
- total_reviewed_items: 1393
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0

## Files

### data/processed/tgb/review_packs/accepted_recheck_v0_2.yaml

- exists: True
- total_items: 55
- reviewed_items: 55
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/review_packs/bull_bear_top80.yaml

- exists: True
- total_items: 80
- reviewed_items: 80
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/review_packs/digitization_top80.yaml

- exists: True
- total_items: 8
- reviewed_items: 0
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/review_packs/execution_rule_top100.yaml

- exists: True
- total_items: 100
- reviewed_items: 0
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/review_packs/index_environment_top100.yaml

- exists: True
- total_items: 100
- reviewed_items: 0
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/review_packs/quant_impact_top100.yaml

- exists: True
- total_items: 100
- reviewed_items: 100
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/review_packs/risk_control_top80.yaml

- exists: True
- total_items: 80
- reviewed_items: 80
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/review_packs/short_term_base_top100.yaml

- exists: True
- total_items: 100
- reviewed_items: 100
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/review_packs/turnover_top100.yaml

- exists: True
- total_items: 100
- reviewed_items: 100
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/review_ready_decisions.yaml

- exists: True
- total_items: 6552
- reviewed_items: 439
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/accepted_review_ready_claims.jsonl

- exists: True
- total_items: 222
- reviewed_items: 222
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/rejected_review_ready_claims.jsonl

- exists: True
- total_items: 95
- reviewed_items: 95
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

### data/processed/tgb/needs_edit_review_ready_claims.jsonl

- exists: True
- total_items: 122
- reviewed_items: 122
- corrupted_review_notes_count: 0
- corrupted_edited_claim_text_count: 0
- sample_claim_ids: []

## Repair Guidance

- Ensure YAML writes use UTF-8 with `allow_unicode=True`.
- Ensure JSONL writes use UTF-8 with `ensure_ascii=False`.
- If corruption is found, rebuild `review_notes` or `edited_claim_text` from a trusted source before applying review outputs.
