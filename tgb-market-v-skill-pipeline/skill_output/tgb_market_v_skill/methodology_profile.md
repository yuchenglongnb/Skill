# 等主人的猫：阶段性方法论画像 v0.1

## 数据状态
- accepted claims: 248
- needs_edit claims: 100
- rejected claims: 91
- reviewed packs: quant_impact_top100, turnover_top100, short_term_base_top100, risk_control_top80, bull_bear_top80
- unreviewed claims: 6113

## 核心主题
### 量化影响

#### Rule Summary
1. 量化影响需要纳入短线市场结构判断
   - rule_id: `quant-impact-overview`
   - rule_text: 量化交易会改变短线生态中的资金反馈速度、流动性分布和追涨/抛压结构；分析短线机会时，需要把量化带来的趋同交易、规避策略和盘中反馈纳入市场结构判断。
   - evidence_claim_ids: claim-ef4706e7c13c1cf0, claim-451671d03a6b0646, claim-9fa24ae5f750c243, claim-acaaf4cdb5d413ec, claim-07c3a9a457b934fa
2. 量化影响规则 1
   - rule_id: `quant-impact-1`
   - rule_text: 在评估量化影响时，应将以下判断纳入市场结构分析：美国和我国都因为量化趋同交易出现了股灾。
   - evidence_claim_ids: claim-451671d03a6b0646
3. 量化影响规则 2
   - rule_id: `quant-impact-2`
   - rule_text: 在评估量化影响时，应将以下判断纳入市场结构分析：进入正题，上面的情况不是孤例，而是市场长期在大量量化交易影响下的演变结果。
   - evidence_claim_ids: claim-9fa24ae5f750c243
4. 量化影响规则 3
   - rule_id: `quant-impact-3`
   - rule_text: 在评估量化影响时，应将以下判断纳入市场结构分析：所以，别再这么傻问怎么狙击量化，低纬战高维，我们都是虫子。
   - evidence_claim_ids: claim-acaaf4cdb5d413ec
5. 量化影响规则 4
   - rule_id: `quant-impact-4`
   - rule_text: 在评估量化影响时，应将以下判断纳入市场结构分析：机构做多那天，会把追涨量化和短线资金都带倒一处，别的地方如果有短线获利盘，则存在流动性不足。
   - evidence_claim_ids: claim-07c3a9a457b934fa
6. 量化影响规则 5
   - rule_id: `quant-impact-5`
   - rule_text: 在评估量化影响时，应将以下判断纳入市场结构分析：因为量化深度绑定市场后，由于它的指增策略和横跳不空仓策略，导致市场会在很长一段时间，无论涨跌都是接近的成交水平。
   - evidence_claim_ids: claim-0f01272d60e70e94
7. 量化影响规则 6
   - rule_id: `quant-impact-6`
   - rule_text: 在评估量化影响时，应将以下判断纳入市场结构分析：而量化高抛低吸的中间差价，实际上就是躺着的自然人付了，因为你持股实际价值变低了。
   - evidence_claim_ids: claim-1bd6f55ea1a4f94f
8. 量化影响规则 7
   - rule_id: `quant-impact-7`
   - rule_text: 在评估量化影响时，应将以下判断纳入市场结构分析：而且量化操作时候也不可能完全识别其它买卖盘是不是量化。
   - evidence_claim_ids: claim-46791f2cd9e4e4a2

#### Representative Accepted Evidence
- claim_id: `claim-ef4706e7c13c1cf0`
  - article_id: 2fQt29pQ3Pa
  - source_type: article
  - raw_excerpt: 量化采取规避策略，那热门标不是减少100股，而是减少20-30%的买盘，外加反向抛压，因为量化本身多转空。
  - method_tags: 量化影响
- claim_id: `claim-451671d03a6b0646`
  - article_id: 25VmrtPmuWI
  - source_type: article
  - raw_excerpt: 美国和我国都因为量化趋同交易出现了股灾。
  - method_tags: 量化影响
- claim_id: `claim-9fa24ae5f750c243`
  - article_id: 1Zn2UmelLMJ
  - source_type: article
  - raw_excerpt: 进入正题，上面的情况不是孤例，而是市场长期在大量量化交易影响下的演变结果。
  - method_tags: 量化影响
- claim_id: `claim-acaaf4cdb5d413ec`
  - article_id: 2ghvnc9bHeR
  - source_type: article
  - raw_excerpt: 所以，别再这么傻问怎么狙击量化，低纬战高维，我们都是虫子。
  - method_tags: 量化影响
- claim_id: `claim-07c3a9a457b934fa`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 机构做多那天，会把追涨量化和短线资金都带倒一处，别的地方如果有短线获利盘，则存在流动性不足。
  - method_tags: 短线基础行情, 量化影响

