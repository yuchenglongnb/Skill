"""Task orchestration for building a rule-based Skill v0.1 draft."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.export.manifest import build_corpus_manifest
from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.skill.evidence_index import (
    build_needs_edit_evidence_index,
    build_rule_evidence_map,
    build_skill_evidence_index,
)
from tgb_pipeline.skill.profile_builder import build_methodology_profile_v0
from tgb_pipeline.skill.rule_builder import build_methodology_rules
from tgb_pipeline.skill.rule_writer import (
    write_methodology_rules,
    write_needs_edit_worklist,
    write_skill_quality_report,
)
from tgb_pipeline.skill.skill_audit import audit_skill_outputs
from tgb_pipeline.skill.skill_writer import (
    write_review_summary,
    write_skill_markdown,
    write_uncertainty_policy,
)
from tgb_pipeline.storage import JSONLStore


def build_skill_v0_bundle(
    raw_dir: Path,
    processed_dir: Path,
    reports_dir: Path,
    *,
    output_dir: Path,
    include_needs_edit_index: bool = False,
    include_needs_edit_worklist: bool = False,
    max_claims_per_theme: int = 5,
    max_rules_per_theme: int = 8,
    max_evidence_per_rule: int = 5,
    rule_mode: bool = False,
) -> list[Path]:
    accepted_claims = _read_claims(processed_dir / "accepted_review_ready_claims.jsonl")
    if not accepted_claims:
        raise ValueError(
            "accepted_review_ready_claims.jsonl not found or empty; apply reviewed packs first."
        )
    needs_edit_claims = _read_claims(processed_dir / "needs_edit_review_ready_claims.jsonl")
    rejected_claims = _read_claims(processed_dir / "rejected_review_ready_claims.jsonl")
    review_ready_claims = _read_claims(processed_dir / "review_ready_claims.jsonl")
    accepted_claim_ids = {claim.claim_id for claim in accepted_claims}
    needs_edit_claim_ids = {claim.claim_id for claim in needs_edit_claims}
    rejected_claim_ids = {claim.claim_id for claim in rejected_claims}
    reviewed_claim_ids = accepted_claim_ids | needs_edit_claim_ids | rejected_claim_ids
    unreviewed_claim_ids = {
        claim.claim_id for claim in review_ready_claims if claim.claim_id not in reviewed_claim_ids
    }
    unreviewed_count = len(unreviewed_claim_ids)
    reviewed_packs = _discover_reviewed_packs(reports_dir / "review_packs")

    rules = build_methodology_rules(
        accepted_claims,
        max_rules_per_theme=max_rules_per_theme,
        max_evidence_per_rule=max_evidence_per_rule,
    )

    methodology_profile_path = build_methodology_profile_v0(
        accepted_claims,
        needs_edit_claims,
        rejected_claims,
        rules,
        output_dir,
        reviewed_packs=reviewed_packs,
        unreviewed_count=unreviewed_count,
        max_claims_per_theme=max_claims_per_theme,
        max_rules_per_theme=max_rules_per_theme,
    )
    skill_md_path = write_skill_markdown(rules, output_dir)
    evidence_index_path = build_skill_evidence_index(accepted_claims, output_dir)
    rule_path = write_methodology_rules(rules, output_dir)
    rule_evidence_map_path = build_rule_evidence_map(rules, accepted_claims, output_dir)
    uncertainty_policy_path = write_uncertainty_policy(output_dir)
    review_summary_path = write_review_summary(
        accepted_claims,
        needs_edit_claims,
        rejected_claims,
        rules,
        output_dir,
        reviewed_packs=reviewed_packs,
        unreviewed_count=unreviewed_count,
    )

    outputs = [
        skill_md_path,
        methodology_profile_path,
        evidence_index_path,
        uncertainty_policy_path,
        review_summary_path,
        rule_path,
        rule_evidence_map_path,
    ]
    if include_needs_edit_index:
        outputs.append(build_needs_edit_evidence_index(needs_edit_claims, output_dir))
    if include_needs_edit_worklist or rule_mode:
        outputs.append(write_needs_edit_worklist(needs_edit_claims, output_dir))

    audit_summary = audit_skill_outputs(
        output_dir,
        rules=rules,
        accepted_claim_ids=accepted_claim_ids,
        needs_edit_claim_ids=needs_edit_claim_ids,
        rejected_claim_ids=rejected_claim_ids,
        unreviewed_claim_ids=unreviewed_claim_ids,
        accepted_claims_count=len(accepted_claims),
        needs_edit_claims_count=len(needs_edit_claims),
        rejected_claims_count=len(rejected_claims),
        unreviewed_claims_count=unreviewed_count,
    )
    outputs.append(write_skill_quality_report(audit_summary, output_dir))
    outputs.append(build_corpus_manifest(raw_dir, processed_dir, reports_dir))
    return outputs


def _read_claims(path: Path) -> list[MethodologyClaim]:
    if not path.exists():
        return []
    return JSONLStore(path, MethodologyClaim, "claim_id").read_all()


def _discover_reviewed_packs(review_pack_reports_dir: Path) -> list[str]:
    if not review_pack_reports_dir.exists():
        return []
    names = []
    for path in sorted(review_pack_reports_dir.glob("*_apply_report.md")):
        pack_name = path.stem.removesuffix("_apply_report")
        if pack_name.startswith("mock_") or pack_name.startswith("mock"):
            continue
        names.append(pack_name)
    preferred_order = [
        "quant_impact_top100",
        "turnover_top100",
        "short_term_base_top100",
        "risk_control_top80",
        "bull_bear_top80",
    ]
    ordered = [name for name in preferred_order if name in names]
    ordered.extend(name for name in names if name not in ordered)
    return ordered
