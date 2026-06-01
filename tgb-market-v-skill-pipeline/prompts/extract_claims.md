# Extract Claims

- 只从原文提取，不杜撰，不补写未出现的逻辑。
- 区分原文、归纳和推断；原文必须保留 raw excerpt。
- 如果证据来自 OCR，明确标记为低证据等级，除非后续人工校验。
- 输出结构化 JSON，保留 source ids、source type、method tags、entities 和 review status。
- 普通成员无互动评论不进入目标作者主 claim，Aoch 观点不得混入目标作者方法论。

