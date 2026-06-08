# 等主人的猫：阶段性方法论画像 v0.2

## 数据状态
- accepted claims: 248
- needs_edit claims: 100
- rejected claims: 91
- reviewed packs: quant_impact_top100, turnover_top100, short_term_base_top100, risk_control_top80, bull_bear_top80
- unreviewed claims: 6113
- accepted recheck candidates: 81

## Rule Summary
### 量化影响

- `quant-impact-market-structure` 量化影响需要纳入短线市场结构判断
  - rule_text: 量化交易会改变短线生态中的资金反馈速度、流动性分布和追涨/抛压结构；分析短线机会时，需要把量化带来的趋同交易、规避策略和盘中反馈纳入市场结构判断。
  - evidence_claim_ids: claim-451671d03a6b0646, claim-9fa24ae5f750c243, claim-acaaf4cdb5d413ec, claim-0f01272d60e70e94, claim-1bd6f55ea1a4f94f
- `quant-impact-not-single-direction` 不要把量化影响简化为单一利多或利空
  - rule_text: 量化影响更像市场结构变量，而不是固定方向结论；同样的量化参与，在不同成交额、指数环境和短线基础行情下会放大不同结果。
  - evidence_claim_ids: claim-46e97b566ea5469f, claim-6d4f584afbbfa9a8
- `quant-impact-intraday-liquidity` 量化会影响盘中流动性与反馈节奏
  - rule_text: 量化会改变盘中流动性分布和反馈节奏，进而影响追涨、回落、回封和承接的时间结构；短线分析不能只看结果，还要看盘中反馈如何被量化重塑。
  - evidence_claim_ids: claim-ef4706e7c13c1cf0, claim-07c3a9a457b934fa, claim-66c0959e9ccbec5f, claim-080543f469028c23, claim-08b11dfb69c89a83

### 成交额 / 量能

- `turnover-short-term-height` 成交额约束短线高度与持续性
  - rule_text: 短线高度、接力持续性和赚钱效应受整体成交额与活跃度约束；当成交额不足时，局部强势未必能外推为更高高度或更长持续性。
  - evidence_claim_ids: claim-7c8abf7d84d3e9e3, claim-3a4023259a7db272, claim-8fa801c11064a31d, claim-1c80c1f2e95cd4d7, claim-41733260a45f4999
- `turnover-with-index-context` 放量和缩量必须结合指数环境与资金稀缺性判断
  - rule_text: 放量、缩量本身没有固定方向含义，必须结合指数环境、资金稀缺性和短线基础行情一起判断；同样的量能变化，在不同市场状态下对应的交易难度并不相同。
  - evidence_claim_ids: claim-c1c3ea0d9bd5e06a, claim-69c5debdc8794968, claim-58420714a6e676ce, claim-5b51bdf81cc631e4, claim-5db540e61b9c4ef6

### 短线基础行情

- `short-term-base-before-local-opportunity` 先判断短线整体环境，再判断局部机会
  - rule_text: 短线机会不能只看单只个股局部强弱，必须先判断整体赚钱效应、接力环境、轮动速度和容错空间；局部机会是否成立，取决于短线基础行情是否支持。
  - evidence_claim_ids: claim-27d6b8820885dee1, claim-38184d61ed1ba0ec, claim-6e6e4c1cd2740054, claim-c1c3ea0d9bd5e06a, claim-07c3a9a457b934fa
- `short-term-base-not-single-stock` 赚钱效应应看短线整体，而不是单个龙头或局部强势
  - rule_text: 短线赚钱效应应从整体接力质量、承接分布和亏钱效应扩散看，而不是把单个龙头或局部强势误判为整体环境转好。
  - evidence_claim_ids: claim-7ae975def66992ff, claim-1238b38b8a84fdc2, claim-6e1ff63c220e4af7, claim-a7fc27632cd96dbb, claim-0c5bf6d39d5a91fb
- `short-term-base-difficulty` 轮动速度、接力容错和指数成交额背景共同决定短线难度
  - rule_text: 短线难度由轮动速度、接力容错、指数环境和成交额背景共同决定；环境越差，越不能把局部强势误当成短线全面回暖。
  - evidence_claim_ids: claim-20690373fb54268c, claim-c3d92b374e2483d9, claim-dd1e19772005d0a3, claim-17a2bdd7c1e40103, claim-184a79cda8f754c6

### 指数环境

