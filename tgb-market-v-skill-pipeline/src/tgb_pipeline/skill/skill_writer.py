"""Write Skill v0.1 markdown artifacts from normalized rules."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim, MethodologyRule
from tgb_pipeline.skill.rule_builder import THEME_ORDER

NEXT_REVIEW_PACKS = [
    "execution_rule_top100",
    "index_environment_top100",
    "digitization_top80",
]


def write_skill_markdown(
    rules: list[MethodologyRule],
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    rules_by_theme = _group_rules_by_theme(rules)
    lines = [
        "# TGB Market V Skill v0.1",
        "",
        "## Purpose",
        "This skill summarizes the reviewed methodology of the target author based on accepted claims only.",
        "",
        "## Scope and Non-advice Boundary",
        "- 用于归纳该作者的方法论表达；",
        "- 用于辅助分析其文章、评论和互动中的方法论线索；",
        "- 不用于生成具体买卖建议；",
        "- 不用于预测个股涨跌；",
        "- 不替代人工判断。",
        "",
        "## Source Policy",
        "- Core rules come from accepted_review_ready_claims only.",
        "- needs_edit claims are treated as uncertain context only.",
        "- rejected and unreviewed claims must not be used as methodology.",
        "",
        "## Core Methodology Rules",
        "",
    ]

    for index, theme in enumerate(THEME_ORDER, start=1):
        lines.append(f"### {index}. {theme}")
        theme_rules = rules_by_theme.get(theme, [])
        if not theme_rules:
            lines.extend(["- 暂无已确认规则。", ""])
            continue
        for rule in theme_rules:
            lines.extend(
                [
                    f"#### Rule {rule.rule_id}: {rule.title}",
                    f"- Rule: {rule.rule_text}",
                    f"- When to use: {'；'.join(rule.when_to_use) if rule.when_to_use else 'none'}",
                    f"- Do not use when: {'；'.join(rule.do_not_use_when) if rule.do_not_use_when else 'none'}",
                    "- Evidence:",
                ]
            )
            for claim_id in rule.evidence_claim_ids:
                lines.append(f"  - `{claim_id}`")
            lines.append(f"- Caveats: {'；'.join(rule.caveats) if rule.caveats else 'none'}")
            lines.append("")

    lines.extend(
        [
            "## How to Analyze a New Statement",
            "1. 识别它更接近量化影响、成交额 / 量能、短线基础行情、指数环境、风控还是牛熊切换。",
            "2. 判断表达是字面陈述，还是可能带有反讽、玩笑、夸张或故意说反话。",
            "3. 如果语气或上下文不确定，标记为 `needs_human_check`，不要自动反向解释。",
            "4. 只有 accepted evidence 支持的规则，才能作为强结论来源。",
            "5. needs_edit 只能作为待确认背景，不能升级成核心规则。",
            "6. 不输出买卖建议，不输出确定性承诺。",
            "",
            "## Tone and Ambiguity Policy",
            "- The author may use sarcasm, jokes, deliberate exaggeration, and intentionally wrong-sounding statements.",
            "- Do not automatically reverse literal meaning.",
            "- Mark ambiguous statements as `needs_human_check`.",
            "- Require surrounding context before converting them into methodology.",
            "",
            "## Output Rules",
            "- 指出发言对应的主题。",
            "- 优先引用 rule_id 和 claim_id，而不是直接复述长段原文。",
            "- 清楚区分已确认方法论和待确认解释。",
            "- 避免直接买卖建议。",
            "- 避免宣称确定性结论。",
            "",
            "## Limitations",
            "- Corpus is partial.",
            "- Some comment pages were inaccessible due to login/verification/app-open pages.",
            "- Image OCR is not a reliable source unless explicitly reviewed.",
            "- Skill v0.1 is based on first-round reviewed packs only.",
            "",
        ]
    )
    output_path = output_dir / "SKILL.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def write_uncertainty_policy(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Uncertainty Policy",
        "",
        "## Sarcasm / Joke / Deliberate Misstatement",
        "If a statement appears sarcastic, joking, exaggerated, or intentionally wrong-sounding:",
        "- do not treat it as literal methodology;",
        "- do not automatically invert it;",
        "- mark it as needs_human_check;",
        "- require surrounding context.",
        "",
        "## Needs-edit Claims",
        "Claims marked needs_edit are not confirmed methodology.",
        "They may be used only as tentative context.",
        "",
        "## Rejected Claims",
        "Rejected claims must not be used as methodology.",
        "",
        "## Inaccessible Pages",
        "Some comment pages returned login/verification/app-open pages.",
        "They are treated as inaccessible evidence gaps, not negative evidence.",
        "",
    ]
    output_path = output_dir / "uncertainty_policy.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def write_review_summary(
    accepted_claims: list[MethodologyClaim],
    needs_edit_claims: list[MethodologyClaim],
    rejected_claims: list[MethodologyClaim],
    rules: list[MethodologyRule],
    output_dir: Path,
    *,
    reviewed_packs: list[str],
    unreviewed_count: int,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    accepted_by_tag = Counter(tag for claim in accepted_claims for tag in claim.method_tags)
    rules_by_theme = Counter(rule.theme for rule in rules)
    lines = [
        "# Review Summary",
        "",
        "## Reviewed Packs",
    ]
    if reviewed_packs:
        for pack in reviewed_packs:
            lines.append(f"- {pack}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Counts",
            f"- accepted: {len(accepted_claims)}",
            f"- rejected: {len(rejected_claims)}",
            f"- needs_edit: {len(needs_edit_claims)}",
            f"- unreviewed: {unreviewed_count}",
            "",
            "## accepted_by_tag",
        ]
    )
    for tag, count in accepted_by_tag.most_common(10):
        lines.append(f"- {tag}: {count}")

    lines.extend(["", "## rule_count_by_theme"])
    for theme in THEME_ORDER:
        lines.append(f"- {theme}: {rules_by_theme.get(theme, 0)}")

    lines.extend(
        [
            "",
            "## Known Gaps",
            "- 部分评论页因登录 / 验证 / 打开 app 页面不可访问，形成证据缺口。",
            "- image OCR 目前只适合作为待复核辅助，不作为默认核心证据。",
            "- 仍有大量 unreviewed review-ready claims 尚未进入本轮 Skill v0.1。",
            "",
            "## Next Recommended Review Packs",
        ]
    )
    for pack in NEXT_REVIEW_PACKS:
        lines.append(f"- {pack}")
    lines.append("- 或继续补 2jbi0efIsof / 2ohHCnLXtP8 评论。")
    lines.append("")

    output_path = output_dir / "review_summary.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _group_rules_by_theme(rules: list[MethodologyRule]) -> dict[str, list[MethodologyRule]]:
    grouped: dict[str, list[MethodologyRule]] = {theme: [] for theme in THEME_ORDER}
    for rule in rules:
        grouped.setdefault(rule.theme, []).append(rule)
    return grouped