#### Needs-edit / Caveats
- claim_id: `claim-01f3c877548cd251`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 但当早上量化资金发现全是抄底资金的时候，它就先不卖，让抄底资金买，高位再卖，是不是价格就高很多，还不用自己抬轿。
  - method_tags: 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-171e0cd2096eef89`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 有下影线是正常的，不是散户抄的底，应该是量化买的。
  - method_tags: 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-55c8271702b5d2ff`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 那个就是量化席位，我不是说了之前发掘某些形态的轮动，盘面挖出来，人家盘中已经进去了，次日卖给我这种。
  - method_tags: 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-5d6a72a7232bf40b`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 龙虎榜3家机构，净买入1.52亿，不是做T，大概率是主观多头的机构，不是量化。
  - method_tags: 量化影响, 买入触发
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-76f055a577e5743a`
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - raw_excerpt: 不用问了，还是那句，午后如果量化策略自动减仓30%，这批短线票腥风血雨的。
  - method_tags: 短线基础行情, 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。

### 成交额 / 量能

#### Rule Summary
1. 成交额约束短线高度与持续性
   - rule_id: `turnover-overview`
   - rule_text: 成交额与量能不是简单的放量好、缩量坏；需要结合指数环境、短线基础行情和资金稀缺性判断。短线高度、接力持续性和赚钱效应都受整体成交活跃度约束。
   - evidence_claim_ids: claim-c1c3ea0d9bd5e06a, claim-7c8abf7d84d3e9e3, claim-3a4023259a7db272, claim-5b51bdf81cc631e4, claim-5fe2969caeba4bdc
2. 成交额 / 量能规则 1
   - rule_id: `turnover-1`
   - rule_text: 在评估成交额与量能时，应优先检查：之所以用换手不用金额，是为体现个股本身精确的活跃度排名，竞价可以用成交量跟金额直接转换，换手率=成交量/自由流通盘*100，大家的数值都是在0-100之间，标准化对比，更能体现全市场活跃度的排列。
   - evidence_claim_ids: claim-7c8abf7d84d3e9e3
3. 成交额 / 量能规则 2
   - rule_id: `turnover-2`
   - rule_text: 在评估成交额与量能时，应优先检查：1. 指数要高开，是需要量能支撑的，以示不是跌多了惜售，而是有增量推动。
   - evidence_claim_ids: claim-3a4023259a7db272
4. 成交额 / 量能规则 3
   - rule_id: `turnover-3`
   - rule_text: 在评估成交额与量能时，应优先检查：本身指数在高位，缩量午后很容易跳水的，所以比较风险。
   - evidence_claim_ids: claim-5b51bdf81cc631e4
5. 成交额 / 量能规则 4
   - rule_id: `turnover-4`
   - rule_text: 在评估成交额与量能时，应优先检查：当时第二天指数缺口低开，但放量，资金抄底，所以有了低开高走。
   - evidence_claim_ids: claim-5fe2969caeba4bdc
6. 成交额 / 量能规则 5
   - rule_id: `turnover-5`
   - rule_text: 在评估成交额与量能时，应优先检查：今天肯定缩量(竞价)，所以，指数如果高开，大概率就是震荡。
   - evidence_claim_ids: claim-86914b3d88bfe3e5
7. 成交额 / 量能规则 6
   - rule_id: `turnover-6`
   - rule_text: 在评估成交额与量能时，应优先检查：但是缩量上板，如果午后指数不举，它就会反复炸。
   - evidence_claim_ids: claim-8859e6bbf84f1014
8. 成交额 / 量能规则 7
   - rule_id: `turnover-7`
   - rule_text: 在评估成交额与量能时，应优先检查：分析是基于市场特征的，近期创业板成交额占比高，基本它压制指数，无论怎样轮动整体市场都被锤，不是高低切可以解决。
   - evidence_claim_ids: claim-8fa801c11064a31d

#### Representative Accepted Evidence
- claim_id: `claim-c1c3ea0d9bd5e06a`
  - article_id: 2jbi0efIsof
  - source_type: article
  - raw_excerpt: 成交量，有或无，也不是大婶口中放量就好，短线大部分放量都不好，随便买意味着没有稀缺性，怎么涨？
  - method_tags: 成交额, 短线基础行情
- claim_id: `claim-7c8abf7d84d3e9e3`
  - article_id: 2ohHCnLXtP8
  - source_type: article
  - raw_excerpt: 之所以用换手不用金额，是为体现个股本身精确的活跃度排名，竞价可以用成交量跟金额直接转换，换手率=成交量/自由流通盘*100，大家的数值都是在0-100之间，标准化对比，更能体现全市场活跃度的排列。
  - method_tags: 成交额, 数字化/标准化
- claim_id: `claim-3a4023259a7db272`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 1. 指数要高开，是需要量能支撑的，以示不是跌多了惜售，而是有增量推动。
  - method_tags: 成交额, 指数环境
