"""Deterministic rule builder for Skill v0.1."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from tgb_pipeline.models import MethodologyClaim, MethodologyRule

THEME_ORDER = [
    "量化影响",
    "成交额 / 量能",
    "短线基础行情",
    "指数环境",
    "风控",
    "牛熊切换",
]

THEME_TAG_MAP = {
    "量化影响": {"量化影响"},
    "成交额 / 量能": {"成交额"},
    "短线基础行情": {"短线基础行情"},
    "指数环境": {"指数环境"},
    "风控": {"风控"},
    "牛熊切换": {"牛熊切换"},
}


@dataclass(frozen=True)
class ThemeRuleTemplate:
    title: str
    rule_text: str
    when_to_use: list[str]
    do_not_use_when: list[str]
    caveats: list[str]


THEME_RULE_TEMPLATES: dict[str, ThemeRuleTemplate] = {
    "量化影响": ThemeRuleTemplate(
        title="量化影响需要纳入短线市场结构判断",
        rule_text=(
            "量化交易会改变短线生态中的资金反馈速度、流动性分布和追涨/抛压结构；"
            "分析短线机会时，需要把量化带来的趋同交易、规避策略和盘中反馈纳入市场结构判断。"
        ),
        when_to_use=[
            "当作者讨论量化、量化冲击、量化反馈或短线生态变化时。",
            "当盘面现象不能只用题材强弱解释时。",
        ],
        do_not_use_when=[
            "只有个股复盘细节、没有市场结构含义时。",
            "只有情绪表达、没有机制判断时。",
        ],
        caveats=[
            "不要把量化影响简化成单一利多或利空。",
            "需要结合指数环境、成交额和短线基础行情共同判断。",
        ],
    ),
    "成交额 / 量能": ThemeRuleTemplate(
        title="成交额约束短线高度与持续性",
        rule_text=(
            "成交额与量能不是简单的放量好、缩量坏；需要结合指数环境、短线基础行情和资金稀缺性判断。"
            "短线高度、接力持续性和赚钱效应都受整体成交活跃度约束。"
        ),
        when_to_use=[
            "当作者讨论成交额、量能、缩量、放量和流动性约束时。",
            "当题材高度或接力持续性出现变化时。",
        ],
        do_not_use_when=[
            "只有单一日内波动、没有成交结构信息时。",
            "只有盘后感叹、没有可抽象规则时。",
        ],
        caveats=[
            "量能本身不是结论，需要和指数环境、风险偏好一起看。",
        ],
    ),
    "短线基础行情": ThemeRuleTemplate(
        title="先判断短线基础行情，再判断局部机会",
        rule_text=(
            "短线机会不能只看个股局部强弱；应先判断整体赚钱效应、接力环境、轮动速度和指数/成交额背景，"
            "再评估个股高度与容错。"
        ),
        when_to_use=[
            "当作者讨论连板、首板、接力、赚钱效应和短线生态时。",
            "当局部强股表现与整体短线环境出现背离时。",
        ],
        do_not_use_when=[
            "只有个股点评、没有短线生态含义时。",
            "只有泛泛说强弱、没有环境判断时。",
        ],
        caveats=[
            "短线基础行情是环境变量，不等于单只股票的即时强弱。",
        ],
    ),
    "指数环境": ThemeRuleTemplate(
        title="指数环境影响短线承接与风险偏好",
        rule_text=(
            "指数环境会影响短线资金的承接、风险偏好和仓位选择；指数震荡或下行风险较大时，"
            "应降低对局部题材强度和持续性的确定性判断。"
        ),
        when_to_use=[
            "当作者讨论指数、市场环境、大盘背景或承接变化时。",
            "当局部题材强度与整体指数环境不一致时。",
        ],
        do_not_use_when=[
            "只有情绪化看法、没有环境传导逻辑时。",
            "只有单日涨跌结论、没有对短线生态的影响判断时。",
        ],
        caveats=[
            "指数环境影响的是风险偏好与承接，不应被机械当成唯一方向判断。",
        ],
    ),
    "风控": ThemeRuleTemplate(
        title="环境不支持进攻时优先收缩风险暴露",
        rule_text=(
            "当指数、成交额、短线基础行情或亏钱效应不支持进攻时，应优先降低仓位、减少交易或等待，"
            "而不是强行套用强行情打法。"
        ),
        when_to_use=[
            "当作者讨论弱市、回撤、亏钱效应、仓位和等待时。",
            "当买入前提不成立或流动性明显恶化时。",
        ],
        do_not_use_when=[
            "只有口号式风险提醒、没有执行原则时。",
            "只有单只个股抱怨、没有风控规则时。",
        ],
        caveats=[
            "风控规则优先于进攻意愿。",
            "需要把环境变化和执行节奏一起看。",
        ],
    ),
    "牛熊切换": ThemeRuleTemplate(
        title="牛熊切换下不能简单沿用同一套短线节奏",
        rule_text=(
            "牛市、熊市和切换期的短线基础行情不同，不能简单沿用同一套短线策略；"
            "需要根据成交额、指数环境和赚钱/亏钱效应重新判断进攻与防守权重。"
        ),
        when_to_use=[
            "当作者讨论牛市、熊市、市场状态变化或周期切换时。",
            "当策略节奏需要根据环境切换时。",
        ],
        do_not_use_when=[
            "只有口语化情绪判断、没有环境差异逻辑时。",
            "只有历史感慨、没有可执行原则时。",
        ],
        caveats=[
            "不要把牛熊切换理解成单一择时信号。",
            "要结合成交额、指数环境和短线基础行情综合判断。",
        ],
    ),
}

THEME_RULE_PREFIXES = {
    "量化影响": "在评估量化影响时，应将以下判断纳入市场结构分析：",
    "成交额 / 量能": "在评估成交额与量能时，应优先检查：",
    "短线基础行情": "在判断短线基础行情时，应重点关注：",
    "指数环境": "在判断指数环境影响时，应优先考虑：",
    "风控": "在执行风控时，应优先遵守：",
    "牛熊切换": "在判断牛熊切换时，应优先检查：",
}


def build_methodology_rules(
    accepted_claims: list[MethodologyClaim],
    *,
    max_rules_per_theme: int = 8,
    min_evidence_per_rule: int = 1,
    max_evidence_per_rule: int = 5,
) -> list[MethodologyRule]:
    grouped = group_claims_by_theme(accepted_claims)
    rules: list[MethodologyRule] = []
    for theme in THEME_ORDER:
        theme_claims = select_representative_claims(grouped.get(theme, []), max_rules_per_theme)
        if len(theme_claims) < min_evidence_per_rule:
            continue
        template = THEME_RULE_TEMPLATES[theme]
        overview_evidence = theme_claims[:max_evidence_per_rule]
        rules.append(
            MethodologyRule(
                rule_id=f"{theme_key(theme)}-overview",
                theme=theme,
                title=template.title,
                rule_text=template.rule_text,
                when_to_use=template.when_to_use,
                do_not_use_when=template.do_not_use_when,
                evidence_claim_ids=[claim.claim_id for claim in overview_evidence],
                evidence_article_ids=_unique_article_ids(overview_evidence),
                caveats=template.caveats,
                source_tags=sorted(THEME_TAG_MAP[theme]),
                raw={
                    "rule_kind": "overview",
                    "evidence_count": len(overview_evidence),
                },
            )
        )
        for index, claim in enumerate(theme_claims[1:max_rules_per_theme], start=1):
            rules.append(
                MethodologyRule(
                    rule_id=f"{theme_key(theme)}-{index}",
                    theme=theme,
                    title=f"{theme}规则 {index}",
                    rule_text=_wrap_rule_text(theme, claim.claim_text),
                    when_to_use=[_default_when_to_use(theme)],
                    do_not_use_when=[_default_do_not_use_when(theme)],
                    evidence_claim_ids=[claim.claim_id],
                    evidence_article_ids=[claim.article_id] if claim.article_id else [],
                    caveats=[_default_caveat(theme)],
                    source_tags=sorted(set(claim.method_tags)),
                    raw={
                        "rule_kind": "claim_normalized",
                        "source_claim_id": claim.claim_id,
                    },
                )
            )
    return rules


def primary_theme(claim: MethodologyClaim) -> str | None:
    for theme in THEME_ORDER:
        if THEME_TAG_MAP[theme].intersection(claim.method_tags):
            return theme
    return None


def group_claims_by_theme(claims: list[MethodologyClaim]) -> dict[str, list[MethodologyClaim]]:
    grouped: dict[str, list[MethodologyClaim]] = defaultdict(list)
    for claim in claims:
        theme = primary_theme(claim)
        if theme is not None:
            grouped[theme].append(claim)
    return grouped


def select_representative_claims(
    claims: list[MethodologyClaim],
    max_items: int,
) -> list[MethodologyClaim]:
    source_priority = {"article": 0, "comment": 1, "interaction": 2, "image_ocr": 3}

    def ranking_score(claim: MethodologyClaim) -> int:
        ranking = (claim.raw or {}).get("ranking") or {}
        return int(ranking.get("score", 0))

    return sorted(
        claims,
        key=lambda claim: (
            source_priority.get(claim.source_type.value, 9),
            -ranking_score(claim),
            claim.claim_id,
        ),
    )[:max_items]


def theme_key(theme: str) -> str:
    return {
        "量化影响": "quant-impact",
        "成交额 / 量能": "turnover",
        "短线基础行情": "short-term-base",
        "指数环境": "index-environment",
        "风控": "risk-control",
        "牛熊切换": "bull-bear",
    }[theme]


def _wrap_rule_text(theme: str, claim_text: str) -> str:
    cleaned = " ".join(claim_text.strip().split())
    cleaned = cleaned.strip("“”\"' ")
    cleaned = cleaned.rstrip("。！？!?")
    return f"{THEME_RULE_PREFIXES[theme]}{cleaned}。"


def _default_when_to_use(theme: str) -> str:
    return {
        "量化影响": "当作者讨论量化冲击、盘中反馈或短线生态变化时。",
        "成交额 / 量能": "当作者讨论成交额、缩量、放量和市场活跃度时。",
        "短线基础行情": "当作者讨论接力环境、赚钱效应和短线容错时。",
        "指数环境": "当作者讨论指数背景、承接变化和风险偏好时。",
        "风控": "当作者讨论仓位、等待、回撤或亏钱效应时。",
        "牛熊切换": "当作者讨论牛熊状态、强弱环境和节奏切换时。",
    }[theme]


def _default_do_not_use_when(theme: str) -> str:
    return {
        "量化影响": "不要把没有结构含义的个股碎句直接当成量化规则。",
        "成交额 / 量能": "不要把没有环境背景的量能描述直接当成独立结论。",
        "短线基础行情": "不要把单一个股强弱直接当成整体短线环境。",
        "指数环境": "不要把指数涨跌本身当成唯一方法论结论。",
        "风控": "不要把情绪化恐慌表达直接当成风控规则。",
        "牛熊切换": "不要把情绪化牛熊判断直接当成稳定策略规则。",
    }[theme]


def _default_caveat(theme: str) -> str:
    return {
        "量化影响": "需要结合成交额、指数环境和短线基础行情一起判断。",
        "成交额 / 量能": "量能本身不是结论，需要结合环境解释。",
        "短线基础行情": "局部强股不能替代整体短线生态判断。",
        "指数环境": "指数环境影响承接与风险偏好，不是唯一方向信号。",
        "风控": "风控优先于进攻，执行前要确认环境是否支持。",
        "牛熊切换": "环境切换意味着策略节奏和风险预算都可能变化。",
    }[theme]


def _unique_article_ids(claims: list[MethodologyClaim]) -> list[str]:
    seen: set[str] = set()
    article_ids: list[str] = []
    for claim in claims:
        if not claim.article_id or claim.article_id in seen:
            continue
        seen.add(claim.article_id)
        article_ids.append(claim.article_id)
    return article_ids
