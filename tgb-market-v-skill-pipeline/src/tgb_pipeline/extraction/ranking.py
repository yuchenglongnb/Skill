"""Ranking helpers for review-ready claim subsets."""

from __future__ import annotations

from tgb_pipeline.models import MethodologyClaim

CORE_ARTICLE_IDS = {
    "2jbi0efIsof",
    "2ohHCnLXtP8",
    "2bWeZGDSi07",
    "2fQt29pQ3Pa",
}
HIGH_VALUE_TAGS = {
    "量化影响",
    "成交额",
    "短线基础行情",
    "指数环境",
    "风控",
    "牛熊切换",
    "数字化?标准化",
}
STRONG_STRUCTURE_TERMS = (
    "不是",
    "而是",
    "如果",
    "那么",
    "因为",
    "所以",
    "核心是",
    "本质是",
    "标准是",
    "取决于",
    "关键在于",
    "风险在于",
)
LOW_PRIORITY_FLAGS = {
    "has_analogy_terms",
    "has_emotional_terms",
    "short_text",
    "has_generic_market_terms",
}


def has_reasonable_density(text: str) -> bool:
    stripped = text.strip()
    if not 20 <= len(stripped) <= 220:
        return False
    punctuation_hits = sum(stripped.count(mark) for mark in ("，", "。", "；", "：", ",", ".", ";", ":"))
    return punctuation_hits >= 1 or len(set(stripped)) >= 12


def rank_claim_for_review(claim: MethodologyClaim) -> MethodologyClaim:
    text = claim.claim_text or ""
    quality = (claim.raw or {}).get("quality") or {}
    quality_reason = str(quality.get("reason", "unknown"))
    quality_score = int(quality.get("score", 0))
    quality_flags = [str(flag) for flag in quality.get("flags", [])]

    bucket = _infer_bucket(claim, text, quality_reason, quality_flags)
    priority, ranking_score, reasons = _infer_priority(
        claim,
        text,
        bucket,
        quality_reason,
        quality_score,
        quality_flags,
    )
    updated_raw = dict(claim.raw)
    updated_raw["ranking"] = {
        "reason": ", ".join(reasons),
        "score": ranking_score,
        "flags": quality_flags,
    }
    return _copy_claim(
        claim,
        review_priority=priority,
        review_bucket=bucket,
        raw=updated_raw,
    )


def _infer_bucket(
    claim: MethodologyClaim,
    text: str,
    quality_reason: str,
    quality_flags: list[str],
) -> str:
    tags = set(claim.method_tags)
    if quality_reason == "analogy_background":
        return "analogy_background"
    if quality_reason in {"emotional_noise", "short_weak_reply"}:
        return "short_reply"
    if quality_reason == "generic_market_statement":
        return "generic_market"
    if "风控" in tags:
        return "risk_control"
    if "指数环境" in tags:
        return "market_environment"
    if any(tag in tags for tag in {"成交额", "量化影响", "短线基础行情", "数字化?标准化"}):
        return "trading_mechanism"
    if any(term in text for term in ("买入", "卖出", "触发", "止损", "仓位")):
        return "execution_rule"
    if any(term in text for term in STRONG_STRUCTURE_TERMS):
        return "core_methodology"
    if "has_generic_market_terms" in quality_flags:
        return "generic_market"
    return "needs_human_check" if claim.source_type.value == "comment" else "background_context"


def _infer_priority(
    claim: MethodologyClaim,
    text: str,
    bucket: str,
    quality_reason: str,
    quality_score: int,
    quality_flags: list[str],
) -> tuple[str, int, list[str]]:
    reasons: list[str] = []
    score = quality_score
    tags = set(claim.method_tags)
    has_strong_structure = any(term in text for term in STRONG_STRUCTURE_TERMS)
    if has_strong_structure:
        reasons.append("strong_structure")
        score += 4
    if tags.intersection(HIGH_VALUE_TAGS):
        reasons.append("high_value_tags")
        score += 3
    if 20 <= len(text) <= 220:
        reasons.append("good_length")
        score += 2
    if claim.article_id in CORE_ARTICLE_IDS:
        reasons.append("core_article")
        score += 2
    if claim.source_type.value == "article":
        reasons.append("article_source")
        score += 2
    if bucket in {"generic_market", "short_reply", "analogy_background", "background_context"}:
        score -= 3
        reasons.append(f"bucket:{bucket}")
    if quality_reason in {"generic_market_statement", "weak_signal_statement"}:
        score -= 3
        reasons.append(f"quality:{quality_reason}")
    if set(quality_flags).intersection(LOW_PRIORITY_FLAGS) and not has_strong_structure:
        score -= 2
        reasons.append("noise_flags")

    if (
        has_strong_structure
        and (tags.intersection(HIGH_VALUE_TAGS) or claim.source_type.value == "article" or claim.article_id in CORE_ARTICLE_IDS)
        and 20 <= len(text) <= 220
    ):
        return "high", score, reasons or ["high_signal"]
    if (
        claim.source_type.value == "article"
        and tags.intersection(HIGH_VALUE_TAGS)
        and 20 <= len(text) <= 220
    ):
        return "high", score, reasons or ["article_high_value_signal"]
    if (
        claim.article_id in CORE_ARTICLE_IDS
        and tags.intersection(HIGH_VALUE_TAGS)
        and has_reasonable_density(text)
    ):
        return "high", score, reasons or ["high_signal"]
    if claim.source_type.value == "article" and bucket not in {"generic_market", "short_reply", "analogy_background"}:
        return "normal", score, reasons or ["article_default"]
    if len(text) < 18 and not has_strong_structure:
        return "low", score, reasons or ["very_short"]
    if bucket in {"generic_market", "short_reply", "analogy_background", "background_context"}:
        return "low", score, reasons or [f"bucket:{bucket}"]
    return "normal", score, reasons or ["default"]


def _copy_claim(claim: MethodologyClaim, **updates) -> MethodologyClaim:
    if hasattr(claim, "model_copy"):
        return claim.model_copy(update=updates, deep=True)
    return claim.copy(update=updates, deep=True)
