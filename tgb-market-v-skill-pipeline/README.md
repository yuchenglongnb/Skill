# tgb-market-v-skill-pipeline

面向投资方法论 Skill 的结构化证据管线。项目围绕淘股吧目标作者“等主人的猫”的公开主帖、评论、互动与图片证据，构建可追溯的采集、过滤、抽取、人工复核和 Skill v0 生成流程。

## 核心原则

- 只处理公开可访问内容；
- 不绕过登录、验证码或访问限制；
- 保留 raw 数据、HTML 快照和证据索引；
- 图片和 OCR 作为独立证据源，不混入正文；
- 普通成员观点不进入目标作者方法论；
- Aoch 单独标记；
- 反讽、打趣、故意说反话的内容必须人工确认；
- Skill v0 不提供买卖建议，不预测个股涨跌。

## Quick Start

```powershell
python -m pip install -e ".[dev]"
pytest
python -m compileall -q src tests
```

## 数据采集

```powershell
python -m tgb_pipeline ingest-article-seeds --target-config configs/target.yaml --crawl-config configs/crawl.yaml
python -m tgb_pipeline crawl-articles --target-config configs/target.yaml --crawl-config configs/crawl.yaml
python -m tgb_pipeline crawl-comments --target-config configs/target.yaml --crawl-config configs/crawl.yaml
python -m tgb_pipeline filter-comments --target-config configs/target.yaml --crawl-config configs/crawl.yaml
python -m tgb_pipeline export-corpus --target-config configs/target.yaml --crawl-config configs/crawl.yaml
```

## 评论补全

```powershell
python -m tgb_pipeline plan-comment-completion --target-config configs/target.yaml --crawl-config configs/crawl.yaml
python -m tgb_pipeline run-comment-completion-plan --target-config configs/target.yaml --crawl-config configs/crawl.yaml --plan data/interim/tgb/comment_completion_plan.json
```

## Claim 抽取与降噪

```powershell
python -m tgb_pipeline extract-claims --target-config configs/target.yaml --crawl-config configs/crawl.yaml
python -m tgb_pipeline build-review-ready-claims --target-config configs/target.yaml --crawl-config configs/crawl.yaml
```

## Review-ready 人工复核

```powershell
python -m tgb_pipeline build-default-review-packs --target-config configs/target.yaml --crawl-config configs/crawl.yaml
python -m tgb_pipeline apply-review-pack --target-config configs/target.yaml --crawl-config configs/crawl.yaml --pack data/processed/tgb/review_packs/quant_impact_top100.yaml
python -m tgb_pipeline review-ready-claims --target-config configs/target.yaml --crawl-config configs/crawl.yaml --apply
python -m tgb_pipeline audit-review-encoding --target-config configs/target.yaml --crawl-config configs/crawl.yaml
```

注意：`apply-review-pack`、`review-ready-claims --apply`、`audit-review-encoding` 必须串行执行，不能并行。

## Build Skill v0

```powershell
python -m tgb_pipeline build-skill-v0 --target-config configs/target.yaml --crawl-config configs/crawl.yaml
```

输出：

```text
skill_output/tgb_market_v_skill/SKILL.md
skill_output/tgb_market_v_skill/methodology_profile.md
skill_output/tgb_market_v_skill/evidence_index.jsonl
skill_output/tgb_market_v_skill/needs_edit_evidence_index.jsonl
skill_output/tgb_market_v_skill/methodology_rules.jsonl
skill_output/tgb_market_v_skill/rule_evidence_map.jsonl
skill_output/tgb_market_v_skill/skill_quality_report.md
skill_output/tgb_market_v_skill/needs_edit_worklist.md
data/processed/tgb/review_packs/accepted_recheck_v0_2.yaml
reports/review_packs/accepted_recheck_v0_2.md
skill_output/tgb_market_v_skill/uncertainty_policy.md
skill_output/tgb_market_v_skill/review_summary.md
```

Skill v0.2 separates abstract rules from raw evidence.

- `SKILL.md` contains abstract methodology rules only.
- `rule_evidence_map.jsonl` contains raw excerpts and claim evidence.
- `accepted_recheck_v0_2.yaml` contains accepted claims that may be too colloquial, sarcastic, or context-dependent and should be manually revisited.
- needs_edit 会被单独输出为待确认材料，不会混入核心规则。

## 当前阶段

已完成五个核心 review pack：

- quant_impact_top100
- turnover_top100
- short_term_base_top100
- risk_control_top80
- bull_bear_top80

Skill v0 基于 accepted claims 生成；needs_edit 只作为不确定证据；rejected/unreviewed 不进入核心规则。

## 编码审计

```powershell
python -m tgb_pipeline audit-review-encoding --target-config configs/target.yaml --crawl-config configs/crawl.yaml
python -m tgb_pipeline audit-text-encoding --target-config configs/target.yaml --crawl-config configs/crawl.yaml
```

## 合规边界

- 不绕过登录、验证码或访问限制；
- 不抓取非公开内容；
- 不输出投资建议；
- 不预测个股涨跌；
- 不把反讽/打趣内容自动解释为相反意思；
- 不把普通成员观点混入目标作者方法论。