- claim_id: `claim-5b51bdf81cc631e4`
  - article_id: 1VvuASpPpMr
  - source_type: comment
  - raw_excerpt: 本身指数在高位，缩量午后很容易跳水的，所以比较风险。
  - method_tags: 成交额, 指数环境
- claim_id: `claim-5fe2969caeba4bdc`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 当时第二天指数缺口低开，但放量，资金抄底，所以有了低开高走。
  - method_tags: 成交额, 指数环境

#### Needs-edit / Caveats
- claim_id: `claim-135f828da00f1296`
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - raw_excerpt: 如果你信V，今天早盘放量恐慌的板块，午后指数跳水点就是买点。
  - method_tags: 成交额, 指数环境
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。
- claim_id: `claim-694dc8a4fb0e17bb`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 因为封板票多是没量的，昨日涨停和昨日连板在跌，能量放量，肯定是追卖或者炸板。
  - method_tags: 成交额, 短线基础行情
  - review_notes: 待编辑：盘中特指较强，需要抽象为成交额或量能机制判断。
- claim_id: `claim-9f5b2f4a90da37fd`
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - raw_excerpt: 所以整个上午指数放了点量，短线那批票反而大幅度缩量。
  - method_tags: 成交额, 指数环境, 短线基础行情
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。
- claim_id: `claim-c20cd2462f4a5f36`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 还有个事，就是现在指数右肩缩量，今天如果再高开，是跳空摸前面3万亿成交的套牢日的。
  - method_tags: 成交额, 指数环境
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。
- claim_id: `claim-cc8ad369db5b642f`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 开得高是没办法，因为市场持续缩量，所以外盘和消息面影响很大，动不动就大高开大低开，指数大阴大阳。
  - method_tags: 成交额, 指数环境
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。

### 短线基础行情

#### Rule Summary
1. 先判断短线基础行情，再判断局部机会
   - rule_id: `short-term-base-overview`
   - rule_text: 短线机会不能只看个股局部强弱；应先判断整体赚钱效应、接力环境、轮动速度和指数/成交额背景，再评估个股高度与容错。
   - evidence_claim_ids: claim-27d6b8820885dee1, claim-38184d61ed1ba0ec, claim-6e6e4c1cd2740054, claim-7ae975def66992ff, claim-20690373fb54268c
2. 短线基础行情规则 1
   - rule_id: `short-term-base-1`
   - rule_text: 在判断短线基础行情时，应重点关注：这里不是独立板块，而是整个短线先后手阵型的对立，让人感觉资金专买你不要的，互卷互拆台。
   - evidence_claim_ids: claim-38184d61ed1ba0ec
3. 短线基础行情规则 2
   - rule_id: `short-term-base-2`
   - rule_text: 在判断短线基础行情时，应重点关注：如果底层观点成立，那，就要把短线分析和统计都独立于指数，否则会自受其乱。
   - evidence_claim_ids: claim-6e6e4c1cd2740054
4. 短线基础行情规则 3
   - rule_id: `short-term-base-3`
   - rule_text: 在判断短线基础行情时，应重点关注：赚钱效应应体现在短线整体，而不是局部，某某龙头还没挂。
   - evidence_claim_ids: claim-7ae975def66992ff
5. 短线基础行情规则 4
   - rule_id: `short-term-base-4`
   - rule_text: 在判断短线基础行情时，应重点关注：所以连板率非常丑，做接力的连接12天盘，轮动超快。
   - evidence_claim_ids: claim-20690373fb54268c
6. 短线基础行情规则 5
   - rule_id: `short-term-base-5`
   - rule_text: 在判断短线基础行情时，应重点关注：指数向下，假设短线不是自己独立的数板行情，明天溢价有限，搞不好被绕柱。
   - evidence_claim_ids: claim-1238b38b8a84fdc2
7. 短线基础行情规则 6
   - rule_id: `short-term-base-6`
   - rule_text: 在判断短线基础行情时，应重点关注：因为我好几年前就把短线和指数分开跟踪，尽量去还原市场。
   - evidence_claim_ids: claim-1d43f83ee28113ea
8. 短线基础行情规则 7
   - rule_id: `short-term-base-7`
   - rule_text: 在判断短线基础行情时，应重点关注：做热门票的资金跟指数ETF不是同一批资金，但是指数是载体，指数弱了，大概率短线货锚着指数杀跌或者补涨的。
   - evidence_claim_ids: claim-20a73a4c0a41d291

#### Representative Accepted Evidence
- claim_id: `claim-27d6b8820885dee1`
  - article_id: 2jbi0efIsof
  - source_type: article
  - raw_excerpt: 举一反四，今天竞价指数低开，如果知道震荡的情况下，你还去冲短线佬多的地方吗？
  - method_tags: 指数环境, 短线基础行情
- claim_id: `claim-38184d61ed1ba0ec`
  - article_id: 1Zn2UmelLMJ
  - source_type: article
  - raw_excerpt: 这里不是独立板块，而是整个短线先后手阵型的对立，让人感觉资金专买你不要的，互卷互拆台。
  - method_tags: 短线基础行情