- `index-environment-risk-appetite` 指数环境影响短线承接与风险偏好
  - rule_text: 指数环境会改变短线承接、风险偏好和仓位容忍度；指数震荡、走弱或风险升高时，短线局部强势的可持续性要打折看待。
  - evidence_claim_ids: claim-6e6e4c1cd2740054, claim-ed117cf1071a1b82, claim-d3a0ff453c56ac8f, claim-1238b38b8a84fdc2, claim-1d43f83ee28113ea
- `index-environment-lower-certainty` 指数震荡或下行风险会降低局部题材确定性
  - rule_text: 指数震荡或下行风险抬升时，局部题材和个股的确定性会下降；即使存在热点，也要降低对持续性和高度的预期。
  - evidence_claim_ids: claim-27d6b8820885dee1, claim-86914b3d88bfe3e5, claim-c7b6d955b4e77c3e, claim-200c6551e0bfbb08, claim-83f5c83ef3a1a1bd
- `index-environment-layered-judgment` 指数、板块、个股需要分层判断
  - rule_text: 指数、板块和个股是不同层级的判断对象；分析时应先分清环境层、板块层和个股层，再决定哪些结论可以外推。
  - evidence_claim_ids: claim-06d4d878c50bbbfc, claim-9f801ab88fb50785, claim-80871be657572a84

### 风控

- `risk-control-reduce-exposure` 环境不支持进攻时优先收缩风险暴露
  - rule_text: 当指数、成交额、短线基础行情或亏钱效应不支持进攻时，应优先收缩风险暴露、减少交易频率或降低仓位；而不是继续套用强环境下的节奏。
  - evidence_claim_ids: claim-a6d53867639e3666, claim-623e3b6b923fee7f, claim-430e333ecc703089, claim-9732e82b3495d755, claim-5518c5aa470f3538
- `risk-control-missing-entry-premise` 买入前提不成立时应减少交易或等待
  - rule_text: 当买入前提、承接条件或流动性条件不成立时，应减少交易、延后出手或直接等待；而不是强行把弱环境里的反弹解释为可持续机会。
  - evidence_claim_ids: claim-2d86cadbf15dbc78, claim-e0eb1c78f60416f2, claim-2e949ad67d21ade0, claim-e90160e37a4ac7d1, claim-8b04518ea5d111a3
- `risk-control-weak-market-priority` 亏钱效应、流动性不足和弱市环境下风控优先
  - rule_text: 当亏钱效应扩散、流动性不足或弱市环境强化时，风控应优先于进攻；短线策略要先处理风险预算，再考虑机会筛选。
  - evidence_claim_ids: claim-fbb0b89761bddf8b, claim-41fa00e960878b4d, claim-fdc0ada0a1053a95, claim-2d8d8202a083ae91, claim-d832417a28904324

### 牛熊切换

- `bull-bear-no-single-rhythm` 牛市、熊市和切换期不能沿用同一套短线节奏
  - rule_text: 牛市、熊市和切换期的短线基础行情不同，不能简单沿用同一套短线节奏；进攻强度、容错预期和风险预算都要随环境调整。
  - evidence_claim_ids: claim-0d18577396d6de47, claim-4401e71816e7b264, claim-24155837184cdad5, claim-8a89cc9f5b4d6a08, claim-3b63682df66aabca
- `bull-bear-combined-signals` 牛熊判断必须结合成交额、指数环境和赚钱/亏钱效应
  - rule_text: 牛熊判断不是单一标签，而是成交额、指数环境、赚钱效应和亏钱效应共同作用的结果；环境切换时，要重新确认哪些变量在主导市场。
  - evidence_claim_ids: claim-ed117cf1071a1b82, claim-c96ab1bcbaaaca45, claim-184d968de1ea8f8b, claim-5eb3fc02b6c6ddcd, claim-b532548766fbbf0e

## Representative Accepted Evidence

### 量化影响

- claim_id: `claim-ef4706e7c13c1cf0`
  - raw_excerpt: 量化采取规避策略，那热门标不是减少100股，而是减少20-30%的买盘，外加反向抛压，因为量化本身多转空。
  - article_id: 2fQt29pQ3Pa
  - source_type: article
  - method_tags: 量化影响
- claim_id: `claim-451671d03a6b0646`
  - raw_excerpt: 美国和我国都因为量化趋同交易出现了股灾。
  - article_id: 25VmrtPmuWI
  - source_type: article
  - method_tags: 量化影响
- claim_id: `claim-9fa24ae5f750c243`
  - raw_excerpt: 进入正题，上面的情况不是孤例，而是市场长期在大量量化交易影响下的演变结果。
  - article_id: 1Zn2UmelLMJ
  - source_type: article
  - method_tags: 量化影响
