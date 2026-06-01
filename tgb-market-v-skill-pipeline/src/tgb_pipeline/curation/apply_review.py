"""Apply review decisions to candidate methodology claims."""

from __future__ import annotations

from copy import deepcopy

from tgb_pipeline.models import MethodologyClaim


def apply_review_decisions(
    claims: list[MethodologyClaim],
    decisions: dict,
    *,
    include_unreviewed: bool = False,
) -> tuple[list[MethodologyClaim], list[MethodologyClaim], list[MethodologyClaim]]:
    decisions_map = decisions.get("decisions", {}) if isinstance(decisions, dict) else {}
    accepted: list[MethodologyClaim] = []
    rejected: list[MethodologyClaim] = []
    needs_edit: list[MethodologyClaim] = []

    for claim in claims:
        review = decisions_map.get(claim.claim_id, {})
        decision = review.get("decision", "unreviewed")
        reason = review.get("reason")
        review_notes = review.get("review_notes")
        edited_claim_text = review.get("edited_claim_text")

        updated = claim.copy(deep=True)
        updated.raw = deepcopy(updated.raw)
        updated.raw["review_decision"] = decision
        updated.raw["review_reason"] = reason
        updated.raw["review_notes"] = review_notes
        updated.review_notes = review_notes

        if decision == "accepted":
            updated.review_status = "accepted"
            accepted.append(updated)
            continue
        if decision == "needs_edit":
            if edited_claim_text:
                updated.raw["edited_from_claim_text"] = updated.claim_text
                updated.claim_text = edited_claim_text
                updated.review_status = "accepted_with_edit"
            else:
                updated.review_status = "needs_edit"
            needs_edit.append(updated)
            continue
        if decision == "rejected":
            updated.review_status = "rejected"
            rejected.append(updated)
            continue
        if include_unreviewed:
            updated.review_status = "unreviewed"
            needs_edit.append(updated)

    return accepted, rejected, needs_edit