- claim_id: `claim-6e6e4c1cd2740054`
  - article_id: 1VvuASpPpMr
  - source_type: article
  - raw_excerpt: 如果底层观点成立，那，就要把短线分析和统计都独立于指数，否则会自受其乱。
  - method_tags: 指数环境, 短线基础行情
- claim_id: `claim-7ae975def66992ff`
  - article_id: 1VvuASpPpMr
  - source_type: article
  - raw_excerpt: 赚钱效应应体现在短线整体，而不是局部，某某龙头还没挂。
  - method_tags: 短线基础行情, 赚钱效应, 龙头
- claim_id: `claim-20690373fb54268c`
  - article_id: 1Vgsye6eK36
  - source_type: article
  - raw_excerpt: 所以连板率非常丑，做接力的连接12天盘，轮动超快。
  - method_tags: 短线基础行情

#### Needs-edit / Caveats
- claim_id: `claim-6d64a9229d147ed7`
  - article_id: 24O3rehPcWv
  - source_type: article
  - raw_excerpt: 现学现卖，“行情不好是因为短线客接不住，接得住行情就会好。
  - method_tags: 短线基础行情
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性短线方法论表述。
- claim_id: `claim-6b7b0cd7472e8ce9`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 实际上，要操作也应该昨天买科技，共振指数修复，而不是今天去接力。
  - method_tags: 指数环境, 短线基础行情
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的短线执行规则表述。
- claim_id: `claim-1d74e64bd2040ab0`
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - raw_excerpt: 小金属今天没先手有风险的，很多短线资金昨天上车，如果午后指数不好回落炸几个板，情况又好像周四周五的
  - method_tags: 指数环境, 短线基础行情, 买入触发
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的风控判断。
- claim_id: `claim-2edec5c39f0403ff`
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - raw_excerpt: 关键，成交快速放，第一波拉升之前6%+，也就是市场整体态度是红盘让你砸，显然不是短线佬加钱买上去的，最厉害就是坑挚爱亲朋，长期卖一把买五忽悠瘸了。
  - method_tags: 短线基础行情
  - review_notes: 待确认：原句口语化且带有嘲讽色彩，需要人工结合上下文确认。
- claim_id: `claim-64b006f936c2bb96`
  - article_id: 24O3rehPcWv
  - source_type: comment
  - raw_excerpt: 情绪指数里面包含远端短线和翘板票，都说了昨天很多是顺势撬开，实际是卖点不是买点。
  - method_tags: 情绪周期, 指数环境, 短线基础行情, 反核
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的短线环境判断。

### 指数环境

#### Rule Summary
1. 指数环境影响短线承接与风险偏好
   - rule_id: `index-environment-overview`
   - rule_text: 指数环境会影响短线资金的承接、风险偏好和仓位选择；指数震荡或下行风险较大时，应降低对局部题材强度和持续性的确定性判断。
   - evidence_claim_ids: claim-ed117cf1071a1b82, claim-859ed6774a56538f, claim-edbf9735a3e0312c, claim-450d050cafe52c0d, claim-80871be657572a84
2. 指数环境规则 1
   - rule_id: `index-environment-1`
   - rule_text: 在判断指数环境影响时，应优先考虑：这次交易制度跟之前牛市不一样，例如，一年纪不能买创业板&+，那增量市场，主板和ohters可能会形成两个交易风格。
   - evidence_claim_ids: claim-859ed6774a56538f
3. 指数环境规则 2
   - rule_id: `index-environment-2`
   - rule_text: 在判断指数环境影响时，应优先考虑：要是指数有一定震荡风险（市场态度模糊），那先减仓风控。
   - evidence_claim_ids: claim-edbf9735a3e0312c
4. 指数环境规则 3
   - rule_id: `index-environment-3`
   - rule_text: 在判断指数环境影响时，应优先考虑：指数正常今天跌也跌不多的，你觉得牛市，周末就别太空舱。
   - evidence_claim_ids: claim-450d050cafe52c0d
5. 指数环境规则 4
   - rule_id: `index-environment-4`
   - rule_text: 在判断指数环境影响时，应优先考虑：指数＞板块＞个股，牛市，熊市，都一样的。
   - evidence_claim_ids: claim-80871be657572a84

#### Representative Accepted Evidence
- claim_id: `claim-ed117cf1071a1b82`
  - article_id: 2jbi0efIsof
  - source_type: article
  - raw_excerpt: 等卖点，没问题的，毕竟昨天指数牛市量，大概率有低吸资金。
  - method_tags: 指数环境, 买入触发, 牛熊切换
- claim_id: `claim-859ed6774a56538f`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 这次交易制度跟之前牛市不一样，例如，一年纪不能买创业板&+，那增量市场，主板和ohters可能会形成两个交易风格。
  - method_tags: 指数环境, 牛熊切换
