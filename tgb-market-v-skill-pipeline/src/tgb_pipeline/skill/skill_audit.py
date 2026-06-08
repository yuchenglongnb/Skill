"""Audit rule-mode skill outputs for evidence integrity and abstraction boundaries."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re

from tgb_pipeline.audit.text_encoding_audit import audit_text_encoding_paths
from tgb_pipeline.models import MethodologyClaim, MethodologyRule

BANNED_INVESTMENT_PHRASES = [
    "推荐买入",
    "必涨",
    "稳赚",
    "满仓买",
    "直接买",
    "无脑买",
    "必跌",
]

WARN_ONLY_BUY_SELL_PHRASES = [
    "买入",
    "卖出",
]

ALLOWED_DESCRIPTIVE_PHRASES = [
    "买入触发",
    "买入前提",
    "买入前提不成立",
    "卖出条件",
    "买入/卖出节奏",
]

NEGATED_ADVICE_PATTERNS = [
    re.compile(r"避免直接买卖建议"),
    re.compile(r"不输出买卖建议"),
    re.compile(r"不用于生成具体买卖建议"),
]

GENERIC_TITLE_RE = re.compile(r"(规则\s*\d+|Rule\s+\d+)", re.IGNORECASE)


def audit_skill_outputs(
    output_dir: Path,
    *,
    rules: list[MethodologyRule],
    accepted_claims: list[MethodologyClaim],
    accepted_claim_ids: set[str],
    needs_edit_claim_ids: set[str],
    rejected_claim_ids: set[str],
    unreviewed_claim_ids: set[str],
    accepted_claims_count: int,
    needs_edit_claims_count: int,
    rejected_claims_count: int,
    unreviewed_claims_count: int,
    accepted_recheck_candidates_count: int = 0,
) -> dict:
    skill_md_path = output_dir / "SKILL.md"
    rules_path = output_dir / "methodology_rules.jsonl"
    evidence_map_path = output_dir / "rule_evidence_map.jsonl"
    files_to_scan = [
        skill_md_path,
        output_dir / "methodology_profile.md",
        rules_path,
        evidence_map_path,
        output_dir / "review_summary.md",
        output_dir / "uncertainty_policy.md",
    ]
    if (output_dir / "needs_edit_worklist.md").exists():
        files_to_scan.append(output_dir / "needs_edit_worklist.md")
    text_audit = audit_text_encoding_paths([path for path in files_to_scan if path.exists()])

    warnings: list[str] = []
    if not skill_md_path.exists():
        warnings.append("SKILL.md missing.")
    if not rules_path.exists():
        warnings.append("methodology_rules.jsonl missing.")
    if not evidence_map_path.exists():
        warnings.append("rule_evidence_map.jsonl missing.")

    rule_coverage_by_theme: dict[str, dict[str, int]] = defaultdict(lambda: {"rules": 0, "evidence_claims": 0})
    evidence_density: dict[str, int] = {}

    direct_excerpt_count = 0
    generic_rule_title_count = 0
    insufficient_evidence_count = 0

    accepted_excerpt_map = {
        claim.claim_id: _normalized_fragments(claim)
        for claim in accepted_claims
    }

    for rule in rules:
        evidence_density[rule.rule_id] = len(rule.evidence_claim_ids)
        rule_coverage_by_theme[rule.theme]["rules"] += 1
        rule_coverage_by_theme[rule.theme]["evidence_claims"] += len(rule.evidence_claim_ids)
        if not rule.evidence_claim_ids:
            warnings.append(f"rule without evidence: {rule.rule_id}")
        if len(rule.evidence_claim_ids) < 2:
            insufficient_evidence_count += 1
            warnings.append(f"insufficient_evidence: {rule.rule_id}")
        if GENERIC_TITLE_RE.search(rule.title):
            generic_rule_title_count += 1
            warnings.append(f"generic rule title: {rule.rule_id}")

        rule_text_normalized = _normalize_text(rule.rule_text)
        if rule_text_normalized:
            for claim_id in rule.evidence_claim_ids:
                claim = accepted_excerpt_map.get(claim_id)
                if claim and _has_overlap(rule_text_normalized, claim):
                    direct_excerpt_count += 1
                    warnings.append(f"direct excerpt in rule_text: {rule.rule_id} -> {claim_id}")
                    break

        for claim_id in rule.evidence_claim_ids:
            if claim_id not in accepted_claim_ids:
                warnings.append(f"non-accepted evidence in rules: {rule.rule_id} -> {claim_id}")
            if claim_id in needs_edit_claim_ids:
                warnings.append(f"needs_edit mixed into rules: {rule.rule_id} -> {claim_id}")
            if claim_id in rejected_claim_ids:
                warnings.append(f"rejected mixed into rules: {rule.rule_id} -> {claim_id}")
            if claim_id in unreviewed_claim_ids:
                warnings.append(f"unreviewed mixed into rules: {rule.rule_id} -> {claim_id}")

    raw_excerpt_in_skill_md_count = 0
    if skill_md_path.exists():
        skill_text = skill_md_path.read_text(encoding="utf-8")
        skill_text_normalized = _normalize_text(skill_text)
        for phrase in BANNED_INVESTMENT_PHRASES:
            if phrase in skill_text and not _is_negated_advice_context(skill_text, phrase):
                warnings.append(f"possible investment-advice wording: {phrase}")
        for phrase in WARN_ONLY_BUY_SELL_PHRASES:
            if (
                phrase in skill_text
                and not any(allowed in skill_text for allowed in ALLOWED_DESCRIPTIVE_PHRASES)
                and not _is_negated_advice_context(skill_text, phrase)
            ):
                warnings.append(f"buy/sell wording needs manual review: {phrase}")
        for claim in accepted_claims:
            if _has_overlap(skill_text_normalized, accepted_excerpt_map[claim.claim_id]):
                raw_excerpt_in_skill_md_count += 1
                warnings.append(f"raw excerpt in SKILL.md: {claim.claim_id}")
                break

    if text_audit["corrupted_files"] > 0:
        warnings.append("mojibake / corrupted text detected in skill outputs")

    return {
        "accepted_claims": accepted_claims_count,
        "generated_rules": len(rules),
        "needs_edit_claims": needs_edit_claims_count,
        "rejected_claims": rejected_claims_count,
        "unreviewed_claims": unreviewed_claims_count,
        "rule_coverage_by_theme": dict(rule_coverage_by_theme),
        "evidence_density": evidence_density,
        "rule_abstraction_checks": {
            "direct_excerpt_in_rule_text": direct_excerpt_count,
            "generic_rule_titles": generic_rule_title_count,
            "raw_excerpt_in_skill_md": raw_excerpt_in_skill_md_count,
            "accepted_recheck_candidates": accepted_recheck_candidates_count,
            "insufficient_evidence": insufficient_evidence_count,
        },
        "warnings": warnings,
        "text_audit": text_audit,
    }


def _normalize_text(text: str | None) -> str:
    return "".join(str(text or "").split())


def _normalized_fragments(claim: MethodologyClaim) -> list[str]:
    fragments = []
    for value in (claim.claim_text, claim.raw_excerpt):
        normalized = _normalize_text(value)
        if len(normalized) >= 20:
            fragments.append(normalized)
    return fragments


def _has_overlap(target: str, source_fragments: list[str], *, window: int = 20) -> bool:
    if not target:
        return False
    for fragment in source_fragments:
        if len(fragment) < window:
            continue
        for start in range(0, len(fragment) - window + 1):
            if fragment[start : start + window] in target:
                return True
    return False


def _is_negated_advice_context(text: str, phrase: str) -> bool:
    if phrase not in text:
        return False
    return any(pattern.search(text) for pattern in NEGATED_ADVICE_PATTERNS)
