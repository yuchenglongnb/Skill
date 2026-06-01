# tgb-market-v-skill-pipeline

面向投资方法论 Skill 的结构化证据管线。项目计划采集淘股吧博主“等主人的猫”自
2023-01-15《情绪周期是否可靠的思考》起的主帖、评论、互动和图片证据，并保留可追溯的
原始数据。

## Milestone 1

当前版本只提供项目骨架、数据模型、JSONL 存储层和 CLI 命令框架，不包含完整爬虫。

```powershell
python -m pip install -e ".[dev]"
pytest
python -m tgb_pipeline crawl-index
```

## 数据边界

- 目标范围从 2023-01-15《情绪周期是否可靠的思考》开始，包含之后的目标作者主帖。
- 主帖、评论和互动均保留 `raw` 载荷；包含原文的实体额外保留 `raw_content`。
- 图片使用 `ImageAsset` 独立建模，是一等证据源，不作为正文附件简单丢弃。
- OCR 使用 `ImageOCR.raw_text` 和 `ImageOCR.normalized_text` 单独保存，不拼接进正文。
- 普通论坛成员评论会落入原始存储，但默认不进入最终语料；只有目标作者参与互动后才允许进入。
- `Aoch` 是重点成员，通过 `AuthorRole.AOCH` 和 `Comment.is_aoch` 单独标记，后续建立专门索引。

## 合规注意事项

- 实现采集器前应确认淘股吧服务条款、robots.txt 和页面访问规则。
- 使用低并发、限速、断点续跑和重试上限，避免对站点造成额外负担。
- 只采集研究所需的公开内容，不绕过登录、验证码、访问控制或反自动化措施。
- 保留来源 URL、原始载荷和证据关联，方便审计、纠错和后续删除。
- 对外导出语料前应复核个人信息、版权边界和引用范围。

## CLI 框架

已预留以下阶段命令：

```text
crawl-index
crawl-articles
crawl-comments
filter-comments
extract-images
download-images
ocr-images
export-corpus
extract-claims
build-skill
```

## 后续里程碑

1. 实现页面发现、主帖和评论采集，生成原始 JSONL。
2. 建立互动关系、评论准入规则和 Aoch 专项索引。
3. 提取、下载并校验图片，接入 OCR，保留图片证据链。
4. 导出可审计语料，抽取方法论主张并生成 Skill 输入材料。