- claim_id: `claim-450d050cafe52c0d`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 指数正常今天跌也跌不多的，你觉得牛市，周末就别太空舱。
  - method_tags: 指数环境, 牛熊切换
- claim_id: `claim-80871be657572a84`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 指数＞板块＞个股，牛市，熊市，都一样的。
  - method_tags: 指数环境, 牛熊切换
- claim_id: `claim-edbf9735a3e0312c`
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - raw_excerpt: 要是指数有一定震荡风险（市场态度模糊），那先减仓风控。
  - method_tags: 指数环境, 风控

#### Needs-edit / Caveats
- claim_id: `claim-01c29b11d81a8401`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 牛市多长阴，今天创业板长了15CM，调整可以20CM的。
  - method_tags: 指数环境, 牛熊切换
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性牛熊切换方法论表述。

### 风控

#### Rule Summary
1. 环境不支持进攻时优先收缩风险暴露
   - rule_id: `risk-control-overview`
   - rule_text: 当指数、成交额、短线基础行情或亏钱效应不支持进攻时，应优先降低仓位、减少交易或等待，而不是强行套用强行情打法。
   - evidence_claim_ids: claim-fbb0b89761bddf8b, claim-2d86cadbf15dbc78, claim-41fa00e960878b4d, claim-fdc0ada0a1053a95, claim-2d8d8202a083ae91
2. 风控规则 1
   - rule_id: `risk-control-1`
   - rule_text: 在执行风控时，应优先遵守：要风控不是现在，要么一早不买。
   - evidence_claim_ids: claim-2d86cadbf15dbc78
3. 风控规则 2
   - rule_id: `risk-control-2`
   - rule_text: 在执行风控时，应优先遵守：我觉得持股都不是问题，关键你要知道什么情况持股，什么情况风控甚至割肉。
   - evidence_claim_ids: claim-41fa00e960878b4d
4. 风控规则 3
   - rule_id: `risk-control-3`
   - rule_text: 在执行风控时，应优先遵守：玩这种系统开发，是要推理出什么条件会走成那样，暂时没有好的想法，所以先风控。
   - evidence_claim_ids: claim-fdc0ada0a1053a95
5. 风控规则 4
   - rule_id: `risk-control-4`
   - rule_text: 在执行风控时，应优先遵守：出门爆砸半小时，后面散户后知后觉就会跟着“纪律止损”，你们想想以往行情不好，是不是忍一整天，很容易1:30~2:00剁雕。
   - evidence_claim_ids: claim-2d8d8202a083ae91
6. 风控规则 5
   - rule_id: `risk-control-5`
   - rule_text: 在执行风控时，应优先遵守：防回撤不是一句空话，你要在一个区间里面把得住才行的。
   - evidence_claim_ids: claim-d832417a28904324
7. 风控规则 6
   - rule_id: `risk-control-6`
   - rule_text: 在执行风控时，应优先遵守：这种是涉及做与不做的问题，相当于上了一道操作的风控锁。
   - evidence_claim_ids: claim-e0eb1c78f60416f2
8. 风控规则 7
   - rule_id: `risk-control-7`
   - rule_text: 在执行风控时，应优先遵守：风控意识一定要有，否则1-2笔大亏的交易让你清零。
   - evidence_claim_ids: claim-f21c0a5161d8c8ab

#### Representative Accepted Evidence
- claim_id: `claim-fbb0b89761bddf8b`
  - article_id: 2bWeZGDSi07
  - source_type: article
  - raw_excerpt: 别行情涨出熊心豹子胆再去杠杆加仓，那时筹码贵，回撤快，倾家荡产的玩法。
  - method_tags: 风控
- claim_id: `claim-41fa00e960878b4d`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 我觉得持股都不是问题，关键你要知道什么情况持股，什么情况风控甚至割肉。
  - method_tags: 风控
- claim_id: `claim-fdc0ada0a1053a95`
  - article_id: 25VmrtPmuWI
  - source_type: comment
  - raw_excerpt: 玩这种系统开发，是要推理出什么条件会走成那样，暂时没有好的想法，所以先风控。
  - method_tags: 风控
- claim_id: `claim-2d8d8202a083ae91`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 出门爆砸半小时，后面散户后知后觉就会跟着“纪律止损”，你们想想以往行情不好，是不是忍一整天，很容易1:30~2:00剁雕？
  - method_tags: 风控
- claim_id: `claim-d832417a28904324`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 防回撤不是一句空话，你要在一个区间里面把得住才行的。
  - method_tags: 风控