- claim_id: `claim-acaaf4cdb5d413ec`
  - raw_excerpt: 所以，别再这么傻问怎么狙击量化，低纬战高维，我们都是虫子。
  - article_id: 2ghvnc9bHeR
  - source_type: article
  - method_tags: 量化影响
- claim_id: `claim-07c3a9a457b934fa`
  - raw_excerpt: 机构做多那天，会把追涨量化和短线资金都带倒一处，别的地方如果有短线获利盘，则存在流动性不足。
  - article_id: 2jbi0efIsof
  - source_type: comment
  - method_tags: 短线基础行情, 量化影响

### 成交额 / 量能

- claim_id: `claim-c1c3ea0d9bd5e06a`
  - raw_excerpt: 成交量，有或无，也不是大婶口中放量就好，短线大部分放量都不好，随便买意味着没有稀缺性，怎么涨？
  - article_id: 2jbi0efIsof
  - source_type: article
  - method_tags: 成交额, 短线基础行情
- claim_id: `claim-7c8abf7d84d3e9e3`
  - raw_excerpt: 之所以用换手不用金额，是为体现个股本身精确的活跃度排名，竞价可以用成交量跟金额直接转换，换手率=成交量/自由流通盘*100，大家的数值都是在0-100之间，标准化对比，更能体现全市场活跃度的排列。
  - article_id: 2ohHCnLXtP8
  - source_type: article
  - method_tags: 成交额, 数字化/标准化
- claim_id: `claim-69c5debdc8794968`
  - raw_excerpt: 而是量化卖出开得好+放量有对手盘，特别是它高配的地方，买入相对低估的。
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - method_tags: 成交额, 量化影响, 买入触发, 卖出条件
- claim_id: `claim-3a4023259a7db272`
  - raw_excerpt: 1. 指数要高开，是需要量能支撑的，以示不是跌多了惜售，而是有增量推动。
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - method_tags: 成交额, 指数环境
- claim_id: `claim-58420714a6e676ce`
  - raw_excerpt: 缩量拉升的上板或者炸板都不碰，因为指数大概率缩量低开，盘中必有回踩，一踩就炸，那天也说了，似乎量化已经把这些走势算计在内。
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - method_tags: 成交额, 指数环境, 量化影响

### 短线基础行情

- claim_id: `claim-27d6b8820885dee1`
  - raw_excerpt: 举一反四，今天竞价指数低开，如果知道震荡的情况下，你还去冲短线佬多的地方吗？
  - article_id: 2jbi0efIsof
  - source_type: article
  - method_tags: 指数环境, 短线基础行情
- claim_id: `claim-38184d61ed1ba0ec`
  - raw_excerpt: 这里不是独立板块，而是整个短线先后手阵型的对立，让人感觉资金专买你不要的，互卷互拆台。
  - article_id: 1Zn2UmelLMJ
  - source_type: article
  - method_tags: 短线基础行情
- claim_id: `claim-6e6e4c1cd2740054`
  - raw_excerpt: 如果底层观点成立，那，就要把短线分析和统计都独立于指数，否则会自受其乱。
  - article_id: 1VvuASpPpMr
  - source_type: article
  - method_tags: 指数环境, 短线基础行情
- claim_id: `claim-7ae975def66992ff`
  - raw_excerpt: 赚钱效应应体现在短线整体，而不是局部，某某龙头还没挂。
  - article_id: 1VvuASpPpMr
  - source_type: article
  - method_tags: 短线基础行情, 赚钱效应, 龙头
- claim_id: `claim-c1c3ea0d9bd5e06a`
  - raw_excerpt: 成交量，有或无，也不是大婶口中放量就好，短线大部分放量都不好，随便买意味着没有稀缺性，怎么涨？
  - article_id: 2jbi0efIsof
  - source_type: article
  - method_tags: 成交额, 短线基础行情

### 指数环境

- claim_id: `claim-27d6b8820885dee1`
  - raw_excerpt: 举一反四，今天竞价指数低开，如果知道震荡的情况下，你还去冲短线佬多的地方吗？
  - article_id: 2jbi0efIsof
  - source_type: article
  - method_tags: 指数环境, 短线基础行情
- claim_id: `claim-6e6e4c1cd2740054`
  - raw_excerpt: 如果底层观点成立，那，就要把短线分析和统计都独立于指数，否则会自受其乱。
  - article_id: 1VvuASpPpMr
  - source_type: article
  - method_tags: 指数环境, 短线基础行情
