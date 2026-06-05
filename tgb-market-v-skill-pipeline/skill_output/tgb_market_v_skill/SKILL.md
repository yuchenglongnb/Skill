# TGB Market V Skill v0.1

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
#### Rule quant-impact-overview: 量化影响需要纳入短线市场结构判断
- Rule: 量化交易会改变短线生态中的资金反馈速度、流动性分布和追涨/抛压结构；分析短线机会时，需要把量化带来的趋同交易、规避策略和盘中反馈纳入市场结构判断。
- When to use: 当作者讨论量化、量化冲击、量化反馈或短线生态变化时。；当盘面现象不能只用题材强弱解释时。
- Do not use when: 只有个股复盘细节、没有市场结构含义时。；只有情绪表达、没有机制判断时。
- Evidence:
  - `claim-ef4706e7c13c1cf0`
  - `claim-451671d03a6b0646`
  - `claim-9fa24ae5f750c243`
  - `claim-acaaf4cdb5d413ec`
  - `claim-07c3a9a457b934fa`
- Caveats: 不要把量化影响简化成单一利多或利空。；需要结合指数环境、成交额和短线基础行情共同判断。

#### Rule quant-impact-1: 量化影响规则 1
- Rule: 在评估量化影响时，应将以下判断纳入市场结构分析：美国和我国都因为量化趋同交易出现了股灾。
- When to use: 当作者讨论量化冲击、盘中反馈或短线生态变化时。
- Do not use when: 不要把没有结构含义的个股碎句直接当成量化规则。
- Evidence:
  - `claim-451671d03a6b0646`
- Caveats: 需要结合成交额、指数环境和短线基础行情一起判断。

#### Rule quant-impact-2: 量化影响规则 2
- Rule: 在评估量化影响时，应将以下判断纳入市场结构分析：进入正题，上面的情况不是孤例，而是市场长期在大量量化交易影响下的演变结果。
- When to use: 当作者讨论量化冲击、盘中反馈或短线生态变化时。
- Do not use when: 不要把没有结构含义的个股碎句直接当成量化规则。
- Evidence:
  - `claim-9fa24ae5f750c243`
- Caveats: 需要结合成交额、指数环境和短线基础行情一起判断。

#### Rule quant-impact-3: 量化影响规则 3
- Rule: 在评估量化影响时，应将以下判断纳入市场结构分析：所以，别再这么傻问怎么狙击量化，低纬战高维，我们都是虫子。
- When to use: 当作者讨论量化冲击、盘中反馈或短线生态变化时。
- Do not use when: 不要把没有结构含义的个股碎句直接当成量化规则。
- Evidence:
  - `claim-acaaf4cdb5d413ec`
- Caveats: 需要结合成交额、指数环境和短线基础行情一起判断。

#### Rule quant-impact-4: 量化影响规则 4
- Rule: 在评估量化影响时，应将以下判断纳入市场结构分析：机构做多那天，会把追涨量化和短线资金都带倒一处，别的地方如果有短线获利盘，则存在流动性不足。
- When to use: 当作者讨论量化冲击、盘中反馈或短线生态变化时。
- Do not use when: 不要把没有结构含义的个股碎句直接当成量化规则。
- Evidence:
  - `claim-07c3a9a457b934fa`
- Caveats: 需要结合成交额、指数环境和短线基础行情一起判断。

#### Rule quant-impact-5: 量化影响规则 5
- Rule: 在评估量化影响时，应将以下判断纳入市场结构分析：因为量化深度绑定市场后，由于它的指增策略和横跳不空仓策略，导致市场会在很长一段时间，无论涨跌都是接近的成交水平。
- When to use: 当作者讨论量化冲击、盘中反馈或短线生态变化时。
- Do not use when: 不要把没有结构含义的个股碎句直接当成量化规则。
- Evidence:
  - `claim-0f01272d60e70e94`
- Caveats: 需要结合成交额、指数环境和短线基础行情一起判断。

#### Rule quant-impact-6: 量化影响规则 6
- Rule: 在评估量化影响时，应将以下判断纳入市场结构分析：而量化高抛低吸的中间差价，实际上就是躺着的自然人付了，因为你持股实际价值变低了。
- When to use: 当作者讨论量化冲击、盘中反馈或短线生态变化时。
- Do not use when: 不要把没有结构含义的个股碎句直接当成量化规则。
- Evidence:
  - `claim-1bd6f55ea1a4f94f`
