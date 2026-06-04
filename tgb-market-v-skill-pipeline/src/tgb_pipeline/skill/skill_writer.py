"""Write Skill v0 markdown artifacts."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from tgb_pipeline.models import MethodologyClaim
from tgb_pipeline.skill.profile_builder import THEME_ORDER, THEME_TAG_MAP, primary_theme

NEXT_REVIEW_PACKS = [
    "execution_rule_top100",
    "index_environment_top100",
    "digitization_top80",
]


def write_skill_markdown(
    accepted_claims: list[MethodologyClaim],
    needs_edit_claims: list[MethodologyClaim],
    output_dir: Path,
    *,
    max_claims_per_theme: int = 5,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    accepted_by_theme = _group_by_theme(accepted_claims)
    lines = [
        "# TGB Market V Skill v0",
        "",
        "## Purpose",
        "This skill summarizes the reviewed methodology of the target author based on accepted claims only.",
        "",
        "## Scope",
        "- 用于归纳该博主的方法论表达；",
        "- 用于辅助分析其发言、文章和评论；",
        "- 不用于生成买卖建议；",
        "- 不用于预测个股涨跌；",
        "- 不替代人工判断。",
        "",
        "## Source Policy",
        "- Core rules come from accepted_review_ready_claims only.",
        "- needs_edit claims are treated as uncertain.",
        "- rejected and unreviewed claims must not be used as methodology.",
        "",
        "## Core Methodology",
        "",
    ]
    for theme in THEME_ORDER:
        lines.append(f"### {theme}")
        theme_claims = _select_claims(accepted_by_theme.get(theme, []), max_claims_per_theme)
        if not theme_claims:
            lines.append("- 暂无已确认规则。")
            lines.append("")
            continue
        for claim in theme_claims:
            lines.append(f"- {claim.claim_text} (`{claim.claim_id}`)")
        lines.append("")

    lines.extend(
        [
            "## Reasoning Rules",
            "When analyzing a new statement from the author:",
            "1. Identify whether it relates to market environment, turnover, quant impact, short-term base condition, risk control, or bull/bear regime.",
            "2. Check whether the statement is literal or possibly sarcastic/joking.",
            "3. If tone is ambiguous, do not infer the opposite meaning automatically.",
            "4. Use accepted evidence only for strong conclusions.",
            "5. Use needs_edit evidence only as tentative context.",
            "",
            "## Tone and Ambiguity Policy",
            "- The author may use sarcasm, jokes, deliberate exaggeration, and intentionally wrong-sounding statements.",
            "- Do not automatically reverse literal meaning.",
            "- Mark ambiguous statements as `needs_human_check`.",
            "- Require surrounding context before converting them into methodology.",
            "",
            "## Output Rules",
            "When asked to analyze a post:",
            "- State which methodology theme it relates to.",
            "- Quote or cite relevant claim_id evidence.",
            "- Clearly distinguish confirmed methodology from tentative interpretation.",
            "- Avoid direct buy/sell recommendations.",
            "- Avoid claims of certainty.",
            "",
            "## Limitations",
            "- Corpus is partial.",
            "- Some comment pages were inaccessible due to login/verification pages.",
            "- Image OCR is currently not a reliable source unless reviewed.",
            "- The skill is v0 and based on first-round reviewed packs only.",
            f"- Current accepted evidence count: {len(accepted_claims)}.",
            f"- Current needs_edit evidence count: {len(needs_edit_claims)}.",
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
    output_dir: Path,
    *,
    reviewed_packs: list[str],
    unreviewed_count: int,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    accepted_by_tag = Counter(tag for claim in accepted_claims for tag in claim.method_tags)
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
    lines.extend(
        [
            "",
            "## Known Gaps",
            "- 部分评论页因登录/验证/app 打开页不可访问，形成证据缺口。",
            "- image OCR 目前只适合作为待复核辅助，不作为默认核心证据。",
            "- 仍有大量 unreviewed review-ready claims 尚未进入本轮 Skill v0。",
            "",
            "## Next Recommended Review Packs",
        ]
    )
    for pack in NEXT_REVIEW_PACKS:
        lines.append(f"- {pack}")
    lines.extend(
        [
            "- 或继续补 2jbi0efIsof / 2ohHCnLXtP8 评论。",
            "",
        ]
    )
    output_path = output_dir / "review_summary.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _group_by_theme(claims: list[MethodologyClaim]) -> dict[str, list[MethodologyClaim]]:
    grouped: dict[str, list[MethodologyClaim]] = {theme: [] for theme in THEME_ORDER}
    for claim in claims:
        theme = primary_theme(claim)
        if theme is not None:
            grouped[theme].append(claim)
    return grouped


def _select_claims(claims: list[MethodologyClaim], max_items: int) -> list[MethodologyClaim]:
    source_priority = {"article": 0, "comment": 1, "interaction": 2, "image_ocr": 3}

    def score(claim: MethodologyClaim) -> int:
        ranking = (claim.raw or {}).get("ranking") or {}
        return int(ranking.get("score", 0))

    return sorted(
        claims,
        key=lambda claim: (
            source_priority.get(claim.source_type.value, 9),
            -score(claim),
            claim.claim_id,
        ),
    )[:max_items]
