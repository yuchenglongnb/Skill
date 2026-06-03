"""Lightweight quality filters for methodology claim candidates."""

from __future__ import annotations

import re

from pydantic import Field

from tgb_pipeline.models import PipelineModel
from tgb_pipeline.utils.text_cleaning import clean_text


class ClaimQualityDecision(PipelineModel):
    keep: bool
    reason: str
    score: int = 0
    flags: list[str] = Field(default_factory=list)


ANALOGY_TERMS = (
    "春夏秋冬",
    "春天",
    "夏天",
    "秋天",
    "冬天",
    "四季",
    "温度",
    "气温",
    "降雨",
    "下雨",
    "天气",
    "节气",
    "农作物",
    "种地",
    "播种",
    "收成",
)
STRONG_TRADING_TERMS = (
    "成交额",
    "量化",
    "指数",
    "短线",
    "连板",
    "买入",
    "卖出",
    "仓位",
    "风控",
    "牛市",
    "熊市",
    "情绪周期",
    "市场结构",
    "亏钱效应",
    "赚钱效应",
)
EMOTIONAL_TERMS = (
    "哈哈",
    "呵呵",
    "牛逼",
    "太难了",
    "真离谱",
    "服了",
    "厉害",
    "感谢",
    "谢谢",
    "新年快乐",
    "周末愉快",
    "看戏",
    "无语",
)
REASONING_TERMS = (
    "因为",
    "所以",
    "如果",
    "但是",
    "本质",
    "规律",
    "标准",
    "决定",
    "意味着",
    "取决于",
    "不是",
    "而是",
    "必须",
    "不能",
    "需要",
    "应该",
    "核心",
    "关键",
    "前提",
)
METHOD_PATTERN_TERMS = (
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
    "成交额决定",
    "量化导致",
    "指数环境决定",
    "短线基础行情",
)
GENERIC_MARKET_TERMS = (
    "市场",
    "指数",
    "行情",
    "情绪",
    "周期",
    "结构",
)
OPERATION_TERMS = (
    "买",
    "卖",
    "低吸",
    "追涨",
    "止损",
    "控仓",
    "加仓",
    "减仓",
    "上仓位",
    "空仓",
)
RISK_TERMS = (
    "风险",
    "风控",
    "止损",
    "回撤",
    "亏钱",
)
STRONG_TAGS = {
    "情绪周期",
    "成交额",
    "短线基础行情",
    "量化影响",
    "市场结构",
    "指数环境",
    "买入触发",
    "风控",
    "牛熊切换",
}
QUESTION_ONLY_RE = re.compile(r"^[^。；!！]*[?？]\s*$")


def evaluate_claim_candidate(
    *,
    text: str,
    source_type: str,
    method_tags: list[str],
    tickers: list[str],
    sectors: list[str],
    concepts: list[str],
) -> ClaimQualityDecision:
    compact = clean_text(text)
    flags: list[str] = []
    score = 0

    if not compact:
        return ClaimQualityDecision(keep=False, reason="empty_text", flags=["empty_text"])
    if compact.startswith("[IMAGE:"):
        return ClaimQualityDecision(
            keep=False,
            reason="image_placeholder",
            flags=["image_placeholder"],
        )

    has_analogy = _contains_any(compact, ANALOGY_TERMS)
    has_strong_trading = _contains_any(compact, STRONG_TRADING_TERMS)
    has_reasoning = _contains_any(compact, REASONING_TERMS)
    has_method_pattern = _contains_any(compact, METHOD_PATTERN_TERMS)
    has_emotional = _contains_any(compact, EMOTIONAL_TERMS)
    has_generic_market = _contains_any(compact, GENERIC_MARKET_TERMS)
    has_operation = _contains_any(compact, OPERATION_TERMS)
    has_risk = _contains_any(compact, RISK_TERMS)
    has_strong_method_tag = bool(set(method_tags).intersection(STRONG_TAGS))
    has_method_tag = bool(method_tags)
    has_entity_context = bool(tickers or sectors or concepts)
    is_short = len(compact) < 12
    is_pure_question = bool(QUESTION_ONLY_RE.match(compact))

    if has_analogy:
        flags.append("has_analogy_terms")
    if has_strong_trading:
        flags.append("has_strong_trading_terms")
        score += 3
    if has_reasoning:
        flags.append("has_reasoning_terms")
        score += 2
    if has_method_pattern:
        flags.append("has_method_pattern")
        score += 3
    if has_emotional:
        flags.append("has_emotional_terms")
    if has_generic_market:
        flags.append("has_generic_market_terms")
    if has_operation:
        flags.append("has_operation_terms")
        score += 2
    if has_risk:
        flags.append("has_risk_terms")
        score += 2
    if has_strong_method_tag:
        flags.append("has_strong_method_tag")
        score += 2
    if has_method_tag:
        flags.append("has_method_tag")
        score += 1
    if has_entity_context:
        flags.append("has_entity_context")
        score += 2
    if is_short:
        flags.append("short_text")
        score -= 1
    if is_pure_question:
        flags.append("pure_question")
        score -= 2
    if source_type == "article":
        score += 1

    if has_analogy and not has_strong_trading:
        return ClaimQualityDecision(
            keep=False,
            reason="analogy_background",
            score=score,
            flags=flags,
        )
    if has_emotional and is_short and not (has_strong_trading or has_reasoning or has_method_pattern):
        return ClaimQualityDecision(
            keep=False,
            reason="emotional_noise",
            score=score,
            flags=flags,
        )
    if is_pure_question and not (has_reasoning or has_method_pattern or has_strong_trading or has_strong_method_tag):
        return ClaimQualityDecision(
            keep=False,
            reason="pure_question",
            score=score,
            flags=flags,
        )
    if (
        has_generic_market
        and not (has_reasoning or has_method_pattern or has_operation or has_risk or has_strong_trading)
        and not has_entity_context
        and not has_strong_method_tag
    ):
        return ClaimQualityDecision(
            keep=False,
            reason="generic_market_statement",
            score=score,
            flags=flags,
        )
    if (
        is_short
        and not has_entity_context
        and not has_strong_method_tag
        and not has_reasoning
        and not has_method_pattern
    ):
        return ClaimQualityDecision(
            keep=False,
            reason="short_weak_reply",
            score=score,
            flags=flags,
        )
    if has_method_pattern or has_strong_method_tag:
        return ClaimQualityDecision(
            keep=True,
            reason="strong_methodology_statement",
            score=score,
            flags=flags,
        )
    if has_strong_trading and (has_reasoning or has_operation or has_risk or has_entity_context):
        return ClaimQualityDecision(
            keep=True,
            reason="trading_mechanism_statement",
            score=score,
            flags=flags,
        )
    if has_entity_context and (has_method_tag or has_reasoning or has_operation or has_strong_trading):
        return ClaimQualityDecision(
            keep=True,
            reason="entity_supported_statement",
            score=score,
            flags=flags,
        )
    if has_reasoning and (has_generic_market or has_strong_trading or has_method_tag):
        return ClaimQualityDecision(
            keep=True,
            reason="reasoned_market_statement",
            score=score,
            flags=flags,
        )
    if has_method_tag and len(compact) >= 12:
        return ClaimQualityDecision(
            keep=True,
            reason="tag_supported_statement",
            score=score,
            flags=flags,
        )
    return ClaimQualityDecision(
        keep=False,
        reason="weak_signal_statement",
        score=score,
        flags=flags,
    )


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)