- Caveats: 需要结合成交额、指数环境和短线基础行情一起判断。

#### Rule quant-impact-7: 量化影响规则 7
- Rule: 在评估量化影响时，应将以下判断纳入市场结构分析：而且量化操作时候也不可能完全识别其它买卖盘是不是量化。
- When to use: 当作者讨论量化冲击、盘中反馈或短线生态变化时。
- Do not use when: 不要把没有结构含义的个股碎句直接当成量化规则。
- Evidence:
  - `claim-46791f2cd9e4e4a2`
- Caveats: 需要结合成交额、指数环境和短线基础行情一起判断。

### 2. 成交额 / 量能
#### Rule turnover-overview: 成交额约束短线高度与持续性
- Rule: 成交额与量能不是简单的放量好、缩量坏；需要结合指数环境、短线基础行情和资金稀缺性判断。短线高度、接力持续性和赚钱效应都受整体成交活跃度约束。
- When to use: 当作者讨论成交额、量能、缩量、放量和流动性约束时。；当题材高度或接力持续性出现变化时。
- Do not use when: 只有单一日内波动、没有成交结构信息时。；只有盘后感叹、没有可抽象规则时。
- Evidence:
  - `claim-c1c3ea0d9bd5e06a`
  - `claim-7c8abf7d84d3e9e3`
  - `claim-3a4023259a7db272`
  - `claim-5b51bdf81cc631e4`
  - `claim-5fe2969caeba4bdc`
- Caveats: 量能本身不是结论，需要和指数环境、风险偏好一起看。

#### Rule turnover-1: 成交额 / 量能规则 1
- Rule: 在评估成交额与量能时，应优先检查：之所以用换手不用金额，是为体现个股本身精确的活跃度排名，竞价可以用成交量跟金额直接转换，换手率=成交量/自由流通盘*100，大家的数值都是在0-100之间，标准化对比，更能体现全市场活跃度的排列。
- When to use: 当作者讨论成交额、缩量、放量和市场活跃度时。
- Do not use when: 不要把没有环境背景的量能描述直接当成独立结论。
- Evidence:
  - `claim-7c8abf7d84d3e9e3`
- Caveats: 量能本身不是结论，需要结合环境解释。

#### Rule turnover-2: 成交额 / 量能规则 2
- Rule: 在评估成交额与量能时，应优先检查：1. 指数要高开，是需要量能支撑的，以示不是跌多了惜售，而是有增量推动。
- When to use: 当作者讨论成交额、缩量、放量和市场活跃度时。
- Do not use when: 不要把没有环境背景的量能描述直接当成独立结论。
- Evidence:
  - `claim-3a4023259a7db272`
- Caveats: 量能本身不是结论，需要结合环境解释。

#### Rule turnover-3: 成交额 / 量能规则 3
- Rule: 在评估成交额与量能时，应优先检查：本身指数在高位，缩量午后很容易跳水的，所以比较风险。
- When to use: 当作者讨论成交额、缩量、放量和市场活跃度时。
- Do not use when: 不要把没有环境背景的量能描述直接当成独立结论。
- Evidence:
  - `claim-5b51bdf81cc631e4`
- Caveats: 量能本身不是结论，需要结合环境解释。

#### Rule turnover-4: 成交额 / 量能规则 4
- Rule: 在评估成交额与量能时，应优先检查：当时第二天指数缺口低开，但放量，资金抄底，所以有了低开高走。
- When to use: 当作者讨论成交额、缩量、放量和市场活跃度时。
- Do not use when: 不要把没有环境背景的量能描述直接当成独立结论。
- Evidence:
  - `claim-5fe2969caeba4bdc`
- Caveats: 量能本身不是结论，需要结合环境解释。

#### Rule turnover-5: 成交额 / 量能规则 5
- Rule: 在评估成交额与量能时，应优先检查：今天肯定缩量(竞价)，所以，指数如果高开，大概率就是震荡。
- When to use: 当作者讨论成交额、缩量、放量和市场活跃度时。
- Do not use when: 不要把没有环境背景的量能描述直接当成独立结论。
- Evidence:
  - `claim-86914b3d88bfe3e5`
- Caveats: 量能本身不是结论，需要结合环境解释。

