# TGB Market V Skill v0.2

## Purpose
This skill summarizes the reviewed methodology of the target author based on accepted claims only.

## Scope and Non-advice Boundary
- 用于归纳该作者的方法论表达；
- 用于辅助分析其文章、评论和互动中的方法论线索；
- 不用于生成具体买卖建议；
- 不用于预测个股涨跌；
- 不替代人工判断。

## Source Policy
- Core rules come from accepted_review_ready_claims only.
- needs_edit claims are treated as uncertain context only.
- rejected and unreviewed claims must not be used as methodology.

## Core Methodology Rules

### 1. 量化影响
#### Rule quant-impact-market-structure: 量化影响需要纳入短线市场结构判断
- Rule: 量化交易会改变短线生态中的资金反馈速度、流动性分布和追涨/抛压结构；分析短线机会时，需要把量化带来的趋同交易、规避策略和盘中反馈纳入市场结构判断。
- When to use:
  - 当作者讨论量化冲击、盘中反馈或短线生态变化时。
- Do not use when:
  - 只有个股复盘细节、没有市场结构含义时。
- Evidence:
  - `claim-451671d03a6b0646`
  - `claim-9fa24ae5f750c243`
  - `claim-acaaf4cdb5d413ec`
  - `claim-0f01272d60e70e94`
  - `claim-1bd6f55ea1a4f94f`
- Caveats:
  - 不要把量化影响简化成单一利多或利空。

#### Rule quant-impact-not-single-direction: 不要把量化影响简化为单一利多或利空
- Rule: 量化影响更像市场结构变量，而不是固定方向结论；同样的量化参与，在不同成交额、指数环境和短线基础行情下会放大不同结果。
- When to use:
  - 当作者用量化解释市场强弱、承接或异动时。
- Do not use when:
  - 只有情绪表达、没有环境约束或结构含义时。
- Evidence:
  - `claim-46e97b566ea5469f`
  - `claim-6d4f584afbbfa9a8`
- Caveats:
  - 需要结合指数环境、成交额和短线基础行情共同判断。

#### Rule quant-impact-intraday-liquidity: 量化会影响盘中流动性与反馈节奏
- Rule: 量化会改变盘中流动性分布和反馈节奏，进而影响追涨、回落、回封和承接的时间结构；短线分析不能只看结果，还要看盘中反馈如何被量化重塑。
- When to use:
  - 当作者讨论盘中承接、追涨抛压、回封或反馈速度时。
- Do not use when:
  - 只有静态行情判断、没有盘中反馈信息时。
- Evidence:
  - `claim-ef4706e7c13c1cf0`
  - `claim-07c3a9a457b934fa`
  - `claim-66c0959e9ccbec5f`
  - `claim-080543f469028c23`
  - `claim-08b11dfb69c89a83`
- Caveats:
  - 更适合作为结构判断，不直接导出具体买卖指令。

### 2. 成交额 / 量能
#### Rule turnover-short-term-height: 成交额约束短线高度与持续性
- Rule: 短线高度、接力持续性和赚钱效应受整体成交额与活跃度约束；当成交额不足时，局部强势未必能外推为更高高度或更长持续性。
- When to use:
  - 当作者讨论成交额、接力高度、持续性和赚钱效应时。
- Do not use when:
  - 只有单只个股强弱、没有整体活跃度背景时。
- Evidence:
  - `claim-7c8abf7d84d3e9e3`
  - `claim-3a4023259a7db272`
  - `claim-8fa801c11064a31d`
  - `claim-1c80c1f2e95cd4d7`
  - `claim-41733260a45f4999`
- Caveats:
  - 成交额是环境变量，不是单独买卖结论。

#### Rule turnover-with-index-context: 放量和缩量必须结合指数环境与资金稀缺性判断
- Rule: 放量、缩量本身没有固定方向含义，必须结合指数环境、资金稀缺性和短线基础行情一起判断；同样的量能变化，在不同市场状态下对应的交易难度并不相同。
- When to use:
  - 当作者讨论放量、缩量、活跃度变化和环境切换时。
- Do not use when:
  - 只有量能描述、没有指数环境或资金背景时。
- Evidence:
  - `claim-c1c3ea0d9bd5e06a`
  - `claim-69c5debdc8794968`
  - `claim-58420714a6e676ce`
  - `claim-5b51bdf81cc631e4`
  - `claim-5db540e61b9c4ef6`
- Caveats:
  - 量能变化需要和市场状态配套解读。

### 3. 短线基础行情
#### Rule short-term-base-before-local-opportunity: 先判断短线整体环境，再判断局部机会
- Rule: 短线机会不能只看单只个股局部强弱，必须先判断整体赚钱效应、接力环境、轮动速度和容错空间；局部机会是否成立，取决于短线基础行情是否支持。
- When to use:
  - 当作者讨论连板、首板、接力和短线容错时。