#### Needs-edit / Caveats
- claim_id: `claim-efc4ff8c194fe3ee`
  - article_id: 21mulzOf8Yb
  - source_type: comment
  - raw_excerpt: 同时所谓超额收益，就是被打死那边逼着止损，资金出来以后，又要去拉升那边追高，因为你没有
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性风控规则。
- claim_id: `claim-2b50815b715120c8`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 最终目的，写好识别算法，这个票出来，弹窗，有没有风控触发，有没有诱多，是否配合行情风格。
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要压缩为中性风控方法论表述。
- claim_id: `claim-b4a07794e0776819`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 要么跟些躺赢老师讨论一下躺赢技术，昨天如何在昨日早盘跳水买到全部不回撤的票，今天如何在300红盘的行情躺赢？
  - method_tags: 风控
  - review_notes: 待确认：原句明显带有调侃语气，需要人工结合上下文确认。
- claim_id: `claim-2acf6176d6d59118`
  - article_id: 25VmrtPmuWI
  - source_type: comment
  - raw_excerpt: 一环扣一环的演变，所以，风控不见得坏。
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要压缩为中性风控方法论表述。
- claim_id: `claim-c1e8b75141c09c82`
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - raw_excerpt: 正常要加个风控机制，估计没想到还有一日涨几十倍的。
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要抽象为亏钱效应或止损盘风险机制判断。

### 牛熊切换

#### Rule Summary
1. 牛熊切换下不能简单沿用同一套短线节奏
   - rule_id: `bull-bear-overview`
   - rule_text: 牛市、熊市和切换期的短线基础行情不同，不能简单沿用同一套短线策略；需要根据成交额、指数环境和赚钱/亏钱效应重新判断进攻与防守权重。
   - evidence_claim_ids: claim-0d18577396d6de47, claim-c96ab1bcbaaaca45, claim-4401e71816e7b264, claim-184d968de1ea8f8b, claim-24155837184cdad5
2. 牛熊切换规则 1
   - rule_id: `bull-bear-1`
   - rule_text: 在判断牛熊切换时，应优先检查：不中听说句，这么多大婶能看出牛市来了，真是牛市也会一波三折。
   - evidence_claim_ids: claim-c96ab1bcbaaaca45
3. 牛熊切换规则 2
   - rule_id: `bull-bear-2`
   - rule_text: 在判断牛熊切换时，应优先检查：认知的一致，是没法垫高市场成本，牛市结构的筹码堆叠就无从说起。
   - evidence_claim_ids: claim-4401e71816e7b264
4. 牛熊切换规则 3
   - rule_id: `bull-bear-3`
   - rule_text: 在判断牛熊切换时，应优先检查：如果是牛市，第一次暴力杀透了，其实不要想太多，概率上是修复概率大的，关键就是修复的能量。
   - evidence_claim_ids: claim-184d968de1ea8f8b
5. 牛熊切换规则 4
   - rule_id: `bull-bear-4`
   - rule_text: 在判断牛熊切换时，应优先检查：因为长期熊市，聪明豆拿不住票的，往往涨两天就到处提示风险，以示经验丰富。
   - evidence_claim_ids: claim-24155837184cdad5
6. 牛熊切换规则 5
   - rule_id: `bull-bear-5`
   - rule_text: 在判断牛熊切换时，应优先检查：如果再有一个大的牛熊周期，熊市应该保住本金，收缩战线。
   - evidence_claim_ids: claim-8a89cc9f5b4d6a08
7. 牛熊切换规则 6
   - rule_id: `bull-bear-6`
   - rule_text: 在判断牛熊切换时，应优先检查：而且投资者心态由熊市到牛市，不是一夜可以解决的。
   - evidence_claim_ids: claim-5dff2483fa3819be
8. 牛熊切换规则 7
   - rule_id: `bull-bear-7`
   - rule_text: 在判断牛熊切换时，应优先检查：牛市多长阴，没长阴不是牛市。
   - evidence_claim_ids: claim-5eb3fc02b6c6ddcd

#### Representative Accepted Evidence
- claim_id: `claim-0d18577396d6de47`
  - article_id: 2bWeZGDSi07
  - source_type: article
  - raw_excerpt: 癌股历来的牛市都是水牛，有钱就涨，涨到某些人怕了从天而降的掌法，拼裸泳。
  - method_tags: 牛熊切换
- claim_id: `claim-c96ab1bcbaaaca45`
  - article_id: 2bWeZGDSi07
  - source_type: article
  - raw_excerpt: 不中听说句，这么多大婶能看出牛市来了，真是牛市也会一波三折。
  - method_tags: 牛熊切换
- claim_id: `claim-4401e71816e7b264`
  - article_id: 2bWeZGDSi07
  - source_type: article
  - raw_excerpt: 认知的一致，是没法垫高市场成本，牛市结构的筹码堆叠就无从说起。
  - method_tags: 市场结构, 牛熊切换
- claim_id: `claim-184d968de1ea8f8b`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 如果是牛市，第一次暴力杀透了，其实不要想太多，概率上是修复概率大的，关键就是修复的能量。
  - method_tags: 牛熊切换