#### Rule turnover-6: 成交额 / 量能规则 6
- Rule: 在评估成交额与量能时，应优先检查：但是缩量上板，如果午后指数不举，它就会反复炸。
- When to use: 当作者讨论成交额、缩量、放量和市场活跃度时。
- Do not use when: 不要把没有环境背景的量能描述直接当成独立结论。
- Evidence:
  - `claim-8859e6bbf84f1014`
- Caveats: 量能本身不是结论，需要结合环境解释。

#### Rule turnover-7: 成交额 / 量能规则 7
- Rule: 在评估成交额与量能时，应优先检查：分析是基于市场特征的，近期创业板成交额占比高，基本它压制指数，无论怎样轮动整体市场都被锤，不是高低切可以解决。
- When to use: 当作者讨论成交额、缩量、放量和市场活跃度时。
- Do not use when: 不要把没有环境背景的量能描述直接当成独立结论。
- Evidence:
  - `claim-8fa801c11064a31d`
- Caveats: 量能本身不是结论，需要结合环境解释。

### 3. 短线基础行情
#### Rule short-term-base-overview: 先判断短线基础行情，再判断局部机会
- Rule: 短线机会不能只看个股局部强弱；应先判断整体赚钱效应、接力环境、轮动速度和指数/成交额背景，再评估个股高度与容错。
- When to use: 当作者讨论连板、首板、接力、赚钱效应和短线生态时。；当局部强股表现与整体短线环境出现背离时。
- Do not use when: 只有个股点评、没有短线生态含义时。；只有泛泛说强弱、没有环境判断时。
- Evidence:
  - `claim-27d6b8820885dee1`
  - `claim-38184d61ed1ba0ec`
  - `claim-6e6e4c1cd2740054`
  - `claim-7ae975def66992ff`
  - `claim-20690373fb54268c`
- Caveats: 短线基础行情是环境变量，不等于单只股票的即时强弱。

#### Rule short-term-base-1: 短线基础行情规则 1
- Rule: 在判断短线基础行情时，应重点关注：这里不是独立板块，而是整个短线先后手阵型的对立，让人感觉资金专买你不要的，互卷互拆台。
- When to use: 当作者讨论接力环境、赚钱效应和短线容错时。
- Do not use when: 不要把单一个股强弱直接当成整体短线环境。
- Evidence:
  - `claim-38184d61ed1ba0ec`
- Caveats: 局部强股不能替代整体短线生态判断。

#### Rule short-term-base-2: 短线基础行情规则 2
- Rule: 在判断短线基础行情时，应重点关注：如果底层观点成立，那，就要把短线分析和统计都独立于指数，否则会自受其乱。
- When to use: 当作者讨论接力环境、赚钱效应和短线容错时。
- Do not use when: 不要把单一个股强弱直接当成整体短线环境。
- Evidence:
  - `claim-6e6e4c1cd2740054`
- Caveats: 局部强股不能替代整体短线生态判断。

#### Rule short-term-base-3: 短线基础行情规则 3
- Rule: 在判断短线基础行情时，应重点关注：赚钱效应应体现在短线整体，而不是局部，某某龙头还没挂。
- When to use: 当作者讨论接力环境、赚钱效应和短线容错时。
- Do not use when: 不要把单一个股强弱直接当成整体短线环境。
- Evidence:
  - `claim-7ae975def66992ff`
- Caveats: 局部强股不能替代整体短线生态判断。

#### Rule short-term-base-4: 短线基础行情规则 4
- Rule: 在判断短线基础行情时，应重点关注：所以连板率非常丑，做接力的连接12天盘，轮动超快。
- When to use: 当作者讨论接力环境、赚钱效应和短线容错时。
- Do not use when: 不要把单一个股强弱直接当成整体短线环境。
- Evidence:
  - `claim-20690373fb54268c`
- Caveats: 局部强股不能替代整体短线生态判断。

#### Rule short-term-base-5: 短线基础行情规则 5
- Rule: 在判断短线基础行情时，应重点关注：指数向下，假设短线不是自己独立的数板行情，明天溢价有限，搞不好被绕柱。
- When to use: 当作者讨论接力环境、赚钱效应和短线容错时。
- Do not use when: 不要把单一个股强弱直接当成整体短线环境。
- Evidence:
  - `claim-1238b38b8a84fdc2`