- claim_id: `claim-ed117cf1071a1b82`
  - raw_excerpt: 等卖点，没问题的，毕竟昨天指数牛市量，大概率有低吸资金。
  - article_id: 2jbi0efIsof
  - source_type: article
  - method_tags: 指数环境, 买入触发, 牛熊切换
- claim_id: `claim-d3a0ff453c56ac8f`
  - raw_excerpt: 正因为这样，昨天市场开出来爆量，量化预计指数不好，它故意去买些没游资潜伏的，安诺其顶了个新高大阳线。
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - method_tags: 指数环境, 量化影响
- claim_id: `claim-06d4d878c50bbbfc`
  - raw_excerpt: 如果不能指数两连阳实体暴涨，板块之间肯定资金拉扯，这是量化市场的一种常态。
  - article_id: 2jbi0efIsof
  - source_type: comment
  - method_tags: 指数环境, 量化影响

### 风控

- claim_id: `claim-fbb0b89761bddf8b`
  - raw_excerpt: 别行情涨出熊心豹子胆再去杠杆加仓，那时筹码贵，回撤快，倾家荡产的玩法。
  - article_id: 2bWeZGDSi07
  - source_type: article
  - method_tags: 风控
- claim_id: `claim-41fa00e960878b4d`
  - raw_excerpt: 我觉得持股都不是问题，关键你要知道什么情况持股，什么情况风控甚至割肉。
  - article_id: 2jbi0efIsof
  - source_type: comment
  - method_tags: 风控
- claim_id: `claim-a6d53867639e3666`
  - raw_excerpt: 市场走弱的情况下，如果助跌，会有很多人类止损追跌，踩踏是量化控制不了的，它只能买一边，等于引导了主观空头。
  - article_id: 25VmrtPmuWI
  - source_type: comment
  - method_tags: 量化影响, 风控
- claim_id: `claim-623e3b6b923fee7f`
  - raw_excerpt: 今年1月的下跌，几乎打穿了所有量化的风控线，所以小票反弹之前，它们头寸大降，仓位都去了抱团大象。
  - article_id: 28ACjvWeEjl
  - source_type: comment
  - method_tags: 量化影响, 仓位管理, 风控
- claim_id: `claim-fdc0ada0a1053a95`
  - raw_excerpt: 玩这种系统开发，是要推理出什么条件会走成那样，暂时没有好的想法，所以先风控。
  - article_id: 25VmrtPmuWI
  - source_type: comment
  - method_tags: 风控

### 牛熊切换

- claim_id: `claim-ed117cf1071a1b82`
  - raw_excerpt: 等卖点，没问题的，毕竟昨天指数牛市量，大概率有低吸资金。
  - article_id: 2jbi0efIsof
  - source_type: article
  - method_tags: 指数环境, 买入触发, 牛熊切换
- claim_id: `claim-0d18577396d6de47`
  - raw_excerpt: 癌股历来的牛市都是水牛，有钱就涨，涨到某些人怕了从天而降的掌法，拼裸泳。
  - article_id: 2bWeZGDSi07
  - source_type: article
  - method_tags: 牛熊切换
- claim_id: `claim-c96ab1bcbaaaca45`
  - raw_excerpt: 不中听说句，这么多大婶能看出牛市来了，真是牛市也会一波三折。
  - article_id: 2bWeZGDSi07
  - source_type: article
  - method_tags: 牛熊切换
- claim_id: `claim-4401e71816e7b264`
  - raw_excerpt: 认知的一致，是没法垫高市场成本，牛市结构的筹码堆叠就无从说起。
  - article_id: 2bWeZGDSi07
  - source_type: article
  - method_tags: 市场结构, 牛熊切换
- claim_id: `claim-184d968de1ea8f8b`
  - raw_excerpt: 如果是牛市，第一次暴力杀透了，其实不要想太多，概率上是修复概率大的，关键就是修复的能量。
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - method_tags: 牛熊切换

## Accepted Claims Recheck Candidates

### 量化影响

- claim_id: `claim-acaaf4cdb5d413ec`
  - article_id: 2ghvnc9bHeR
  - source_type: article
  - recheck_reason: ['colloquial_or_exaggerated']
  - raw_excerpt: 所以，别再这么傻问怎么狙击量化，低纬战高维，我们都是虫子。
  - review_notes: 保留：属于量化影响下的交易机制或市场结构判断。
- claim_id: `claim-66c0959e9ccbec5f`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 因为今天整体市场向上，所以增量都是追涨的性质，量化价格都不用维护，最多打点折，资金出来又可以去别的地方扫板。
  - review_notes: 保留：属于量化影响下的交易机制或市场结构判断。