- claim_id: `claim-24155837184cdad5`
  - article_id: 21ZIusToJzV
  - source_type: comment
  - raw_excerpt: 因为长期熊市，聪明豆拿不住票的，往往涨两天就到处提示风险，以示经验丰富。
  - method_tags: 牛熊切换

#### Needs-edit / Caveats
- claim_id: `claim-4fb37e6610f88183`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 我不确定这是不是牛市，如果是牛市，一生不会遇到多少次。
  - method_tags: 牛熊切换
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性牛熊切换方法论表述。
- claim_id: `claim-9ee6f4c04ec7e9c5`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 癌股的牛市，最后大部分人都赔得倾家荡产，宝总不是孤例。
  - method_tags: 牛熊切换
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性风控规则。
- claim_id: `claim-03c257757050e834`
  - article_id: 1VvuASpPpMr
  - source_type: comment
  - raw_excerpt: 说了牛市全部老鸟玩不过菜市场大妈，因为知道得太多了。
  - method_tags: 牛熊切换
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-897ffdeb9f7eb078`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 今天不是证明了牛市熊市，秒天地板是没啥区别的？
  - method_tags: 牛熊切换
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-a9a023dd2f05d434`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 大牛市十大致富招数，大牛市最好的操作就是躺赢，大牛市最好就是拼上仓位，大牛市老鸟最容易收割小鸟。
  - method_tags: 仓位管理, 牛熊切换
  - review_notes: 待编辑：盘中特指较强，需要抽象为市场状态下的执行原则。

## 主题之间的关系

- 量化影响如何改变短线生态：量化资金会改变资金反馈速度、流动性分布和盘中承接结构。
- 成交额如何约束短线高度：成交活跃度不足时，短线高度、接力持续性和赚钱效应都会受限。
- 指数环境如何影响短线基础行情：指数环境会直接影响短线承接、风险偏好和容错空间。
- 弱市或熊市为什么需要风控优先：当亏钱效应扩散、流动性不足时，仓位与交易频率都应先收缩。
- 牛熊切换下为什么不能简单套用同一套短线策略：环境切换会改变风险收益比、执行节奏和可用模式。

## 待确认观点

### 量化影响
- claim_id: `claim-01f3c877548cd251`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 但当早上量化资金发现全是抄底资金的时候，它就先不卖，让抄底资金买，高位再卖，是不是价格就高很多，还不用自己抬轿。
  - method_tags: 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-171e0cd2096eef89`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 有下影线是正常的，不是散户抄的底，应该是量化买的。
  - method_tags: 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-55c8271702b5d2ff`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 那个就是量化席位，我不是说了之前发掘某些形态的轮动，盘面挖出来，人家盘中已经进去了，次日卖给我这种。
  - method_tags: 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-5d6a72a7232bf40b`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 龙虎榜3家机构，净买入1.52亿，不是做T，大概率是主观多头的机构，不是量化。
  - method_tags: 量化影响, 买入触发
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-76f055a577e5743a`
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - raw_excerpt: 不用问了，还是那句，午后如果量化策略自动减仓30%，这批短线票腥风血雨的。
  - method_tags: 短线基础行情, 量化影响
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。

### 成交额 / 量能
- claim_id: `claim-135f828da00f1296`
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - raw_excerpt: 如果你信V，今天早盘放量恐慌的板块，午后指数跳水点就是买点。
  - method_tags: 成交额, 指数环境
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。
- claim_id: `claim-694dc8a4fb0e17bb`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 因为封板票多是没量的，昨日涨停和昨日连板在跌，能量放量，肯定是追卖或者炸板。
  - method_tags: 成交额, 短线基础行情
  - review_notes: 待编辑：盘中特指较强，需要抽象为成交额或量能机制判断。
- claim_id: `claim-9f5b2f4a90da37fd`
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - raw_excerpt: 所以整个上午指数放了点量，短线那批票反而大幅度缩量。
  - method_tags: 成交额, 指数环境, 短线基础行情
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。
- claim_id: `claim-c20cd2462f4a5f36`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 还有个事，就是现在指数右肩缩量，今天如果再高开，是跳空摸前面3万亿成交的套牢日的。
  - method_tags: 成交额, 指数环境
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。
- claim_id: `claim-cc8ad369db5b642f`
  - article_id: 2ohHCnLXtP8
  - source_type: comment
  - raw_excerpt: 开得高是没办法，因为市场持续缩量，所以外盘和消息面影响很大，动不动就大高开大低开，指数大阴大阳。
  - method_tags: 成交额, 指数环境
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为成交额或量能环境判断。