- Caveats: 局部强股不能替代整体短线生态判断。

#### Rule short-term-base-6: 短线基础行情规则 6
- Rule: 在判断短线基础行情时，应重点关注：因为我好几年前就把短线和指数分开跟踪，尽量去还原市场。
- When to use: 当作者讨论接力环境、赚钱效应和短线容错时。
- Do not use when: 不要把单一个股强弱直接当成整体短线环境。
- Evidence:
  - `claim-1d43f83ee28113ea`
- Caveats: 局部强股不能替代整体短线生态判断。

#### Rule short-term-base-7: 短线基础行情规则 7
- Rule: 在判断短线基础行情时，应重点关注：做热门票的资金跟指数ETF不是同一批资金，但是指数是载体，指数弱了，大概率短线货锚着指数杀跌或者补涨的。
- When to use: 当作者讨论接力环境、赚钱效应和短线容错时。
- Do not use when: 不要把单一个股强弱直接当成整体短线环境。
- Evidence:
  - `claim-20a73a4c0a41d291`
- Caveats: 局部强股不能替代整体短线生态判断。

### 4. 指数环境
#### Rule index-environment-overview: 指数环境影响短线承接与风险偏好
- Rule: 指数环境会影响短线资金的承接、风险偏好和仓位选择；指数震荡或下行风险较大时，应降低对局部题材强度和持续性的确定性判断。
- When to use: 当作者讨论指数、市场环境、大盘背景或承接变化时。；当局部题材强度与整体指数环境不一致时。
- Do not use when: 只有情绪化看法、没有环境传导逻辑时。；只有单日涨跌结论、没有对短线生态的影响判断时。
- Evidence:
  - `claim-ed117cf1071a1b82`
  - `claim-859ed6774a56538f`
  - `claim-edbf9735a3e0312c`
  - `claim-450d050cafe52c0d`
  - `claim-80871be657572a84`
- Caveats: 指数环境影响的是风险偏好与承接，不应被机械当成唯一方向判断。

#### Rule index-environment-1: 指数环境规则 1
- Rule: 在判断指数环境影响时，应优先考虑：这次交易制度跟之前牛市不一样，例如，一年纪不能买创业板&+，那增量市场，主板和ohters可能会形成两个交易风格。
- When to use: 当作者讨论指数背景、承接变化和风险偏好时。
- Do not use when: 不要把指数涨跌本身当成唯一方法论结论。
- Evidence:
  - `claim-859ed6774a56538f`
- Caveats: 指数环境影响承接与风险偏好，不是唯一方向信号。

#### Rule index-environment-2: 指数环境规则 2
- Rule: 在判断指数环境影响时，应优先考虑：要是指数有一定震荡风险（市场态度模糊），那先减仓风控。
- When to use: 当作者讨论指数背景、承接变化和风险偏好时。
- Do not use when: 不要把指数涨跌本身当成唯一方法论结论。
- Evidence:
  - `claim-edbf9735a3e0312c`
- Caveats: 指数环境影响承接与风险偏好，不是唯一方向信号。

#### Rule index-environment-3: 指数环境规则 3
- Rule: 在判断指数环境影响时，应优先考虑：指数正常今天跌也跌不多的，你觉得牛市，周末就别太空舱。
- When to use: 当作者讨论指数背景、承接变化和风险偏好时。
- Do not use when: 不要把指数涨跌本身当成唯一方法论结论。
- Evidence:
  - `claim-450d050cafe52c0d`
- Caveats: 指数环境影响承接与风险偏好，不是唯一方向信号。

#### Rule index-environment-4: 指数环境规则 4
- Rule: 在判断指数环境影响时，应优先考虑：指数＞板块＞个股，牛市，熊市，都一样的。
- When to use: 当作者讨论指数背景、承接变化和风险偏好时。
- Do not use when: 不要把指数涨跌本身当成唯一方法论结论。
- Evidence:
  - `claim-80871be657572a84`
- Caveats: 指数环境影响承接与风险偏好，不是唯一方向信号。