- claim_id: `claim-d3a0ff453c56ac8f`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 正因为这样，昨天市场开出来爆量，量化预计指数不好，它故意去买些没游资潜伏的，安诺其顶了个新高大阳线。
  - review_notes: 保留：属于量化影响与市场环境关系的判断。
- claim_id: `claim-080543f469028c23`
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 首先，前面拉升一直有资金利用量化追涨，实际上那个高位并不是人类认可的位置。
  - review_notes: 保留：属于量化影响下的交易机制或市场结构判断。
- claim_id: `claim-08b11dfb69c89a83`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 去看看1009盘中对科技的看法，说了昨天如果不是补跌开盘，会被量化用逆因子杀跌的。
  - review_notes: 保留：属于量化影响下的交易机制或市场结构判断。

### 成交额 / 量能

- claim_id: `claim-c1c3ea0d9bd5e06a`
  - article_id: 2jbi0efIsof
  - source_type: article
  - recheck_reason: ['colloquial_or_exaggerated', 'rhetorical_or_question']
  - raw_excerpt: 成交量，有或无，也不是大婶口中放量就好，短线大部分放量都不好，随便买意味着没有稀缺性，怎么涨？
  - review_notes: 保留：属于成交额或量能变化影响交易机制的判断。
- claim_id: `claim-7c8abf7d84d3e9e3`
  - article_id: 2ohHCnLXtP8
  - source_type: article
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 之所以用换手不用金额，是为体现个股本身精确的活跃度排名，竞价可以用成交量跟金额直接转换，换手率=成交量/自由流通盘*100，大家的数值都是在0-100之间，标准化对比，更能体现全市场活跃度的排列。
  - review_notes: 保留：属于可沉淀的成交额或量能方法论判断。
- claim_id: `claim-5b51bdf81cc631e4`
  - article_id: 1VvuASpPpMr
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 本身指数在高位，缩量午后很容易跳水的，所以比较风险。
  - review_notes: 保留：属于成交额或量能条件下的风控判断。
- claim_id: `claim-86914b3d88bfe3e5`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 今天肯定缩量(竞价)，所以，指数如果高开，大概率就是震荡。
  - review_notes: 保留：属于成交额或量能变化与市场环境关系的判断。
- claim_id: `claim-8859e6bbf84f1014`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 但是缩量上板，如果午后指数不举，它就会反复炸。
  - review_notes: 保留：属于成交额或量能条件下的执行规则判断。

### 短线基础行情

- claim_id: `claim-27d6b8820885dee1`
  - article_id: 2jbi0efIsof
  - source_type: article
  - recheck_reason: ['rhetorical_or_question', 'strong_context_dependency']
  - raw_excerpt: 举一反四，今天竞价指数低开，如果知道震荡的情况下，你还去冲短线佬多的地方吗？
  - review_notes: 保留：属于弱市短线的风控或仓位判断。
- claim_id: `claim-38184d61ed1ba0ec`
  - article_id: 1Zn2UmelLMJ
  - source_type: article
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 这里不是独立板块，而是整个短线先后手阵型的对立，让人感觉资金专买你不要的，互卷互拆台。
  - review_notes: 保留：属于短线基础行情或接力机制的判断。
- claim_id: `claim-6ad31981dcfeccf9`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 而不是这个强那个强，还好今天短线板票开得不高，但凡市场看好点，全部卖给你。
  - review_notes: 保留：属于短线基础行情或接力机制的判断。
- claim_id: `claim-bb1daf51bc0582d7`
  - article_id: 24O3rehPcWv
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 盘前短线佬肯定高配板票、大票（因为昨晚集中开吹），今天收官日，跟去年3个长假收官一样，卖给你。
  - review_notes: 保留：属于短线基础行情或接力机制的判断。
- claim_id: `claim-c243a8147e4a2acb`
  - article_id: 25VmrtPmuWI
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 以往这里可能是我买点，既然它不是龙一，在市场不接力和指数可能会冲高回落的情况下，早上流动性好就卖。
  - review_notes: 保留：属于弱市短线的风控或仓位判断。

### 指数环境

- claim_id: `claim-ed117cf1071a1b82`
  - article_id: 2jbi0efIsof
  - source_type: article
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 等卖点，没问题的，毕竟昨天指数牛市量，大概率有低吸资金。
  - review_notes: 保留：属于牛熊切换下市场状态识别或环境变化判断。
