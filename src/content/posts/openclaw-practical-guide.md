---
title: OpenClaw实战：从"能聊天"到"能干活"的工程实践
date: 2026-04-10
description: 一个人、一台Mac、六个AI Agent - 深入解析OpenClaw多Agent系统的工程设计与实战经验
tags: [OpenClaw, AI Agent, 多Agent系统, 自动化, 工程实践]
category: AI工程
image: /images/ai-agent-team.jpg
---

# OpenClaw实战：从"能聊天"到"能干活"的工程实践

> **精读原文**：[OpenClaw 实战：一个人、一台 Mac、六个 AI Agent — 从"能聊天"到"能干活"的工程实战](https://mp.weixin.qq.com/s/S6XKuXHa4QqZ_qno1yGIFQ)
>
> **作者**：岚遥
> **来源**：阿里云开发者
> **精读日期**：2026年4月10日

## 核心摘要

这篇文章详细记录了作者如何用一台Mac构建了一个由6个AI Agent组成的自动化团队,从"能聊天"的Chatbot进化到"能干活"的完整工程体系。文章深度解析了Agent系统设计的三个核心工程问题:

1. **上下文管理** - 如何让Agent不会因为Session膨胀而崩溃
2. **记忆与成长** - 如何让Agent从错误中学习并持续改进
3. **多Agent协作** - 如何设计协议让多个Agent可靠协作

核心观点: **90%的时间花在工程问题上,不是AI问题上**。Agent系统的瓶颈不是模型能力,而是基础设施的成熟度。

---

## 一天被接管的生活

想象这样的场景:

- 你睡着时,交易蜘蛛已经出了股市收盘报告
- 你醒来前,宏观分析师已经写完了A股晨报
- 你还没刷手机,管家蜘蛛已推来天气、日程和今日待办
- AI哨兵已经扫完GitHub Trending、arXiv最新论文和100+个信息源
- 18+条技术情报按重要性排好序等你看

这不再是科幻,而是作者用OpenClaw实现的现实。

**系统规模**:
- 1个编排者 + 5个专业Agent + 6类ACP编码专家(最大6并发)
- 52个cron定时任务
- 118个Skills(33全局共享 + 85 Agent专属)
- 29个注册LLM模型
- 每天几千次LLM调用
- 2086行运维脚本 + 半个月23次自动恢复

---

## 团队架构:1+5+6阵型

### Zoe (大龙虾) — CTO / 首席编排者

不只是"管理员"。Zoe负责:
- **技术方案设计** - 三态通信协议、Task Watcher、通信Guardrail框架
- **任务编排** - 每天巡检3次(10:00/14:00/22:00)
- **系统运维** - 检查cron执行状态、磁盘使用、session健康度
- **记忆系统维护** - 每周分析各Agent的MEMORY.md是否超限并执行分层压缩
- **技术雷达评估** - 消费ainews提供的技术发现,评估哪些值得应用到系统上

**巡检覆盖6大维度**:
1. cron任务执行状态(是否有失败/跳过的任务)
2. workspace磁盘使用(文件增长异常检测)
3. session大小与健康度
4. Chrome CDP进程是否泄露
5. .learnings/中是否有待处理条目
6. shared-context/时间戳是否正常(检测Agent是否"静默失联")

### AI哨兵(ainews) — 情报中枢

最关键的Agent之一。每天从100+个信息源采集信息:
- GitHub Trending
- arXiv
- RSS
- HackerNews
- Reddit

**产出**:
- 晨报、午间论文解读、晚间趋势分析
- 主动评估技术发现对系统的影响
- 有价值的发现会进入Tech Radar

**核心工具链**:
- `github_trending.py` --ai-only过滤 + --since weekly周趋势
- `rss_aggregator.py` (多源并发采集)
- `arxiv_papers.py` (多关键词搜索)
- Tavily (AI优化搜索首选)
- agent-browser (Playwright驱动,JS渲染页面采集)

**防幻觉硬约束**:
- 每条新闻MUST带原文URL
- 发布前自检可达性
- 无法交叉验证的标注「单源,建议核实」

### 交易蜘蛛(Trading) — 量化分析师

团队中任务最密集的Agent:
- **21个cron任务**
- **20个原子量化工具**(quant.py CLI)
- **15个专属Skills**(68000+行代码)
- **65/35混合评分模型**(65%工具量化 + 35% AI判断)

**覆盖**:
- A股全时段(集合竞价→盘中每10分钟扫描→尾盘速报)
- 美股(盘前→盘中每30分钟→盘后夜报)
- 大宗商品(每小时白天+夜盘)

**四步分析框架**:
1. 读取Macro宏观因子
2. 多维评分(技术面25% / 资金面30% / 基本面10% / 情绪面20% / 市场面15%)
3. 逆向检验(与共识一致吗?若错最可能原因?)
4. 输出标的+评分(0-100)+止损位+置信度

**硬性规则**:
- NEVER给出没有止损的买入建议
- NEVER编造数据(工具失败时直接报告原因)
- 置信度<60%标注「低置信度,建议观望」

### Macro(首席经济学家) — 数据驱动的四层映射

提供宏观→传导→国内→市场四层映射因子包,供Trading直接引用。

**9个cron任务覆盖**:
- 晨报(07:50)
- 午间(12:30)
- 财经晚报(18:00)
- 美股盘前(22:00)
- 美股收盘(次日05:20)
- 周日18:30周度宏观复盘

**分析纪律**:
- 每个判断标注数据来源和时效性
- 区分事实(有数据)和判断(有逻辑无直接数据)
- 标注重信度(高>70%/中50-70%/低<50%)
- 每个判断提出反面论据

**真实案例**:
伊朗局势分析时,传统框架预测"地缘→避险→黄金涨",实际油价+14%但黄金-5%。Macro的分析指出"油价涨幅>10%,通胀逻辑主导,市场交易的是通胀而非避险"。这个洞察被沉淀到MEMORY.md成为持久知识。

### 内容蜘蛛(Content) — 内容策略师

不是自己"想"内容,而是从团队情报链中提取素材:
- ainews提供改写要点
- Macro提供深度分析
- Trading提供市场观点

**9个cron任务驱动四阶段流水线**:
09:00 Research(54个平台热榜抓取) → 10:30 Ideate(消费ainews改写要点) → 14:00 Write(产出初稿) → 22:10 Reflect(反思)

**自主进化案例**:
发现AI味太重后,Content自行调研"去AI味"工具,编写Skill,发布到ClawHub,并沉淀为全团队通用能力。

**X五篮子热点雷达**:
Content自主设计的情报采集框架,覆盖五个维度:

| 篮子 | 覆盖范围 | 配额 |
|------|----------|------|
| AI/科技 | OpenAI / Claude / Agent / LLM | ≤40% |
| 产品/创业 | startup / founder / product launch | 按热度 |
| 一人公司/效率 | solopreneur / productivity / automation | 按热度 |
| 投资/市场/宏观 | stocks / macro / bitcoin / fed | 按热度 |
| 社会情绪/国际 | geopolitics / layoffs / tariffs | 按热度 |

关键约束:AI/科技部分不超过整份输出的40%。这不是硬编码,是Content自己在反思中迭代出来的。

### 管家蜘蛛(Butler) — 生活管家

深度集成Apple生态:
- Reminders / Calendar / Health / Notes / Shortcuts

**7个cron任务**:
- 早安问候(08:00)
- 日程规划(08:30)
- 5次喝水提醒(温馨/幽默/知识科普/名人名言/emoji五种风格随机切换)
- 健康检查(20:00)
- 晚安总结(22:00)

**核心理念**:
- 不多不少,刚刚好
- 单次提醒<50字,间隔≥1.5小时
- 23:00–07:00仅发送紧急事项
- 用户没回复,不会连续催促

### ACP编码专家阵型

通过ACP协议按需委派编码任务:
- Pi / Claude Code / Codex / OpenCode / Gemini / GPT-5.3-Codex
- 最大6并发实例
- 120min TTL

**核心决策**:
不要让分析Agent直接编码。早期设了coding、architect、PM三个技术角色,发现产出有限,增加通信复杂度和调试成本。后来全砍了,编码通过ACP委派给Claode Code等专业工具。

---

## 核心工程问题一:上下文是Agent的操作系统

### 问题:Agent系统的热力学第二定律

不加约束,entropy只增不减。持续运行的Agent系统会确定性地走向崩溃——不是"可能",是"一定"。

### 三个真实事故

**P0 — 全团队瘫痪8小时**
ainews的session因为连续处理新闻和论文累积到235K tokens。Gateway启动时对所有session做compaction,这个session永远超时 → crash → macOS守护进程ThrottleInterval=1每秒重启 → 无限循环。所有Agent全部离线。

**修复要四层**:
1. 手动清理膨胀session
2. ThrottleInterval 1→10
3. idleMinutes "180"→30
4. exec.security full→allowlist

**P1 — 3500字报告被框架"优化"到800字**
交易蜘蛛的收盘速报包含完整的数据表格、资金流向、个股评分。OpenClaw在文本超过textChunkLimit时自动做content compaction(LLM summarize),数据表格被"智能压缩"掉了。

框架认为"帮你优化了"——但在数据密集场景下,AI的"智能"是灾难。

**P2 — 信息过载后关键规则失效**
当SOUL.md里堆满了各种操作规范、当session膨胀到几万tokens,Agent开始"选择性遵守"规则。管家蜘蛛越界做投资分析。交易蜘蛛忽略数据验证规则。

不是模型变笨了,而是关键信息被噪声淹没了。

### 解决:双层控制 — Context Engineering + Harness

#### 第一层:Context Engineering(设计Agent的信息架构)

设计Agent每次推理时看到的完整信息结构:

1. **SOUL.md放在system prompt最前面** - Agent的"宪法",身份定义、决策框架、绝对禁止项。保持精简,只放最核心的约束
2. **AGENTS.md跟在SOUL.md后面** - 定义操作规范和协作协议
3. **Skills通过extraDirs配置按需加载** - Trading有15个Skills共68000+行内容,不可能全放在system prompt里。只在Agent需要用到某个Skill时才注入上下文
4. **shared-context/是跨Agent的共享状态** - Agent通过工具主动读取
5. **Obsidian Vault是冷存储** - 归档产出但不参与推理

**关键洞察**:
- LLM的上下文窗口不是等价的。system prompt前面的信息权重远高于后面的
- session膨胀到几万tokens后,早期消息的影响力被稀释
- 类似操作系统的内存管理:热数据放缓存,冷数据放磁盘,关键数据常驻内存

**规则措辞必须面向最弱的模型**:
多模型fallback环境下(GPT-5.4超时 → Qwen3.5+ → Ollama qwen3:8b),规则遵循率随模型能力递减:

- "建议不要编造数据" → GPT-5.4基本遵守,Qwen3.5+偶尔遵守,qwen3:8b几乎无视
- "MUST: 不编造数据" → 各模型遵守率显著提升
- "MUST + P0 + NON-NEGOTIABLE" → 即使弱模型也能保持较高的遵守率

多模型fallback时,不知道哪次推理会用弱模型,所以所有关键规则都要按最弱模型的理解能力来写。显式>隐式,硬规则>软建议。

#### 第二层:Harness(框架自动管理)

Agent 7×24运行,session会持续膨胀——你设计得再好,运行一天之后上下文就变了。框架替Agent管,OpenClaw的harness配置提供自动化的上下文生命周期管理:

| 机制 | 触发条件 | 动作 | 为什么需要 |
|------|----------|------|------------|
| compaction memoryFlush | Session超过40K tokens | 提取精华到memory/YYYY-MM-DD.md | 防止session无限膨胀 |
| contextPruning | 上下文超过6小时 | cache-ttl裁剪,保留最近3条 | 防止旧上下文干扰新推理 |
| session reset | 每天5:00或空闲30分钟 | 自动重置 | 防止跨天数据残留 |
| session maintenance | 文件超过7天 | 自动清理,磁盘上限100MB | 防止磁盘被撑满 |
| self-improving-agent Skill | Agent启动时 |注入.learnings/历史经验 | 确保学到的东西不丢失 |

**实际的openclaw.json配置**(每个参数背后都是真实事故):

```json
{
  "compaction": {
    "mode": "safeguard",
    "memoryFlush": {
      "enabled": true,
      "softThresholdTokens": 40000,
      "prompt": "Distill to memory/YYYY-MM-DD.md. Focus: decisions, state changes, lessons, blockers."
    }
  },
  "contextPruning": { "mode": "cache-ttl", "ttl": "6h", "keepLastAssistants": 3 },
  "session": {
    "reset": { "mode": "daily", "atHour": 5, "idleMinutes": 30 },
    "maintenance": { "pruneAfter": "7d", "maxDiskBytes": 104857600 }
  },
  "hooks": {
    "bootstrap": ["self-improving-agent"]
  }
}
```

**跨会话记忆恢复链**(Agent重启后如何"想起来自己是谁"):

```
新 session 启动
↓ self-improvement hook: 读 SOUL.md → AGENTS.md → MEMORY.md → .learnings/
↓ memorySearch: 从 memory/ + sessions 中检索与当前任务相关的历史上下文
↓ 读取 shared-context/ (团队实时状态)
Agent 恢复到"知道自己是谁、做过什么、团队现在在干什么"的状态
```

---

## 核心工程问题二:让Agent真正"记住"并"成长"

### 问题:Agent今天犯的错,明天还会犯

这是一个比上下文管理更深层的问题。chatbot每次对话从零开始,所以它每次都犯同样的错是正常的。但如果你的Agent 7×24运行、每天处理几千次LLM调用,你会无法接受它反复犯同一个错误。

**交易蜘蛛5次把龙虎榜API字段名搞错**:
BILLBOARD_BUY_AMT写成BUY_AMT,每次session重置后记忆丢失,下一次又犯。

用户纠正"昨天建议买军工,今天跌了就转空",Agent当场改了,但三天后遇到类似场景又给出同样的单向建议。

chatbot和Agent的分水岭就在这里:Agent应该能从错误中学习,并且下次不犯。

### 解决:五层记忆 — 从人类认知模型中借鉴

设计记忆系统时,作者参考了人类记忆的分层模型:工作记忆(短期)→长期记忆(经验)→程序性记忆(技能)。Agent的记忆也应该有不同的时间尺度和管理方式:

| 层 | 存储 | 时间尺度 | 管理方式 | 典型内容 |
|----|------|----------|----------|----------|
| L1 身份层 | SOUL.md(精简核心) | 永恒 | 人工确认修改 | 身份+硬约束+决策框架 |
| L2 长期记忆 | MEMORY.md(<3000 tokens) | 长期 | Agent自主维护 | 结构化经验(✅成功模式/❌失败教训) |
| L3 中期记忆 | memory/YYYY-MM-DD.md + memory.db | 中期 | Harness自动提取 | Session超过40K tokens时的精华快照 |
| L4 短期记忆 | .learnings/(ERRORS/LEARNINGS/FEATURES) | 短期 | Agent即时记录 | 错误记录、用户纠正、最佳实践 |
| L5 持久化 | Skills + Obsidian + ontology + vector_store.db | 持久 | 共享/归档 | 技能库+知识归档+知识图谱+向量检索 |

### 记忆自主迭代 — 6步循环

这是整个系统最核心的机制。没有这个循环,Agent只是chatbot;有了这个循环,Agent才是真正的Agent。

```
1) 触发事件
   操作失败 · 用户纠正 · 发现更优做法 · 需要新能力
   任意一种都会触发即时记录

2) .learnings/ 即时记录
   ERRORS.md · LEARNINGS.md · FEATURE_REQUESTS.md
   "状态: pending — 低成本、高频率、不审查直接写入"

3) 每日反思 Cron (23:00-23:45)
   扫描.learnings/所有pending条目 → 评估复现频率和重要性 → 验证≥3次?
   ✓ ≥3次 promote到MEMORY.md
   ✗ <3次 保留pending,继续观察

4) promote到MEMORY.md
   长期记忆 · <3000 tokens硬上限 · 超限时Agent自主精简(合并相似、删除过时)

5) 下次Session加载
   self-improvement hook · bootstrap注入 · 检查.learnings/ · 引用历史经验

6) Agent行为改进
   下次遇到同样问题时自动避免 — 迭代完成

🔒 SOUL.md修改— 需要用户确认(Agent不能自己改自己的"宪法")
```

**真实进化案例**:

```python
用户纠正: "昨天建议买军工,今天跌了就转空"
↓
即时记录 (.learnings/):
"[LRN-20260303-001] correction | priority: high | status: pending
军工策略在地缘利好场景下未充分强调短线拥挤与顶背离风险
Suggested Action: 条件单模板 — 入场带失效位 + bullish/base/bear 三情景"
↓
每日反思cron (23:30): promote到MEMORY.md
↓
MEMORY.md: "❌ 事件驱动标的必须用条件单模板"
↓
三周后遇到类似板块轮动:
交易蜘蛛直接引用了这条经验
```

这不是我写的规则——是Agent从纠正中自己提炼出方案,自己写入长期记忆。

**更多真实进化记录**:

| 发现 | 进化 | 来源 |
|------|------|------|
| SOUL.md信息过载导致规则失效 | 精简核心,非核心规则迁移到Skills按需加载 | 行为异常排查 |
| delivery=ok ≠ 知识库已落库 | 反思同时核对投递+文件存在性 | 管家零产出事件 |
| butler零产出但反思说"正常" | 建议性兜底→硬门禁(产出为空=失败) | 运维巡检 |
| macro→trading引用缺乏追溯 | 强制结构化引用+验证字段 | 数据追溯困难 |
| trading频道刷屏(双发送链路) | 幂等键+单层重试+节流 | P0事故 |
| 军工策略只看事件驱动 | 条件单模板:入场+失效位+三情景 | Agent自提方案 |

### 假设驱动的迭代 — 从修Bug到科学方法

记忆系统最有深度的进化不是修某个具体的Bug,而是Agent学会了主动提出假设并验证——这是从"被动修复"升级到"主动改进"的关键一步。

每日反思中,Agent会基于当天的工作提出3-5条可验证假设,晚间反思时用实际数据评估:

| 假设 | 验证结果 | 后续动作 |
|------|----------|----------|
| 评分报告加上推理过程可降低用户质疑 | ✓ 已验证:Trading加上推理链后用户追问显著减少 | 固化为评分模板硬性要求 |
| Macro→Trading引用上游结论可减少重复分析 | ✓ 已验证:从"每次重新分析"变为"引用+增量" | 写入协作协议 |
| 端到端评测集比单点指标更能提升日报质量 | 验证中 | 正在建立评测基准 |

验证通过的假设被固化为规则或Skill,验证失败的被标注原因并淘汰。Agent不只是"犯错后改正",而是在主动寻找改进空间——从reactive到proactive的跃迁。

### 自主进化机制:哪些是OpenClaw自带的,哪些是我们加的

理解这套记忆系统需要区分框架能力和运营优化——很多人问"OpenClaw是不是开箱即用",答案是"框架能力开箱可用,但要跑好需要大量运营层设计"。

| 能力 | OpenClaw框架自带 | 我们的运营层优化 |
|------|------------------|------------------|
| Session管理 | compaction、contextPruning、session reset、session maintenance | 调优参数(40K/6h/30min)来自多次事故复盘 |
| self-improving-agent Skill | ❌ 框架不自带 | 额外安装的Skill——Agent启动时注入.learnings/提醒 |
| Memory flush | 超过阈值自动提取精华到memory/ | 定制flush prompt强调"decisions/state-changes/lessons/blockers" |
| Skills加载 | extraDirs按需注入 | 15个Trading专属Skill、33个全局共享Skill,按需加载 |
| ACP委派 | sessions_spawn + 编码Agent session管理 | 委派策略(什么任务用什么编码专家)、TTL和并发调优 |
| 反思+自我迭代 | ❌ 框架不自带 | 完全自建——每日23:30每个Agent独立反思+Zoe汇总 |
| 三态通信协议 | ❌ 框架不自带 | Zoe自主设计——从刷屏问题出发,迭代到V1线程协议 |
| Task Watcher | ❌ 框架不自带 | Zoe设计+ACP编码落地——task-watcher Skill |
| MEMORY.md容量管理 | ❌ | memory_maintenance.py每周压缩+Agent自主精简 |
| ontology知识图谱 | ❌ | 自建schema.yaml + graph.jsonl实体关系 |

OpenClaw提供了优秀的框架级基础设施(Session管理、Harness、ACP),但让Agent真正"活"起来的进化机制——反思迭代、协作协议、Task Watcher、记忆压缩——都是在框架之上的运营层设计。

---

## 核心工程问题三:多Agent协作是协议问题,不是群聊问题

### 问题:把Agent放进群聊 ≠ 协作

大多数人对Multi-Agent的直觉是"给几个Agent一个聊天群,它们就能协作"。实际上,这和把几个工程师拉到一个没有流程规范的群聊里没有区别——有沟通能力不等于有协作能力。

**Macro和Trading在"伊朗局势对A股影响"上互相"收到/确认/感谢"刷了十几轮。**

分析早就做完了——Macro判断"油价涨幅>10%→通胀逻辑主导→黄金反跌"(实际走势:油价+14%,黄金-5%,判断准确)——但分析之后两个Agent客套的token比分析本身还多。

根因不是"Agent太客套"。根因是缺乏终态协议。Discord配置中requireMention=true表示Agent只在被@时才回复。当两个Agent互相@,A→B→A→B......这就是经典的ACK storm,和TCP协议早期遇到的问题是一样的。

解法也是一样的:设计协议。不是告诉Agent"少说话"——实际观察中"建议"式规则在弱模型上几乎不起作用——而是设计一个有状态机的通信协议。

### 解决:协议级设计 → 真实案例

#### 实例:下周A股策略圆桌讨论

Zoe发起圆桌 → Macro提供宏观研判 → Trading回应策略建议 → 按固定三态协议有序收敛:

**Step 1 — Zoe发起议题 + Macro/Trading按协议confirmed**

**Step 2 — Trading基于Macro研判给出详细策略(confirmed输出)**

**Step 3 — Trading输出final(DRI结论+完整推理过程)**

**Step 4 — 协议收敛(final后全员静默)**

#### 协议设计

**固定三态通信协议 + V1线程协议**(被刷屏教训后设计,已迭代到V1版本,沉淀到AGENTS.md):

```
固定三态协议(强制)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[request] @对方 + ack_id + 期望动作 + 截止时间
模板: @agent [state=request] [ack_id=topic-v1-202603081430]

[confirmed] @发起方 + 相同 ack_id + 版本号/生效时间/关键结论
模板: @requester [state=confirmed] [ack_id=...] 版本=v2

[final] @相关方 + 相同 ack_id + 终态收敛(全线程仅1条)
发出后全员进入静默,"收到/感谢/OK" → NO_REPLY

V1线程协议(2026-03-08起)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 同一线程只允许一个ack_id,新一轮必须新开
• final后禁止续话;必须补充时优先edit既有消息
• sessions_send超时≠失败 → 同一ack_id不得重试
• 同一内容最多重试1次;第二次超时 → shared-context/文件投递
⏰ 5分钟无confirmed → 催办1次 · 10分钟仍无 → 升级Zoe仲裁
```

**子线程策略**:多轮协作的内容任务默认开专用子线程(命名:<主题>-<负责人>-<日期>),主频道只同步三次状态:[Dispatch] → [ACK] → [DraftReady]。

#### 三种通信机制

| 机制 | 用途 | 例子 |
|------|------|------|
| sessions_send | 实时任务分派/圆桌讨论 | Zoe→Macro "分析伊朗局势" |
| shared-context/ | 异步状态共享 | Macro写入宏观因子包→Trading直接读取 |
| 知识归档 | 结构化素材接口 | ainews报告末尾留"改写要点"→content消费 |

**shared-context/的核心价值**:从消息驱动升级到状态驱动。Trading不需要每次问Macro"今天宏观怎么样",直接读intel/finance_news_latest.json。sessions_send适合实时触发,但不可靠(超时、重复)——关键数据走文件才可追溯。

Zoe主导了shared-context/的标准化:

```
shared-context/
├── agent-sessions/          # ACP编码专家的session状态(30个claude/codex session)
├── agent-runs/             # Agent运行记录
├── monitor-tasks/          # Task Watcher持久化存储
│   ├── tasks.jsonl         # 任务注册(小红书审核/ACP完成/cron健康等)
│   ├── watcher.log         # 轮询日志
│   ├── audit.log           # 审计追踪
│   ├── dlq.jsonl           # 死信队列(处理失败的任务)
│   └── notifications/      # 通知记录
├── intel/                 # 情报共享(finance_news_latest.json等)
├── roundtable/             # 圆桌讨论记录
├── decisions/             # 重大决策存档
├── job-status/            # cron任务状态
├── knowledge-base/        # 共享知识
├── status/                # 各Agent当前状态JSON
├── tech-radar.json        # 技术雷达(Adopt/Trial/Assess三级)
├── memory-maintenance-latest.json  # 最近一次记忆压缩报告
└── PROJECT_STATUS.md      # 项目全局状态(Zoe维护)
```

这不是一次性设计出来的——是Zoe在实际运营中逐步标准化的。每增加一个新的协作场景(ACP编码、Task Watcher、Tech Radar),Zoe就在shared-context/中增加对应的标准化目录和文件格式。

**DRI原则**:一个问题只有一个Directly Responsible Individual出最终结论。非DRI只能补充,不能覆盖。Zoe组织和归档,不替代专业Agent出专业意见。

#### 协议优化后的自主反思

协议落地后,Agent不只是"按规则执行"——它们会主动反思效果并提出改进方向。从初版"禁止客套"到V1"线程级收敛",每一步协议优化都来自Agent的.learnings/经验沉淀——这正是五层记忆系统的价值所在。

**最新进展**(2026-03-08):Zoe刚完成了一次全员通信标准下沉——修改了26个文件(6个Agent的AGENTS.md + SOUL.md + 相关Skill文档),把通信硬规则统一写入每个Agent的本地配置。同时执行了全员通信路径审计,识别出main/SOUL.md与圆桌Thread规则的冲突并修复。

#### 五条联动链路

Agent之间不是各干各的,是上游主动为下游准备接口:

| 链路 | 流转 | 机制 |
|------|------|------|
| ainews→content | ainews每份报告末尾留"改写要点" | 约定接口格式 |
| ainews→Zoe | Tech Radar技术雷达→Zoe评估与决策 | shared-context/tech-radar.json |
| Macro→Trading | 宏观因子包(DXY/US10Y/油价方向/Fed路径/板块映射) | shared-context/intel/ |
| Trading→Macro(美股跨时区) | Trading 05:10夜报→Macro 05:20宏观复盘 | 时序联动 |
| Macro→Trading(周末递进) | 18:30宏观→19:30市场→20:30技术 | 递进链路 |
| Zoe→全团队 | 23:45跨workspace读取6 Agent产出+.learnings/ | 反思汇总 |

**Tech Radar真实示例**——ainews每日维护的技术雷达,分为Adopt(已验证可用)、Trial(值得尝试)、Assess(持续观察)三级:

```json
{
  "adopt": [
    { "name": "MCP Protocol", "reason": "MCP 2.0发布,三大框架推进标准化" }
  ],
  "trial": [
    { "name": "OpenAI Skills Catalog", "reason": "582→947星,可参考Skill格式" },
    { "name": "ReMe Agent记忆管理", "reason": "独立记忆工具包,评估替代方案" }
  ]
}
```

Zoe消费Tech Radar后做源码级评估,判断对现有系统的影响——本周就基于此发起了ReMe评估并委派Claude Code落地PoC。

### 安全边界 — Agent能改什么、不能改什么

安全在于限制Agent能触碰的范围:

| 安全层 | 机制 | 教训 |
|--------|------|------|
| 执行权限 | exec.security: allowlist | Content曾自己改坏配置→改为白名单执行 |
| 配置保护 | SOUL.md / openclaw.json不允许Agent修改 | Agent把自己的"人格"改松→行为失控 |
| 密钥隔离 | API keys在env中,不在文件中 | 防止暴露到session或Discord |
| 代码审查 | ACP编码走review流程 | Agent生成的代码不直接部署 |

### Task Watcher — 解决"Agent说了会做但实际没做"

Agent最难发现的问题不是崩溃或报错,而是**"说了会做但实际没做"**。

Content蜘蛛发完小红书说"审核通过后通知你"——但session已经结束了,它根本做不到异步回调。更隐蔽的是cron任务"执行了"但零产出——反思也说"一切正常"。

Zoe主导设计了一套Task Callback Event Bus——插件式架构,5个组件各司其职,把异步监控下沉到cron级别:

```
注册任务 → tasks.jsonl(shared-context/monitor-tasks/)
↓
Cron (*/3 min) → Watcher → Adapter检查状态 → 状态变化?
↓ Yes
Policy决策 → Notifier发Discord
```

- **Adapter插件**:小红书审核状态、GitHub PR、ACP编码任务——想监控什么加一个Adapter
- **Policy策略**:通知频率、升级、重试都可配
- **6小时超时保护**(默认),3次投递失败自动升级,不会死循环、不会卡死

这套系统由Zoe自行设计 → 委派Claude Code实现 → 130个单元测试 → 开源发布为OpenClaw Skill。从需求到代码到测试到发布,我只在方案评审时介入,其余由Agent团队完成。

### 通信Guardrail + 异步状态链(最新进展)

Task Watcher解决了"异步任务有没有产出"的问题,但更深层的问题是:Agent之间的通信本身缺乏系统级约束。message被误用为内部控制面、timeout不等于失败却被当作失败处理、completed和delivered无法区分——这些都不是靠文档规则能解决的。

Zoe自主设计并委派ACP编码专家实现了一套通信Guardrail + 请求生命周期状态链(~3000行Python),核心组件:

| 模块 | 行数 | 作用 |
|------|------|------|
| agent_comm_guardrail.py | 383 | 5条硬性规则:拒绝message误用、阻止身份伪造、拦截ack_id重发 |
| agent_request_models.py | 289 | 11态生命周期模型:accepted→routed→queued→started→completed→delivered |
| agent_request_store.py | 529 | 文件级状态存储,requests.jsonl + events.jsonl全链路审计 |
| completion_bus.py | 507 | 异步完成投递总线,producer-consumer模式 |
| acp_state_bridge.py | 502 | ACP编码任务的状态桥接 |
| dead_letter_queue.py | 271 | 投递失败兜底队列 |

**设计决策**:
- **timeout≠failed**:超时只是控制面观察结果,任务可能已经在执行——引入ambiguous_success语义
- **completed≠delivered**:工作完成≠结果送达,分离两个状态避免投递失败覆盖工作成果
- **通信生命周期独立于业务TaskState**:不污染现有Task Watcher的submitted→completed→failed状态机
- **文件级状态源**:先用shared-context/agent-requests/跑通,不依赖Redis/MQ等重量级设施

这套系统从"Zoe发现问题 → 设计方案 → 委派编码 → 代码实现 → 测试验收",我只在方案确认环节介入,其余环节由Agent自主完成——是Agent从"执行者"进化为"系统设计者"的典型案例。

---

## 整体架构总结 — 五层工程视角

回过头看,整个系统的核心设计可以归结为五个层次:

| 层 | 核心机制 | 解决什么问题 |
|----|----------|--------------|
| 通信层 | 三态协议+ack_id+四层一体化+shared-context/ | Agent之间如何可靠地协作 |
| 记忆层 | 五层分层存储+Harness自动管理+反思迭代 | Agent如何记住经验并持续成长 |
| 自愈层 | 三层自愈架构+heartbeat-guardian+memory_maintenance | 系统如何7×24稳定运行 |
| 进化层 | .learnings→promote→MEMORY+Skill自研+ClawHub发布 | Agent如何从"执行者"变成"设计者" |
| 编排层 | Zoe巡检+圆桌主持+Task Watcher+ACP委派 | 谁来管理和协调这一切 |

这五层不是独立的——它们相互依赖、相互强化。通信层的三态协议是Zoe在编排层中发现问题后设计的。记忆层的压缩策略是自愈层的一部分。进化层的Skill自研能力来自通信层的跨Agent协作。

---

## 跑了半个月之后的认知变化

### 1. 90%的时间花在工程问题上,不是AI问题上

Session膨胀、消息风暴、配置被改坏——解法在分布式系统和SRE经典知识中,不在AI论文里。Agent系统的瓶颈不是模型能力,是基础设施的成熟度。模型升级是锦上添花,通信协议、记忆架构、自愈机制才是决定成败的底座。

### 2. AI的"智能"在生产环境中经常是灾难

Discord消息被"智能压缩"砍掉了数据表格,Agent"智能修复"自己的配置改坏了工具名,管家蜘蛛在session膨胀后"智能地"越界做投资分析。

在需要精确、可预测输出的场景下,"智能"反而是负面特性。显式>隐式,硬规则>软建议,可预测>可解释。

### 3. 持续运行的系统必然退化——不是bug,是热力学

配置堆积、记忆过长、session膨胀、磁盘撑满——这些会确定性地发生。对策不是"一次设置好",而是建立反退化机制栈:compaction管session,maintenance管记忆,heartbeat-guardian管配置,巡检管行为漂移。

用Agent运维Agent,用cron监控cron——每层兜底机制都需要自己的兜底。

### 4. 协作是协议问题,不是prompt问题

两个Agent放在同一个Thread里不写协议,等价于两个进程共享内存不加锁。Macro和Trading用同一个模型、同一个知识库,刷屏时每条回复都言之有物——加上三态协议后产出从十几轮废话变成了一份可执行策略文档。模型没变,变的是规则。

### 5. Agent最大的价值不是执行力,而是"参与设计"

当Agent从"你让我做什么我就做什么"进化到"我发现了问题,调研了三种方案,推荐B,你确认我就落地"——这时它才真正成为团队成员。

十个进化案例里,大多数的起因不是"我让它做什么",而是"它遇到了问题然后自己想办法"。系统设计的目标不是让Agent听话,而是让它有能力自己解决问题。

---

## 如果你也想试试

不需要照搬6个Agent。从1个开始。整个系统从零到6个Agent稳定运行花了大约半个月的下班时间——不是开发时间,是调试和填坑时间。

### 第1-2天:先让1个Agent稳定运行

最重要的三件事:

1. **SOUL.md保持精简,只放核心约束**。把它当"宪法"不是"操作手册"——非核心规则放Skills按需加载
2. **Session管理参数第一天就设好**:idleMinutes=30、pruneAfter=7d、maxDiskBytes=100MB。不设=定时炸弹
3. **从第一天就启用.learnings/+反思cron**。没有反思的Agent只是chatbot,不是Agent

### 第3-5天:加第2个,开始处理协作

4. **Discord配置比你想的复杂10倍**。每个Agent需要独立Bot账号。requireMention、textChunkLimit、delivery.mode、子Thread创建、Bot权限——每个都有坑,而且组合起来的症状让你根本猜不到是哪个配置的问题
5. **协作需要协议,不是群聊**。两个Agent在群聊里会互相ACK到死。固定三态协议+ack_id+超时升级,两个都不能少

### 第2周起:逐步扩展到完整阵型

6. **规则用最强措辞,面向最弱模型**。LLM对"建议"式规则的遵循率远于"MUST",尤其在长上下文和弱模型上
7. **"成功"要严格定义**。投递成功≠归档成功,无报错≠有产出,Agent说"正常"≠真正正常
8. **Agent不回复是常态**——准备好Task Watcher和重试机制
9. **shared-context/是协作基石**——sessions_send不可靠(超时、重复),关键数据走文件才可追溯
10. **每加一个Agent都需要半天到一天的调试**。急于求成=浪费更多时间在排查上

装好不难,跑通也不难。难的是:让6个Agent在没有你盯着的时候也能稳定产出、自我修正、协作不打架。这不是prompt问题,是系统工程问题。

---

## 附录:技术栈快速参考

### LLM模型分层

| 任务类型 | 模型 | 成本 |
|----------|------|------|
| 主对话/反思/圆桌 | GPT-5.4 | |
| ACP编码任务 | K2.5 / GPT-5.4 | $ |
| Cron日常任务 | Qwen3.5+ / K2.5 | $ |
| 心跳/健康检查 | Ollama qwen3:8b | 免费 |

**Fallback链**:gpt-5.4 → k2.5 → qwen3.5-plus → ollama/qwen3:8b

### 核心Harness配置

```json
{
  "compaction": { "mode": "safeguard", "memoryFlush": { "softThresholdTokens": 40000 } },
  "contextPruning": { "mode": "cache-ttl", "ttl": "6h", "keepLastAssistants": 3 },
  "session": {
    "reset": { "atHour": 5, "idleMinutes": 30 },
    "maintenance": { "pruneAfter": "7d", "maxDiskBytes": 104857600 }
  },
  "acp": { "maxConcurrentSessions": 6, "ttlMinutes": 120 }
}
```

### 数据源

| 市场 | 数据源 | 覆盖 |
|------|--------|------|
| A股 | AKShare + TuShare Pro | 实时行情+历史+财务+龙虎榜+北向 |
| 美股/港股 | yfinance + Finnhub | 行情+新闻+基本面 |
| 信息采集 | Tavily + RSS 13源 + GitHub Trending + 54平台热榜 + arXiv | 搜索+新闻+热点+论文 |
| 浏览器 | agent-browser (Playwright) | JS渲染页面(X/Twitter、雪球等) |

### 部署配置

| 组件 | 配置 |
|------|------|
| 硬件 | Mac本地7×24 |
| 进程守护 | launchctl + ThrottleInterval=10 |
| 自愈 | 2086行脚本(heartbeat-guardian / check_cron_health / memory_maintenance) |
| 备份 | 每日03:00全量备份 |
| 监控 | Zoe 3次/天巡检 + 系统crontab 15分钟健康检查 |
| 知识归档 | Obsidian Vault + obsidian-livesync |

---

## 精读总结

这篇文章的价值在于它不是理论,而是真实的工程实践记录。作者从0到1构建了一个完整的多Agent系统,遇到的每一个坑都给出了详细的解决方案和真实案例。

**核心收获**:

1. **工程重于AI** - Agent系统90%的精力花在工程问题上,通信协议、记忆管理、自愈机制才是决定成败的底座
2. **显式优于隐式** - 在生产环境中,AI的"智能"往往是灾难,硬规则、可预测的输出更重要
3. **协议驱动协作** - 多Agent协作不是群聊,而是需要精心设计的协议和状态机
4. **持续进化机制** - Agent从"执行者"到"设计者"的关键在于建立完整的反思迭代循环
5. **热力学定律适用** - 持续运行的系统必然退化,需要建立反退化机制栈

这篇文章对于任何想要构建多Agent系统的人来说都是必读的参考资料。它不仅展示了"能做到什么",更重要的是详细记录了"怎么做"、"会遇到什么问题"、"如何解决"。

---

**精读完成时间**: 2026年4月10日
**文档生成方式**: AI辅助精读 + 结构化整理
**推荐阅读人群**: AI工程师、系统架构师、想要构建Agent系统的开发者

---

*本文基于原微信文章《OpenClaw实战:一个人、一台Mac、六个AI Agent》的精读整理,保留了原文的核心内容和案例,并增加了结构化的梳理和总结。*