### 5. 风控
#### Rule risk-control-overview: 环境不支持进攻时优先收缩风险暴露
- Rule: 当指数、成交额、短线基础行情或亏钱效应不支持进攻时，应优先降低仓位、减少交易或等待，而不是强行套用强行情打法。
- When to use: 当作者讨论弱市、回撤、亏钱效应、仓位和等待时。；当买入前提不成立或流动性明显恶化时。
- Do not use when: 只有口号式风险提醒、没有执行原则时。；只有单只个股抱怨、没有风控规则时。
- Evidence:
  - `claim-fbb0b89761bddf8b`
  - `claim-2d86cadbf15dbc78`
  - `claim-41fa00e960878b4d`
  - `claim-fdc0ada0a1053a95`
  - `claim-2d8d8202a083ae91`
- Caveats: 风控规则优先于进攻意愿。；需要把环境变化和执行节奏一起看。

#### Rule risk-control-1: 风控规则 1
- Rule: 在执行风控时，应优先遵守：要风控不是现在，要么一早不买。
- When to use: 当作者讨论仓位、等待、回撤或亏钱效应时。
- Do not use when: 不要把情绪化恐慌表达直接当成风控规则。
- Evidence:
  - `claim-2d86cadbf15dbc78`
- Caveats: 风控优先于进攻，执行前要确认环境是否支持。

#### Rule risk-control-2: 风控规则 2
- Rule: 在执行风控时，应优先遵守：我觉得持股都不是问题，关键你要知道什么情况持股，什么情况风控甚至割肉。
- When to use: 当作者讨论仓位、等待、回撤或亏钱效应时。
- Do not use when: 不要把情绪化恐慌表达直接当成风控规则。
- Evidence:
  - `claim-41fa00e960878b4d`
- Caveats: 风控优先于进攻，执行前要确认环境是否支持。

#### Rule risk-control-3: 风控规则 3
- Rule: 在执行风控时，应优先遵守：玩这种系统开发，是要推理出什么条件会走成那样，暂时没有好的想法，所以先风控。
- When to use: 当作者讨论仓位、等待、回撤或亏钱效应时。
- Do not use when: 不要把情绪化恐慌表达直接当成风控规则。
- Evidence:
  - `claim-fdc0ada0a1053a95`
- Caveats: 风控优先于进攻，执行前要确认环境是否支持。

#### Rule risk-control-4: 风控规则 4
- Rule: 在执行风控时，应优先遵守：出门爆砸半小时，后面散户后知后觉就会跟着“纪律止损”，你们想想以往行情不好，是不是忍一整天，很容易1:30~2:00剁雕。
- When to use: 当作者讨论仓位、等待、回撤或亏钱效应时。
- Do not use when: 不要把情绪化恐慌表达直接当成风控规则。
- Evidence:
  - `claim-2d8d8202a083ae91`
- Caveats: 风控优先于进攻，执行前要确认环境是否支持。

#### Rule risk-control-5: 风控规则 5
- Rule: 在执行风控时，应优先遵守：防回撤不是一句空话，你要在一个区间里面把得住才行的。
- When to use: 当作者讨论仓位、等待、回撤或亏钱效应时。
- Do not use when: 不要把情绪化恐慌表达直接当成风控规则。
- Evidence:
  - `claim-d832417a28904324`
- Caveats: 风控优先于进攻，执行前要确认环境是否支持。

#### Rule risk-control-6: 风控规则 6
- Rule: 在执行风控时，应优先遵守：这种是涉及做与不做的问题，相当于上了一道操作的风控锁。
- When to use: 当作者讨论仓位、等待、回撤或亏钱效应时。
- Do not use when: 不要把情绪化恐慌表达直接当成风控规则。
- Evidence:
  - `claim-e0eb1c78f60416f2`
- Caveats: 风控优先于进攻，执行前要确认环境是否支持。

#### Rule risk-control-7: 风控规则 7
- Rule: 在执行风控时，应优先遵守：风控意识一定要有，否则1-2笔大亏的交易让你清零。
- When to use: 当作者讨论仓位、等待、回撤或亏钱效应时。
- Do not use when: 不要把情绪化恐慌表达直接当成风控规则。
- Evidence:
  - `claim-f21c0a5161d8c8ab`
- Caveats: 风控优先于进攻，执行前要确认环境是否支持。