- claim_id: `claim-859ed6774a56538f`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 这次交易制度跟之前牛市不一样，例如，一年纪不能买创业板&+，那增量市场，主板和ohters可能会形成两个交易风格。
  - review_notes: 保留：属于牛熊切换下市场状态识别或环境变化判断。
- claim_id: `claim-450d050cafe52c0d`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 指数正常今天跌也跌不多的，你觉得牛市，周末就别太空舱。
  - review_notes: 保留：属于不同市场状态下的执行原则。

### 风控

- claim_id: `claim-2d8d8202a083ae91`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - recheck_reason: ['rhetorical_or_question']
  - raw_excerpt: 出门爆砸半小时，后面散户后知后觉就会跟着“纪律止损”，你们想想以往行情不好，是不是忍一整天，很容易1:30~2:00剁雕？
  - review_notes: 保留：属于弱市环境下的风控原则。
- claim_id: `claim-5393587bdc8a4b5e`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - recheck_reason: ['rhetorical_or_question']
  - raw_excerpt: 这种打法账户波动很大的，碰上连续冰冰的日子，一波回撤本季没了80%，你还坚持吗?
  - review_notes: 保留：属于弱市环境下的风控原则。
- claim_id: `claim-2d86cadbf15dbc78`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - recheck_reason: ['too_short']
  - raw_excerpt: 要风控不是现在，要么一早不买。
  - review_notes: 保留：属于减少交易、等待或规避风险的执行原则。
- claim_id: `claim-254fb4cfc0f002f9`
  - article_id: 1VvuASpPpMr
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 今天涨停开1.47%，明知道整体承接不好，昨天83个涨停，全是先手，就先风控。
  - review_notes: 保留：属于弱市环境下的风控原则。

### 牛熊切换

- claim_id: `claim-0d18577396d6de47`
  - article_id: 2bWeZGDSi07
  - source_type: article
  - recheck_reason: ['colloquial_or_exaggerated']
  - raw_excerpt: 癌股历来的牛市都是水牛，有钱就涨，涨到某些人怕了从天而降的掌法，拼裸泳。
  - review_notes: 保留：属于牛熊环境对交易机制影响的判断。
- claim_id: `claim-c96ab1bcbaaaca45`
  - article_id: 2bWeZGDSi07
  - source_type: article
  - recheck_reason: ['colloquial_or_exaggerated']
  - raw_excerpt: 不中听说句，这么多大婶能看出牛市来了，真是牛市也会一波三折。
  - review_notes: 保留：属于牛熊切换下市场状态识别或环境变化判断。
- claim_id: `claim-96f858b0bfdd7619`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - recheck_reason: ['strong_context_dependency']
  - raw_excerpt: 所有的牛市都以股灾结束，希望这次不一样，让大家财富永续昌隆吧。
  - review_notes: 保留：属于不同市场环境下的风控原则。
- claim_id: `claim-89eb0e2b4494fe23`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - recheck_reason: ['rhetorical_or_question']
  - raw_excerpt: 以现在淘县客左冲右核的本事，平台段就退市一大半，本金没了，牛市主升浪来了跟你有什么关系吗？
  - review_notes: 保留：属于不同市场环境下的风控原则。
- claim_id: `claim-5eb3fc02b6c6ddcd`
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - recheck_reason: ['too_short']
  - raw_excerpt: 牛市多长阴，没长阴不是牛市。
  - review_notes: 保留：属于牛熊切换下市场状态识别或环境变化判断。

## Needs-edit Worklist

### 量化影响

- claim_id: `claim-01f3c877548cd251`
  - raw_excerpt: 但当早上量化资金发现全是抄底资金的时候，它就先不卖，让抄底资金买，高位再卖，是不是价格就高很多，还不用自己抬轿。
  - article_id: 2jbi0efIsof
  - source_type: comment
  - method_tags: 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-171e0cd2096eef89`
  - raw_excerpt: 有下影线是正常的，不是散户抄的底，应该是量化买的。
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - method_tags: 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-55c8271702b5d2ff`
  - raw_excerpt: 那个就是量化席位，我不是说了之前发掘某些形态的轮动，盘面挖出来，人家盘中已经进去了，次日卖给我这种。
  - article_id: 2jbi0efIsof
  - source_type: comment
  - method_tags: 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-5d6a72a7232bf40b`
  - raw_excerpt: 龙虎榜3家机构，净买入1.52亿，不是做T，大概率是主观多头的机构，不是量化。
  - article_id: 2jbi0efIsof
  - source_type: comment
  - method_tags: 量化影响, 买入触发
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-76f055a577e5743a`
  - raw_excerpt: 不用问了，还是那句，午后如果量化策略自动减仓30%，这批短线票腥风血雨的。
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - method_tags: 短线基础行情, 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。

