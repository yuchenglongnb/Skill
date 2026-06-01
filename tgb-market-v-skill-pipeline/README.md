# tgb-market-v-skill-pipeline

面向投资方法论 Skill 的结构化证据管线。项目计划采集淘股吧博主“等主人的猫”自
2023-01-15《情绪周期是否可靠的思考》起的主帖、评论、互动和图片证据，并保留可追溯的
原始数据。

## Milestone 1

当前版本提供项目骨架、数据模型、JSONL 存储层和 CLI 命令框架。

```powershell
python -m pip install -e ".[dev]"
pytest
python -m tgb_pipeline crawl-index
```

## Milestone 2：博客索引和主帖正文

当前版本已实现公开页面范围内的博客索引解析和主帖正文解析。默认目标配置位于
`configs/target.yaml`，其中包含目标作者公开博客主页和起始帖 URL。

```powershell
tgb-pipeline crawl-index --target-config configs/target.yaml --crawl-config configs/crawl.yaml
tgb-pipeline crawl-articles --target-config configs/target.yaml --crawl-config configs/crawl.yaml
```

生成文件：

```text
data/raw/tgb/articles_index.jsonl
data/raw/tgb/articles.jsonl
data/raw/tgb/images.jsonl
data/raw/tgb/html/blog_index_page_{n}.html
data/raw/tgb/html/{article_id}_page_1.html
```

`crawl-index` 和 `crawl-articles` 均使用去重写入，重复运行时可以断点续跑。正文图片会替换为
`[IMAGE: image_id]` 占位符，并单独写入 `images.jsonl`。本阶段不会下载图片，也不会执行 OCR。
`ArticleIndex` 仍是索引元数据主表；`Article` 上的 `mobile_url/tag/view_count/reply_count` 仅作为
从索引表填充的便捷冗余字段，完整元数据以 `ArticleIndex` 为 canonical source。

## Milestone 3A：Seed fallback

公开博客索引有时不会暴露完整主帖列表，导致 `crawl-index` 无法看到起始帖《情绪周期是否可靠的思考》。
本阶段支持从 `target.start_article.url` 构造 seed `ArticleIndex`，让后续 `crawl-articles` 和后续的
评论采集阶段在公开索引不完整时仍然有稳定输入。

```powershell
tgb-pipeline seed-start-article --target-config configs/target.yaml --crawl-config configs/crawl.yaml
tgb-pipeline crawl-index --target-config configs/target.yaml --crawl-config configs/crawl.yaml
tgb-pipeline crawl-articles --target-config configs/target.yaml --crawl-config configs/crawl.yaml
```

使用说明：

- `seed-start-article` 只根据 `target.start_article.url` 生成 seed `ArticleIndex` 并写入 `data/raw/tgb/articles_index.jsonl`。
- 当公开索引缺失起始帖且 `allow_seed_article_fallback: true` 时，`crawl-index` 会自动写入 seed 记录，而不是直接报错退出。
- 当公开索引正常包含起始帖时，仍优先使用索引页解析结果，不改变原有逻辑。

## Milestone 3B：评论分页、角色标注和互动过滤

本阶段新增了评论分页解析、评论图片元信息提取、作者角色标注、Aoch 专项索引和互动过滤。评论抓取不依赖公开博客主页，而是基于 `articles_index.jsonl` 中的 `mobile_url` 生成评论分页 URL，因此也可以直接接在 seed fallback 之后运行。

```powershell
tgb-pipeline crawl-comments --target-config configs/target.yaml --crawl-config configs/crawl.yaml
tgb-pipeline filter-comments --target-config configs/target.yaml --crawl-config configs/crawl.yaml
```

生成文件：

```text
data/raw/tgb/comments_all.jsonl
data/raw/tgb/comments.jsonl
data/raw/tgb/aoch_discussions.jsonl
data/raw/tgb/interactions.jsonl
data/raw/tgb/html/{article_id}_comments_page_{n}.html
```

行为说明：

- `crawl-comments` 会抓取评论分页 HTML、写入 `comments_all.jsonl`，并把评论中的图片元信息追加到 `images.jsonl`。
- `filter-comments` 会先标注作者角色，再筛选目标作者互动评论、输出 `interactions.jsonl`，同时把 `Aoch` 评论单独写入 `aoch_discussions.jsonl`。
- 普通成员的低价值评论默认不进入互动语料，但原始评论仍保留在 `comments_all.jsonl` 中，方便审计和后续复核。

## 数据边界

- 目标范围从 2023-01-15《情绪周期是否可靠的思考》开始，包含之后的目标作者主帖。
- 主帖、评论和互动均保留 `raw` 载荷；包含原文的实体额外保留 `raw_content`。
- 图片使用 `ImageAsset` 独立建模，是一等证据源，不作为正文附件简单丢弃。
- OCR 使用 `ImageOCR.raw_text` 和 `ImageOCR.normalized_text` 单独保存，不拼接进正文。
- 普通论坛成员评论会落入原始存储，但默认不进入最终语料；只有目标作者参与互动后才允许进入。
- `Aoch` 是重点成员，通过 `AuthorRole.AOCH`、`Comment.is_aoch` 和 `eligible_for_aoch_corpus` 单独标记，后续建立专门索引。

## 合规注意事项

- 实现采集器前应确认淘股吧服务条款、robots.txt 和页面访问规则。
- 使用低并发、限速、断点续跑和重试上限，避免对站点造成额外负担。
- 只采集研究所需的公开内容，不绕过登录、验证码、访问控制或反自动化措施。
- Seed fallback 只使用用户显式配置的公开 URL，不绕过登录、验证码、访问限制。
- 保留来源 URL、原始载荷、HTML 快照和证据关联，方便审计、纠错和后续删除。
- 对外导出语料前应复核个人信息、版权边界和引用范围。

## CLI 框架

当前命令：

```text
crawl-index
crawl-articles
seed-start-article
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

1. 实现评论采集、互动关系归档和评论准入规则。
2. 建立 Aoch 专项索引和评论证据链。
3. 提取、下载并校验图片，接入 OCR，保留图片证据链。
4. 导出可审计语料，抽取方法论主张并生成 Skill 输入材料。