### 6. 牛熊切换
#### Rule bull-bear-overview: 牛熊切换下不能简单沿用同一套短线节奏
- Rule: 牛市、熊市和切换期的短线基础行情不同，不能简单沿用同一套短线策略；需要根据成交额、指数环境和赚钱/亏钱效应重新判断进攻与防守权重。
- When to use: 当作者讨论牛市、熊市、市场状态变化或周期切换时。；当策略节奏需要根据环境切换时。
- Do not use when: 只有口语化情绪判断、没有环境差异逻辑时。；只有历史感慨、没有可执行原则时。
- Evidence:
  - `claim-0d18577396d6de47`
  - `claim-c96ab1bcbaaaca45`
  - `claim-4401e71816e7b264`
  - `claim-184d968de1ea8f8b`
  - `claim-24155837184cdad5`
- Caveats: 不要把牛熊切换理解成单一择时信号。；要结合成交额、指数环境和短线基础行情综合判断。

#### Rule bull-bear-1: 牛熊切换规则 1
- Rule: 在判断牛熊切换时，应优先检查：不中听说句，这么多大婶能看出牛市来了，真是牛市也会一波三折。
- When to use: 当作者讨论牛熊状态、强弱环境和节奏切换时。
- Do not use when: 不要把情绪化牛熊判断直接当成稳定策略规则。
- Evidence:
  - `claim-c96ab1bcbaaaca45`
- Caveats: 环境切换意味着策略节奏和风险预算都可能变化。

#### Rule bull-bear-2: 牛熊切换规则 2
- Rule: 在判断牛熊切换时，应优先检查：认知的一致，是没法垫高市场成本，牛市结构的筹码堆叠就无从说起。
- When to use: 当作者讨论牛熊状态、强弱环境和节奏切换时。
- Do not use when: 不要把情绪化牛熊判断直接当成稳定策略规则。
- Evidence:
  - `claim-4401e71816e7b264`
- Caveats: 环境切换意味着策略节奏和风险预算都可能变化。

#### Rule bull-bear-3: 牛熊切换规则 3
- Rule: 在判断牛熊切换时，应优先检查：如果是牛市，第一次暴力杀透了，其实不要想太多，概率上是修复概率大的，关键就是修复的能量。
- When to use: 当作者讨论牛熊状态、强弱环境和节奏切换时。
- Do not use when: 不要把情绪化牛熊判断直接当成稳定策略规则。
- Evidence:
  - `claim-184d968de1ea8f8b`
- Caveats: 环境切换意味着策略节奏和风险预算都可能变化。

#### Rule bull-bear-4: 牛熊切换规则 4
- Rule: 在判断牛熊切换时，应优先检查：因为长期熊市，聪明豆拿不住票的，往往涨两天就到处提示风险，以示经验丰富。
- When to use: 当作者讨论牛熊状态、强弱环境和节奏切换时。
- Do not use when: 不要把情绪化牛熊判断直接当成稳定策略规则。
- Evidence:
  - `claim-24155837184cdad5`
- Caveats: 环境切换意味着策略节奏和风险预算都可能变化。

#### Rule bull-bear-5: 牛熊切换规则 5
- Rule: 在判断牛熊切换时，应优先检查：如果再有一个大的牛熊周期，熊市应该保住本金，收缩战线。
- When to use: 当作者讨论牛熊状态、强弱环境和节奏切换时。
- Do not use when: 不要把情绪化牛熊判断直接当成稳定策略规则。
- Evidence:
  - `claim-8a89cc9f5b4d6a08`
- Caveats: 环境切换意味着策略节奏和风险预算都可能变化。

#### Rule bull-bear-6: 牛熊切换规则 6
- Rule: 在判断牛熊切换时，应优先检查：而且投资者心态由熊市到牛市，不是一夜可以解决的。
- When to use: 当作者讨论牛熊状态、强弱环境和节奏切换时。
- Do not use when: 不要把情绪化牛熊判断直接当成稳定策略规则。
- Evidence:
  - `claim-5dff2483fa3819be`
- Caveats: 环境切换意味着策略节奏和风险预算都可能变化。

#### Rule bull-bear-7: 牛熊切换规则 7
- Rule: 在判断牛熊切换时，应优先检查：牛市多长阴，没长阴不是牛市。
- When to use: 当作者讨论牛熊状态、强弱环境和节奏切换时。
- Do not use when: 不要把情绪化牛熊判断直接当成稳定策略规则。
- Evidence:
  - `claim-5eb3fc02b6c6ddcd`
- Caveats: 环境切换意味着策略节奏和风险预算都可能变化。

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
- Skill v0.1 is based on first-round reviewed packs only.