### 成交额 / 量能

- claim_id: `claim-135f828da00f1296`
  - raw_excerpt: 如果你信V，今天早盘放量恐慌的板块，午后指数跳水点就是买点。
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - method_tags: 成交额, 指数环境
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。
- claim_id: `claim-694dc8a4fb0e17bb`
  - raw_excerpt: 因为封板票多是没量的，昨日涨停和昨日连板在跌，能量放量，肯定是追卖或者炸板。
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - method_tags: 成交额, 短线基础行情
  - review_notes: 待编辑：盘中特指较强，需要抽象为成交额或量能机制判断。
- claim_id: `claim-9f5b2f4a90da37fd`
  - raw_excerpt: 所以整个上午指数放了点量，短线那批票反而大幅度缩量。
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - method_tags: 成交额, 指数环境, 短线基础行情
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。
- claim_id: `claim-c20cd2462f4a5f36`
  - raw_excerpt: 还有个事，就是现在指数右肩缩量，今天如果再高开，是跳空摸前面3万亿成交的套牢日的。
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - method_tags: 成交额, 指数环境
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。
- claim_id: `claim-cc8ad369db5b642f`
  - raw_excerpt: 开得高是没办法，因为市场持续缩量，所以外盘和消息面影响很大，动不动就大高开大低开，指数大阴大阳。
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - method_tags: 成交额, 指数环境
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。

### 短线基础行情

- claim_id: `claim-6d64a9229d147ed7`
  - raw_excerpt: 现学现卖，“行情不好是因为短线客接不住，接得住行情就会好。
  - article_id: 24O3rehPcWv
  - source_type: article
  - method_tags: 短线基础行情
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性短线方法论表述。
- claim_id: `claim-6b7b0cd7472e8ce9`
  - raw_excerpt: 实际上，要操作也应该昨天买科技，共振指数修复，而不是今天去接力。
  - article_id: 2jbi0efIsof
  - source_type: comment
  - method_tags: 指数环境, 短线基础行情
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的短线执行规则表述。
- claim_id: `claim-76f055a577e5743a`
  - raw_excerpt: 不用问了，还是那句，午后如果量化策略自动减仓30%，这批短线票腥风血雨的。
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - method_tags: 短线基础行情, 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-1d74e64bd2040ab0`
  - raw_excerpt: 小金属今天没先手有风险的，很多短线资金昨天上车，如果午后指数不好回落炸几个板，情况又好像周四周五的
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - method_tags: 指数环境, 短线基础行情, 买入触发
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的风控判断。
- claim_id: `claim-2edec5c39f0403ff`
  - raw_excerpt: 关键，成交快速放，第一波拉升之前6%+，也就是市场整体态度是红盘让你砸，显然不是短线佬加钱买上去的，最厉害就是坑挚爱亲朋，长期卖一把买五忽悠瘸了。
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - method_tags: 短线基础行情
  - review_notes: 待确认：原句口语化且带有嘲讽色彩，需要人工结合上下文确认。

### 指数环境

- claim_id: `claim-6b7b0cd7472e8ce9`
  - raw_excerpt: 实际上，要操作也应该昨天买科技，共振指数修复，而不是今天去接力。
  - article_id: 2jbi0efIsof
  - source_type: comment
  - method_tags: 指数环境, 短线基础行情
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的短线执行规则表述。
- claim_id: `claim-135f828da00f1296`
  - raw_excerpt: 如果你信V，今天早盘放量恐慌的板块，午后指数跳水点就是买点。
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - method_tags: 成交额, 指数环境
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。
- claim_id: `claim-1d74e64bd2040ab0`
  - raw_excerpt: 小金属今天没先手有风险的，很多短线资金昨天上车，如果午后指数不好回落炸几个板，情况又好像周四周五的
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - method_tags: 指数环境, 短线基础行情, 买入触发
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的风控判断。
- claim_id: `claim-64b006f936c2bb96`
  - raw_excerpt: 情绪指数里面包含远端短线和翘板票，都说了昨天很多是顺势撬开，实际是卖点不是买点。
  - article_id: 24O3rehPcWv
  - source_type: comment
  - method_tags: 情绪周期, 指数环境, 短线基础行情, 反核
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的短线环境判断。
- claim_id: `claim-88f3a06648d1f267`
  - raw_excerpt: 讲真，今天指数卦象并不好，因为权重护盘，大多次日要补跌，哪怕市场资金想做，量化买了一手大象，来对手盘立刻给你万象奔腾。
  - article_id: 21ZIusToJzV
  - source_type: comment
  - method_tags: 指数环境, 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。

### 风控

- claim_id: `claim-cbee30f7327ef4d2`
  - raw_excerpt: 如果量化自身的风控线被自己打破了（你理解成猫仔锤到它风控也可以），就会开启揍自己模式，比你先砸盘，带着雕王们一起揍自己。
  - article_id: 28ACjvWeEjl
  - source_type: comment
  - method_tags: 量化影响, 风控
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-efc4ff8c194fe3ee`
  - raw_excerpt: 同时所谓超额收益，就是被打死那边逼着止损，资金出来以后，又要去拉升那边追高，因为你没有
  - article_id: 21mulzOf8Yb
  - source_type: comment
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性风控规则。
- claim_id: `claim-2b50815b715120c8`
  - raw_excerpt: 最终目的，写好识别算法，这个票出来，弹窗，有没有风控触发，有没有诱多，是否配合行情风格。
  - article_id: 2jbi0efIsof
  - source_type: comment
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要压缩为中性风控方法论表述。
- claim_id: `claim-b4a07794e0776819`
  - raw_excerpt: 要么跟些躺赢老师讨论一下躺赢技术，昨天如何在昨日早盘跳水买到全部不回撤的票，今天如何在300红盘的行情躺赢？
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - method_tags: 风控
  - review_notes: 待确认：原句明显带有调侃语气，需要人工结合上下文确认。
