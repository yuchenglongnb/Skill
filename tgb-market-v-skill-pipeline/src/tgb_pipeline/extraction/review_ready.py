"""Build review-ready claim subsets from the full candidate pool."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from tgb_pipeline.extraction.ranking import rank_claim_for_review
from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.storage import JSONLStore


def build_review_ready_claims(
    processed_dir: Path,
    reports_dir: Path,
    *,
    max_per_tag: int = 500,
    include_normal: bool = True,
) -> tuple[Path, Path]:
    claims = _read_claims(processed_dir)
    ranked_claims = [rank_claim_for_review(claim) for claim in claims]

    review_ready: list[MethodologyClaim] = []
    low_priority: list[MethodologyClaim] = []
    per_tag_counts: Counter[str] = Counter()
    seen_normalized: set[str] = set()

    for claim in _sorted_for_review(ranked_claims):
        normalized = _normalize_excerpt(claim.raw_excerpt)
        if claim.review_priority == "low":
            low_priority.append(claim)
            continue
        if normalized in seen_normalized:
            low_priority.append(_demote_duplicate(claim))
            continue
        if claim.review_priority == "normal" and not include_normal:
            low_priority.append(_demote_for_bucket(claim, "background_context"))
            continue
        if claim.review_priority == "normal" and not _within_tag_cap(claim, per_tag_counts, max_per_tag):
            low_priority.append(_demote_for_bucket(claim, "background_context"))
            continue

        review_ready.append(claim)
        seen_normalized.add(normalized)
        for tag in claim.method_tags:
            per_tag_counts[tag] += 1

    review_ready_path = processed_dir / "review_ready_claims.jsonl"
    low_priority_path = processed_dir / "low_priority_methodology_claims.jsonl"
    JSONLStore(review_ready_path, MethodologyClaim, "claim_id").rewrite_all(review_ready)
    JSONLStore(low_priority_path, MethodologyClaim, "claim_id").rewrite_all(low_priority)
    return review_ready_path, low_priority_path


def _read_claims(processed_dir: Path) -> list[MethodologyClaim]:
    path = processed_dir / "methodology_claims.jsonl"
    if not path.exists():
        return []
    return JSONLStore(path, MethodologyClaim, "claim_id").read_all()


def _sorted_for_review(claims: list[MethodologyClaim]) -> list[MethodologyClaim]:
    priority_order = {"high": 0, "normal": 1, "low": 2}
    source_order = {"article": 0, "comment": 1, "interaction": 2, "image_ocr": 3}

    def ranking_score(claim: MethodologyClaim) -> int:
        ranking = (claim.raw or {}).get("ranking") or {}
        return int(ranking.get("score", 0))

    return sorted(
        claims,
        key=lambda claim: (
            priority_order.get(claim.review_priority, 9),
            source_order.get(claim.source_type.value, 9),
            -ranking_score(claim),
            claim.claim_id,
        ),
    )


def _within_tag_cap(claim: MethodologyClaim, per_tag_counts: Counter[str], max_per_tag: int) -> bool:
    if not claim.method_tags:
        return True
    return any(per_tag_counts[tag] < max_per_tag for tag in claim.method_tags)


def _normalize_excerpt(text: str) -> str:
    return "".join(str(text).split()).casefold()


def _demote_duplicate(claim: MethodologyClaim) -> MethodologyClaim:
    updated_raw = dict(claim.raw)
    ranking = dict((updated_raw.get("ranking") or {}))
    ranking["reason"] = f"{ranking.get('reason', '')}, duplicate_excerpt".strip(", ")
    updated_raw["ranking"] = ranking
    return _copy_claim(claim, review_priority="low", review_bucket="background_context", raw=updated_raw)


def _demote_for_bucket(claim: MethodologyClaim, bucket: str) -> MethodologyClaim:
    updated_raw = dict(claim.raw)
    ranking = dict((updated_raw.get("ranking") or {}))
    ranking["reason"] = f"{ranking.get('reason', '')}, capped_or_excluded".strip(", ")
    updated_raw["ranking"] = ranking
    return _copy_claim(claim, review_priority="low", review_bucket=bucket, raw=updated_raw)


def _copy_claim(claim: MethodologyClaim, **updates) -> MethodologyClaim:
    if hasattr(claim, "model_copy"):
        return claim.model_copy(update=updates, deep=True)
    return claim.copy(update=updates, deep=True)