- Do not use when:
  - 只有个股点评、没有整体短线生态含义时。
- Evidence:
  - `claim-27d6b8820885dee1`
  - `claim-38184d61ed1ba0ec`
  - `claim-6e6e4c1cd2740054`
  - `claim-c1c3ea0d9bd5e06a`
  - `claim-07c3a9a457b934fa`
- Caveats:
  - 局部龙头强势不等于整体短线环境健康。

#### Rule short-term-base-not-single-stock: 赚钱效应应看短线整体，而不是单个龙头或局部强势
- Rule: 短线赚钱效应应从整体接力质量、承接分布和亏钱效应扩散看，而不是把单个龙头或局部强势误判为整体环境转好。
- When to use:
  - 当作者讨论龙头、赚钱效应、亏钱效应或局部强势时。
- Do not use when:
  - 只有局部情绪评价、没有整体短线生态判断时。
- Evidence:
  - `claim-7ae975def66992ff`
  - `claim-1238b38b8a84fdc2`
  - `claim-6e1ff63c220e4af7`
  - `claim-a7fc27632cd96dbb`
  - `claim-0c5bf6d39d5a91fb`
- Caveats:
  - 龙头表现只能作为局部样本，不能替代整体环境判断。

#### Rule short-term-base-difficulty: 轮动速度、接力容错和指数成交额背景共同决定短线难度
- Rule: 短线难度由轮动速度、接力容错、指数环境和成交额背景共同决定；环境越差，越不能把局部强势误当成短线全面回暖。
- When to use:
  - 当作者讨论轮动速度、接力难度、承接或环境压制时。
- Do not use when:
  - 只有单点行情描述、没有环境变量之间的关系时。
- Evidence:
  - `claim-20690373fb54268c`
  - `claim-c3d92b374e2483d9`
  - `claim-dd1e19772005d0a3`
  - `claim-17a2bdd7c1e40103`
  - `claim-184a79cda8f754c6`
- Caveats:
  - 要和指数环境、成交额约束一起阅读。

### 4. 指数环境
#### Rule index-environment-risk-appetite: 指数环境影响短线承接与风险偏好
- Rule: 指数环境会改变短线承接、风险偏好和仓位容忍度；指数震荡、走弱或风险升高时，短线局部强势的可持续性要打折看待。
- When to use:
  - 当作者讨论指数、风险偏好、承接和短线容错时。
- Do not use when:
  - 只有单日涨跌陈述、没有承接或风险偏好含义时。
- Evidence:
  - `claim-6e6e4c1cd2740054`
  - `claim-ed117cf1071a1b82`
  - `claim-d3a0ff453c56ac8f`
  - `claim-1238b38b8a84fdc2`
  - `claim-1d43f83ee28113ea`
- Caveats:
  - 指数环境影响的是容错与承接，不应被机械当成唯一方向信号。

#### Rule index-environment-lower-certainty: 指数震荡或下行风险会降低局部题材确定性
- Rule: 指数震荡或下行风险抬升时，局部题材和个股的确定性会下降；即使存在热点，也要降低对持续性和高度的预期。
- When to use:
  - 当作者讨论热点持续性、局部题材或大盘压制时。
- Do not use when:
  - 只有个股复盘、没有指数背景约束时。
- Evidence:
  - `claim-27d6b8820885dee1`
  - `claim-86914b3d88bfe3e5`
  - `claim-c7b6d955b4e77c3e`
  - `claim-200c6551e0bfbb08`
  - `claim-83f5c83ef3a1a1bd`
- Caveats:
  - 局部题材强势需要放回大盘环境中重新评估。

#### Rule index-environment-layered-judgment: 指数、板块、个股需要分层判断
- Rule: 指数、板块和个股是不同层级的判断对象；分析时应先分清环境层、板块层和个股层，再决定哪些结论可以外推。
- When to use:
  - 当作者讨论大盘、板块、个股之间的关系时。
- Do not use when:
  - 只有情绪化环境判断、没有层级区分时。
- Evidence:
  - `claim-06d4d878c50bbbfc`
  - `claim-9f801ab88fb50785`
  - `claim-80871be657572a84`
- Caveats:
  - 不要用单层级强弱替代全部层级判断。

### 5. 风控
#### Rule risk-control-reduce-exposure: 环境不支持进攻时优先收缩风险暴露
- Rule: 当指数、成交额、短线基础行情或亏钱效应不支持进攻时，应优先收缩风险暴露、减少交易频率或降低仓位；而不是继续套用强环境下的节奏。
- When to use:
  - 当作者讨论弱市、回撤、亏钱效应、减仓或等待时。
- Do not use when:
  - 只有口号式风控提醒、没有环境依据时。
