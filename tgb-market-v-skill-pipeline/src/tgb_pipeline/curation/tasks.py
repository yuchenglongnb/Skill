"""Task orchestration for reviewed claim curation."""

from __future__ import annotations

from pathlib import Path

from tgb_pipeline.curation.apply_review import apply_review_decisions
from tgb_pipeline.curation.decisions import load_review_decisions, write_review_decision_template
from tgb_pipeline.curation.profile import build_curated_methodology_profile
from tgb_pipeline.curation.report import build_claim_curation_report
from tgb_pipeline.curation.review_ready_apply import apply_review_ready_decisions
from tgb_pipeline.curation.review_ready_decisions import (
    load_review_ready_decisions,
    sync_review_ready_decisions,
    write_review_ready_decision_template,
)
from tgb_pipeline.curation.review_ready_profile import build_review_ready_curated_profile
from tgb_pipeline.curation.review_ready_report import build_review_ready_curation_report
from tgb_pipeline.export.manifest import build_corpus_manifest
from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def review_claims_bundle(
    raw_dir: Path,
    processed_dir: Path,
    reports_dir: Path,
    *,
    decisions_path: Path,
    overwrite_review_template: bool = False,
    include_unreviewed: bool = False,
    apply: bool = False,
) -> list[Path]:
    claims_path = processed_dir / "methodology_claims.jsonl"
    if not claims_path.exists():
        raise ValueError("methodology_claims.jsonl not found; run extract-claims first.")

    claims = JSONLStore(claims_path, MethodologyClaim, "claim_id").read_all()
    template_path = write_review_decision_template(
        claims,
        decisions_path,
        overwrite=overwrite_review_template,
        generated_from=_relative(claims_path),
    )
    if not apply:
        return [template_path]

    decisions = load_review_decisions(decisions_path)
    accepted, rejected, needs_edit = apply_review_decisions(
        claims,
        decisions,
        include_unreviewed=include_unreviewed,
    )
    accepted_path = processed_dir / "accepted_methodology_claims.jsonl"
    rejected_path = processed_dir / "rejected_methodology_claims.jsonl"
    needs_edit_path = processed_dir / "needs_edit_methodology_claims.jsonl"
    JSONLStore(accepted_path, MethodologyClaim, "claim_id").rewrite_all(accepted)
    JSONLStore(rejected_path, MethodologyClaim, "claim_id").rewrite_all(rejected)
    JSONLStore(needs_edit_path, MethodologyClaim, "claim_id").rewrite_all(needs_edit)
    curated_profile_path = build_curated_methodology_profile(accepted, needs_edit, reports_dir)
    curation_report_path = build_claim_curation_report(
        claims,
        accepted,
        rejected,
        needs_edit,
        reports_dir,
    )
    manifest_path = build_corpus_manifest(raw_dir, processed_dir, reports_dir)
    return [
        template_path,
        accepted_path,
        rejected_path,
        needs_edit_path,
        curated_profile_path,
        curation_report_path,
        manifest_path,
    ]


def review_ready_claims_bundle(
    raw_dir: Path,
    processed_dir: Path,
    reports_dir: Path,
    *,
    decisions_path: Path,
    overwrite_template: bool = False,
    include_unreviewed: bool = False,
    sync: bool = False,
    apply: bool = False,
) -> list[Path]:
    claims_path = processed_dir / "review_ready_claims.jsonl"
    if not claims_path.exists():
        raise ValueError("review_ready_claims.jsonl not found; run build-review-ready-claims first.")

    claims = JSONLStore(claims_path, MethodologyClaim, "claim_id").read_all()
    outputs: list[Path] = []
    if not decisions_path.exists():
        outputs.append(
            write_review_ready_decision_template(
                claims,
                decisions_path,
                overwrite=overwrite_template,
                generated_from=_relative(claims_path),
            )
        )
    elif sync:
        sync_review_ready_decisions(claims_path, decisions_path)
        outputs.append(decisions_path)
    else:
        outputs.append(
            write_review_ready_decision_template(
                claims,
                decisions_path,
                overwrite=overwrite_template,
                generated_from=_relative(claims_path),
            )
        )

    if not apply:
        return outputs

    decisions = load_review_ready_decisions(decisions_path)
    accepted, rejected, needs_edit = apply_review_ready_decisions(
        claims,
        decisions,
        include_unreviewed=include_unreviewed,
    )
    accepted_path = processed_dir / "accepted_review_ready_claims.jsonl"
    rejected_path = processed_dir / "rejected_review_ready_claims.jsonl"
    needs_edit_path = processed_dir / "needs_edit_review_ready_claims.jsonl"
    JSONLStore(accepted_path, MethodologyClaim, "claim_id").rewrite_all(accepted)
    JSONLStore(rejected_path, MethodologyClaim, "claim_id").rewrite_all(rejected)
    JSONLStore(needs_edit_path, MethodologyClaim, "claim_id").rewrite_all(needs_edit)
    curated_profile_path = build_review_ready_curated_profile(accepted, needs_edit, reports_dir)
    curation_report_path = build_review_ready_curation_report(
        claims,
        accepted,
        rejected,
        needs_edit,
        reports_dir,
    )
    manifest_path = build_corpus_manifest(raw_dir, processed_dir, reports_dir)
    return [
        *outputs,
        accepted_path,
        rejected_path,
        needs_edit_path,
        curated_profile_path,
        curation_report_path,
        manifest_path,
    ]


def _relative(path: Path) -> str:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    try:
        return resolved.relative_to(cwd).as_posix()
    except ValueError:
        return path.as_posix()