- claim_id: `claim-2acf6176d6d59118`
  - raw_excerpt: 一环扣一环的演变，所以，风控不见得坏。
  - article_id: 25VmrtPmuWI
  - source_type: comment
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要压缩为中性风控方法论表述。

### 牛熊切换

- claim_id: `claim-4fb37e6610f88183`
  - raw_excerpt: 我不确定这是不是牛市，如果是牛市，一生不会遇到多少次。
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - method_tags: 牛熊切换
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性牛熊切换方法论表述。
- claim_id: `claim-9ee6f4c04ec7e9c5`
  - raw_excerpt: 癌股的牛市，最后大部分人都赔得倾家荡产，宝总不是孤例。
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - method_tags: 牛熊切换
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性风控规则。
- claim_id: `claim-03c257757050e834`
  - raw_excerpt: 说了牛市全部老鸟玩不过菜市场大妈，因为知道得太多了。
  - article_id: 1VvuASpPpMr
  - source_type: comment
  - method_tags: 牛熊切换
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-897ffdeb9f7eb078`
  - raw_excerpt: 今天不是证明了牛市熊市，秒天地板是没啥区别的？
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - method_tags: 牛熊切换
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-a9a023dd2f05d434`
  - raw_excerpt: 大牛市十大致富招数，大牛市最好的操作就是躺赢，大牛市最好就是拼上仓位，大牛市老鸟最容易收割小鸟。
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - method_tags: 仓位管理, 牛熊切换
  - review_notes: 待编辑：盘中特指较强，需要抽象为市场状态下的执行原则。

## 主题之间的关系

- 量化影响如何改变短线生态：量化资金会改变资金反馈速度、流动性分布和盘中承接结构。
- 成交额如何约束短线高度：成交活跃度不足时，短线高度、接力持续性和赚钱效应都会受限。
- 指数环境如何影响短线基础行情：指数环境会直接影响短线承接、风险偏好和容错空间。
- 弱市或熊市为什么需要风控优先：当亏钱效应扩散、流动性不足时，仓位与交易频率都应先收缩。
- 牛熊切换下为什么不能简单套用同一套短线策略：环境切换会改变风险收益比、执行节奏和可用模式。

## 排除边界

- rejected 类型总结：
  - 拒绝：表达过于碎片化，缺少可沉淀判断。: 28
  - 拒绝：更像盘中特指或复盘背景，不进入方法论。: 22
  - 拒绝：更像背景信息或行情评论，不进入方法论。: 13
  - 拒绝：表述偏泛，不能独立构成牛熊切换方法论。: 7
  - 拒绝：表述偏泛，不能独立构成短线方法论。: 5
  - 拒绝：更像背景信息或铺垫，不进入方法论。: 4
  - 拒绝：表述偏泛，不能独立构成方法论。: 4
  - 拒绝：与已有表达重复，缺少新增方法论信息。: 2
- 泛句、碎句、反讽、上下文不足不进入核心方法论。
- needs_edit 只作为待确认素材，不直接写成核心规则。
- rejected / unreviewed 不进入 Skill v0.2 的核心方法论。