- Evidence:
  - `claim-a6d53867639e3666`
  - `claim-623e3b6b923fee7f`
  - `claim-430e333ecc703089`
  - `claim-9732e82b3495d755`
  - `claim-5518c5aa470f3538`
- Caveats:
  - 风控优先于进攻意愿。

#### Rule risk-control-missing-entry-premise: 买入前提不成立时应减少交易或等待
- Rule: 当买入前提、承接条件或流动性条件不成立时，应减少交易、延后出手或直接等待；而不是强行把弱环境里的反弹解释为可持续机会。
- When to use:
  - 当作者讨论买入前提、承接不足、流动性恶化或等待时。
- Do not use when:
  - 只有模糊的情绪宣泄、没有可识别前提条件时。
- Evidence:
  - `claim-2d86cadbf15dbc78`
  - `claim-e0eb1c78f60416f2`
  - `claim-2e949ad67d21ade0`
  - `claim-e90160e37a4ac7d1`
  - `claim-8b04518ea5d111a3`
- Caveats:
  - 这是一条执行约束，不是具体买卖建议。

#### Rule risk-control-weak-market-priority: 亏钱效应、流动性不足和弱市环境下风控优先
- Rule: 当亏钱效应扩散、流动性不足或弱市环境强化时，风控应优先于进攻；短线策略要先处理风险预算，再考虑机会筛选。
- When to use:
  - 当作者讨论弱市、防守、亏钱效应或仓位管理时。
- Do not use when:
  - 只有个股层面的抱怨、没有环境层的风险判断时。
- Evidence:
  - `claim-fbb0b89761bddf8b`
  - `claim-41fa00e960878b4d`
  - `claim-fdc0ada0a1053a95`
  - `claim-2d8d8202a083ae91`
  - `claim-d832417a28904324`
- Caveats:
  - 需要结合指数环境和成交额共同确认。

### 6. 牛熊切换
#### Rule bull-bear-no-single-rhythm: 牛市、熊市和切换期不能沿用同一套短线节奏
- Rule: 牛市、熊市和切换期的短线基础行情不同，不能简单沿用同一套短线节奏；进攻强度、容错预期和风险预算都要随环境调整。
- When to use:
  - 当作者讨论牛市、熊市、切换期和短线节奏时。
- Do not use when:
  - 只有泛泛的牛熊评论、没有策略差异判断时。
- Evidence:
  - `claim-0d18577396d6de47`
  - `claim-4401e71816e7b264`
  - `claim-24155837184cdad5`
  - `claim-8a89cc9f5b4d6a08`
  - `claim-3b63682df66aabca`
- Caveats:
  - 牛熊切换要和成交额、指数环境、赚钱效应一起看。

#### Rule bull-bear-combined-signals: 牛熊判断必须结合成交额、指数环境和赚钱/亏钱效应
- Rule: 牛熊判断不是单一标签，而是成交额、指数环境、赚钱效应和亏钱效应共同作用的结果；环境切换时，要重新确认哪些变量在主导市场。
- When to use:
  - 当作者讨论市场状态识别、牛熊判断或环境变化时。
- Do not use when:
  - 只有情绪化牛熊表述、没有变量支撑时。
- Evidence:
  - `claim-ed117cf1071a1b82`
  - `claim-c96ab1bcbaaaca45`
  - `claim-184d968de1ea8f8b`
  - `claim-5eb3fc02b6c6ddcd`
  - `claim-b532548766fbbf0e`
- Caveats:
  - 不要把牛熊判断当作单一、瞬时信号。

## How to Analyze a New Statement
1. 识别它更接近量化影响、成交额 / 量能、短线基础行情、指数环境、风控还是牛熊切换。
2. 判断表达是字面陈述，还是可能带有反讽、玩笑、夸张或故意说反话。
3. 如果语气或上下文不确定，标记为 `needs_human_check`，不要自动反向解释。
4. 只有 accepted evidence 支持的规则，才能作为强结论来源。
5. needs_edit 只能作为待确认背景，不能升级成核心规则。
6. 不输出买卖建议，不输出确定性承诺。

## Tone and Ambiguity Policy
- The author may use sarcasm, jokes, deliberate exaggeration, and intentionally wrong-sounding statements.
- Do not automatically reverse literal meaning.
- Mark ambiguous statements as `needs_human_check`.
- Require surrounding context before converting them into methodology.

## Output Rules
- 指出发言对应的主题。
- 优先引用 rule_id 和 claim_id，而不是直接复述长段原文。
- 清楚区分已确认方法论和待确认解释。
- 避免直接买卖建议。
- 避免宣称确定性结论。

## Limitations
- Corpus is partial.
- Some comment pages were inaccessible due to login/verification/app-open pages.
- Image OCR is not a reliable source unless explicitly reviewed.
- Skill v0.2 is based on first-round reviewed packs only.
