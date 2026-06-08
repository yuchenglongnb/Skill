"""Build a structured methodology profile from abstract rules and reviewed evidence."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim, MethodologyRule
from tgb_pipeline.skill.rule_builder import THEME_ORDER, group_claims_by_theme

THEME_RELATIONSHIPS = [
    "量化影响如何改变短线生态：量化资金会改变资金反馈速度、流动性分布和盘中承接结构。",
    "成交额如何约束短线高度：成交活跃度不足时，短线高度、接力持续性和赚钱效应都会受限。",
    "指数环境如何影响短线基础行情：指数环境会直接影响短线承接、风险偏好和容错空间。",
    "弱市或熊市为什么需要风控优先：当亏钱效应扩散、流动性不足时，仓位与交易频率都应先收缩。",
    "牛熊切换下为什么不能简单套用同一套短线策略：环境切换会改变风险收益比、执行节奏和可用模式。",
]


def build_methodology_profile_v0(
    accepted_claims: list[MethodologyClaim],
    needs_edit_claims: list[MethodologyClaim],
    rejected_claims: list[MethodologyClaim],
    rules: list[MethodologyRule],
    output_dir: Path,
    *,
    reviewed_packs: list[str],
    unreviewed_count: int,
    accepted_recheck_candidates: list[dict[str, object]] | None = None,
    max_claims_per_theme: int = 5,
    max_rules_per_theme: int = 5,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    accepted_recheck_candidates = accepted_recheck_candidates or []
    accepted_by_theme = group_claims_by_theme(accepted_claims)
    needs_edit_by_theme = group_claims_by_theme(needs_edit_claims)
    rules_by_theme = _group_rules_by_theme(rules)
    recheck_by_theme = _group_recheck_by_theme(accepted_recheck_candidates)
    rejected_reason_counts = Counter(
        claim.review_notes or claim.raw.get("review_reason") or claim.review_bucket or "rejected"
        for claim in rejected_claims
    )

    lines = [
        "# 等主人的猫：阶段性方法论画像 v0.2",
        "",
        "## 数据状态",
        f"- accepted claims: {len(accepted_claims)}",
        f"- needs_edit claims: {len(needs_edit_claims)}",
        f"- rejected claims: {len(rejected_claims)}",
        f"- reviewed packs: {', '.join(reviewed_packs) if reviewed_packs else 'none'}",
        f"- unreviewed claims: {unreviewed_count}",
        f"- accepted recheck candidates: {len(accepted_recheck_candidates)}",
        "",
        "## Rule Summary",
    ]

    for theme in THEME_ORDER:
        lines.extend([f"### {theme}", ""])
        theme_rules = rules_by_theme.get(theme, [])[:max_rules_per_theme]
        if theme_rules:
            for rule in theme_rules:
                lines.extend(
                    [
                        f"- `{rule.rule_id}` {rule.title}",
                        f"  - rule_text: {rule.rule_text}",
                        f"  - evidence_claim_ids: {', '.join(rule.evidence_claim_ids)}",
                    ]
                )
        else:
            lines.append("- 暂无该主题规则。")
        lines.append("")

    lines.extend(["## Representative Accepted Evidence", ""])
    for theme in THEME_ORDER:
        lines.extend([f"### {theme}", ""])
        theme_claims = accepted_by_theme.get(theme, [])[:max_claims_per_theme]
        if theme_claims:
            for claim in theme_claims:
                lines.extend(_claim_block(claim))
        else:
            lines.append("- 暂无已确认代表 evidence。")
        lines.append("")

    lines.extend(["## Accepted Claims Recheck Candidates", ""])
    if accepted_recheck_candidates:
        for theme in [*THEME_ORDER, "未分类"]:
            theme_items = recheck_by_theme.get(theme, [])[:max_claims_per_theme]
            if not theme_items:
                continue
            lines.extend([f"### {theme}", ""])
            for item in theme_items:
                lines.extend(
                    [
                        f"- claim_id: `{item['claim_id']}`",
                        f"  - article_id: {item['article_id'] or 'unknown'}",
                        f"  - source_type: {item['source_type']}",
                        f"  - recheck_reason: {item['recheck_reason']}",
                        f"  - raw_excerpt: {item['raw_excerpt']}",
                        f"  - review_notes: {item['review_notes'] or 'none'}",
                    ]
                )
            lines.append("")
    else:
        lines.append("- 当前没有 accepted recheck candidates。")
        lines.append("")

    lines.extend(["## Needs-edit Worklist", ""])
    if needs_edit_claims:
        for theme in THEME_ORDER:
            theme_claims = needs_edit_by_theme.get(theme, [])[:max_claims_per_theme]
            if not theme_claims:
                continue
            lines.extend([f"### {theme}", ""])
            for claim in theme_claims:
                lines.extend(_claim_block(claim, include_notes=True))
            lines.append("")
    else:
        lines.append("- 当前没有 needs_edit 观点。")
        lines.append("")

    lines.extend(["## 主题之间的关系", ""])
    for relation in THEME_RELATIONSHIPS:
        lines.append(f"- {relation}")

    lines.extend(["", "## 排除边界", "", "- rejected 类型总结："])
    if rejected_reason_counts:
        for reason, count in rejected_reason_counts.most_common(8):
            lines.append(f"  - {reason}: {count}")
    else:
        lines.append("  - 暂无 rejected 记录。")
    lines.extend(
        [
            "- 泛句、碎句、反讽、上下文不足不进入核心方法论。",
            "- needs_edit 只作为待确认素材，不直接写成核心规则。",
            "- rejected / unreviewed 不进入 Skill v0.2 的核心方法论。",
            "",
        ]
    )

    output_path = output_dir / "methodology_profile.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _group_rules_by_theme(rules: list[MethodologyRule]) -> dict[str, list[MethodologyRule]]:
    grouped: dict[str, list[MethodologyRule]] = defaultdict(list)
    for rule in rules:
        grouped[rule.theme].append(rule)
    return grouped


def _group_recheck_by_theme(items: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in items:
        grouped[str(item.get("theme") or "未分类")].append(item)
    return grouped


def _claim_block(claim: MethodologyClaim, *, include_notes: bool = False) -> list[str]:
    lines = [
        f"- claim_id: `{claim.claim_id}`",
        f"  - raw_excerpt: {claim.raw_excerpt}",
        f"  - article_id: {claim.article_id or 'unknown'}",
        f"  - source_type: {claim.source_type.value}",
        f"  - method_tags: {', '.join(claim.method_tags) if claim.method_tags else 'none'}",
    ]
    if include_notes:
        lines.append(f"  - review_notes: {claim.review_notes or 'none'}")
    return lines
