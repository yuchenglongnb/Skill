"""Build a reviewed methodology profile from curated claims."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim

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

THEME_RELATIONSHIPS = [
    "量化影响如何改变短线生态：量化资金会改变反馈速度、涨跌停结构和日内承接节奏。",
    "成交额如何约束短线高度：量能不足时，短线高度、接力持续性和赚钱效应都会受限。",
    "指数环境如何影响短线基础行情：指数强弱会直接影响短线情绪、承接和容错空间。",
    "弱市/熊市为什么需要风控优先：当亏钱效应扩大、流动性不足时，仓位和交易频率都应先收缩。",
    "牛熊切换下为什么不能简单套用同一套短线策略：环境切换会改变风险收益比、执行节奏和可用模式。",
]


def build_methodology_profile_v0(
    accepted_claims: list[MethodologyClaim],
    needs_edit_claims: list[MethodologyClaim],
    rejected_claims: list[MethodologyClaim],
    output_dir: Path,
    *,
    reviewed_packs: list[str],
    unreviewed_count: int,
    max_claims_per_theme: int = 5,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    accepted_by_theme = _group_claims_by_theme(accepted_claims)
    needs_edit_by_theme = _group_claims_by_theme(needs_edit_claims)
    rejected_reason_counts = Counter(
        claim.review_notes or claim.raw.get("review_reason") or claim.review_bucket or "rejected"
        for claim in rejected_claims
    )

    lines = [
        "# 等主人的猫：阶段性方法论画像 v0",
        "",
        "## 数据状态",
        f"- accepted claims: {len(accepted_claims)}",
        f"- needs_edit claims: {len(needs_edit_claims)}",
        f"- rejected claims: {len(rejected_claims)}",
        f"- reviewed packs: {', '.join(reviewed_packs) if reviewed_packs else 'none'}",
        f"- unreviewed claims: {unreviewed_count}",
        "",
        "## 核心主题",
    ]

    for theme in THEME_ORDER:
        theme_claims = accepted_by_theme.get(theme, [])
        lines.extend(
            [
                f"### {theme}",
                "",
                "核心规则：",
            ]
        )
        for index, claim in enumerate(_representative_claims(theme_claims, max_claims_per_theme), start=1):
            rule_text = claim.claim_text
            lines.append(f"{index}. {rule_text} (`{claim.claim_id}`)")
        if not theme_claims:
            lines.append("1. 暂无已确认规则。")
        lines.extend(["", "代表 claim："])
        if theme_claims:
            for claim in _representative_claims(theme_claims, max_claims_per_theme):
                lines.extend(_claim_block(claim))
        else:
            lines.append("- 暂无已确认代表 claim。")
        lines.append("")

    lines.extend(["## 主题之间的关系", ""])
    for relation in THEME_RELATIONSHIPS:
        lines.append(f"- {relation}")

    lines.extend(["", "## 待确认观点", ""])
    pending_any = False
    for theme in THEME_ORDER:
        theme_claims = needs_edit_by_theme.get(theme, [])
        if not theme_claims:
            continue
        pending_any = True
        lines.append(f"### {theme}")
        for claim in _representative_claims(theme_claims, max_claims_per_theme):
            lines.extend(_claim_block(claim))
        lines.append("")
    if not pending_any:
        lines.append("- 当前没有待确认观点。")
        lines.append("")

    lines.extend(
        [
            "## 排除边界",
            "",
            "- rejected 类型总结：",
        ]
    )
    if rejected_reason_counts:
        for reason, count in rejected_reason_counts.most_common(6):
            lines.append(f"  - {reason}: {count}")
    else:
        lines.append("  - 暂无 rejected 记录。")
    lines.extend(
        [
            "- 泛句、碎句、反讽、上下文不足不进入核心方法论。",
            "- needs_edit 只作为待确认材料，不写成确定规则。",
            "",
        ]
    )

    output_path = output_dir / "methodology_profile.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def primary_theme(claim: MethodologyClaim) -> str | None:
    for theme in THEME_ORDER:
        if THEME_TAG_MAP[theme].intersection(claim.method_tags):
            return theme
    return None


def _group_claims_by_theme(claims: list[MethodologyClaim]) -> dict[str, list[MethodologyClaim]]:
    grouped: dict[str, list[MethodologyClaim]] = defaultdict(list)
    for claim in claims:
        theme = primary_theme(claim)
        if theme is not None:
            grouped[theme].append(claim)
    return grouped


def _representative_claims(
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


def _claim_block(claim: MethodologyClaim) -> list[str]:
    return [
        f"- claim_id: {claim.claim_id}",
        f"  - article_id: {claim.article_id or 'unknown'}",
        f"  - source_type: {claim.source_type.value}",
        f"  - raw_excerpt: {claim.raw_excerpt}",
        f"  - method_tags: {', '.join(claim.method_tags) if claim.method_tags else 'none'}",
    ]