### 短线基础行情
- claim_id: `claim-6d64a9229d147ed7`
  - article_id: 24O3rehPcWv
  - source_type: article
  - raw_excerpt: 现学现卖，“行情不好是因为短线客接不住，接得住行情就会好。
  - method_tags: 短线基础行情
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性短线方法论表述。
- claim_id: `claim-6b7b0cd7472e8ce9`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 实际上，要操作也应该昨天买科技，共振指数修复，而不是今天去接力。
  - method_tags: 指数环境, 短线基础行情
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的短线执行规则表述。
- claim_id: `claim-1d74e64bd2040ab0`
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - raw_excerpt: 小金属今天没先手有风险的，很多短线资金昨天上车，如果午后指数不好回落炸几个板，情况又好像周四周五的
  - method_tags: 指数环境, 短线基础行情, 买入触发
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的风控判断。
- claim_id: `claim-2edec5c39f0403ff`
  - article_id: 2fQt29pQ3Pa
  - source_type: comment
  - raw_excerpt: 关键，成交快速放，第一波拉升之前6%+，也就是市场整体态度是红盘让你砸，显然不是短线佬加钱买上去的，最厉害就是坑挚爱亲朋，长期卖一把买五忽悠瘸了。
  - method_tags: 短线基础行情
  - review_notes: 待确认：原句口语化且带有嘲讽色彩，需要人工结合上下文确认。
- claim_id: `claim-64b006f936c2bb96`
  - article_id: 24O3rehPcWv
  - source_type: comment
  - raw_excerpt: 情绪指数里面包含远端短线和翘板票，都说了昨天很多是顺势撬开，实际是卖点不是买点。
  - method_tags: 情绪周期, 指数环境, 短线基础行情, 反核
  - review_notes: 待编辑：原句有价值，但需要压缩为中性的短线环境判断。

### 指数环境
- claim_id: `claim-01c29b11d81a8401`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 牛市多长阴，今天创业板长了15CM，调整可以20CM的。
  - method_tags: 指数环境, 牛熊切换
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性牛熊切换方法论表述。

### 风控
- claim_id: `claim-efc4ff8c194fe3ee`
  - article_id: 21mulzOf8Yb
  - source_type: comment
  - raw_excerpt: 同时所谓超额收益，就是被打死那边逼着止损，资金出来以后，又要去拉升那边追高，因为你没有
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性风控规则。
- claim_id: `claim-2b50815b715120c8`
  - article_id: 2jbi0efIsof
  - source_type: comment
  - raw_excerpt: 最终目的，写好识别算法，这个票出来，弹窗，有没有风控触发，有没有诱多，是否配合行情风格。
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要压缩为中性风控方法论表述。
- claim_id: `claim-b4a07794e0776819`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 要么跟些躺赢老师讨论一下躺赢技术，昨天如何在昨日早盘跳水买到全部不回撤的票，今天如何在300红盘的行情躺赢？
  - method_tags: 风控
  - review_notes: 待确认：原句明显带有调侃语气，需要人工结合上下文确认。
- claim_id: `claim-2acf6176d6d59118`
  - article_id: 25VmrtPmuWI
  - source_type: comment
  - raw_excerpt: 一环扣一环的演变，所以，风控不见得坏。
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要压缩为中性风控方法论表述。
- claim_id: `claim-c1e8b75141c09c82`
  - article_id: 1Zn2UmelLMJ
  - source_type: comment
  - raw_excerpt: 正常要加个风控机制，估计没想到还有一日涨几十倍的。
  - method_tags: 风控
  - review_notes: 待编辑：原句有价值，但需要抽象为亏钱效应或止损盘风险机制判断。

### 牛熊切换
- claim_id: `claim-4fb37e6610f88183`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 我不确定这是不是牛市，如果是牛市，一生不会遇到多少次。
  - method_tags: 牛熊切换
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性牛熊切换方法论表述。
- claim_id: `claim-9ee6f4c04ec7e9c5`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 癌股的牛市，最后大部分人都赔得倾家荡产，宝总不是孤例。
  - method_tags: 牛熊切换
  - review_notes: 待编辑：原句有价值，但需要结合上下文压缩为中性风控规则。
- claim_id: `claim-03c257757050e834`
  - article_id: 1VvuASpPpMr
  - source_type: comment
  - raw_excerpt: 说了牛市全部老鸟玩不过菜市场大妈，因为知道得太多了。
  - method_tags: 牛熊切换
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-897ffdeb9f7eb078`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 今天不是证明了牛市熊市，秒天地板是没啥区别的？
  - method_tags: 牛熊切换
  - review_notes: 待确认：疑似反讽、打趣或上下文不足，需要人工结合原文确认。
- claim_id: `claim-a9a023dd2f05d434`
  - article_id: 2bWeZGDSi07
  - source_type: comment
  - raw_excerpt: 大牛市十大致富招数，大牛市最好的操作就是躺赢，大牛市最好就是拼上仓位，大牛市老鸟最容易收割小鸟。
  - method_tags: 仓位管理, 牛熊切换
  - review_notes: 待编辑：盘中特指较强，需要抽象为市场状态下的执行原则。

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
- needs_edit 只作为待确认材料，不直接写成核心规则。
- rejected / unreviewed 不进入 Skill v0.1 的核心方法论。
