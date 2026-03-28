---
title: '深度拆解 Superpowers 和 gstack：AI 编程真正的差距，不在模型，在工作流'
description: 'Superpowers 是能力编排系统，gstack 是组织流程系统。它们都在重塑 AI 编程，但走的是两条完全不同的路。'
date: '2026-03-28'
tags: ['AI编程', 'Superpowers', 'gstack', 'Agent架构', '工作流']
category: '技术解读'
---

> 来源：知乎 | 原文链接：[深度拆解 Superpowers 和 gstack：AI 编程真正的差距，不在模型，在工作流](https://zhuanlan.zhihu.com/p/2019440154893374100) | 日期：2026年3月23日

---

## 一、核心观点摘要

**一句话总结**：Superpowers 是"能力编排系统"，gstack 是"组织流程系统"。真正决定 AI 写代码质量的，往往不是模型本身，而是你如何组织它的工作方式。

过去一年，AI 编程工具最大的变化，不是模型更强了，而是大家逐渐意识到一件事：真正决定 AI 写代码质量的，往往不是模型本身，而是你如何组织它的工作方式。

问题已经从"用哪个模型"慢慢转向了：
- 怎么让 AI 不要一上来就胡乱写代码？
- 怎么让它先想清楚需求、边界、测试和设计？
- 怎么让它像一个靠谱的工程团队，而不是一个情绪不稳定的实习生？

最近两个很有代表性的开源项目，正好走了两条不同但都很值得研究的路径：
- **Superpowers**（obra/superpowers）：把 AI 编程流程建立在 skills（技能）之上，强调可组合、可复用、可自动触发的工程化工作流
- **gstack**（garrytan/gstack）：把 AI 编程流程建立在 roles（角色）之上，用"CEO、工程经理、设计师、QA、发布经理"等角色，把 Claude Code 组织成一个"虚拟工程团队"

**核心洞察**：Superpowers 让 AI 更像工程师，gstack 让 AI 更像一个团队。

---

## 二、核心概念图谱

```mermaid
graph TB
    A[AI编程范式演进] --> B[传统方式]
    A --> C[Superpowers]
    A --> D[gstack]

    B --> B1[直接对AI说：帮我把这个功能写了]

    C --> C1[核心理念: 能力编排系统]
    C1 --> C2[控制任务执行粒度]
    C2 --> C3[更像工程操作系统]
    C3 --> C4[让AI像工程师]

    D --> D1[核心理念: 组织流程系统]
    D1 --> D2[控制决策视角粒度]
    D2 --> D3[更像AI版软件组织架构]
    D3 --> D4[让AI像团队]

    C --> E[共同目标: 解决AI编程失控问题]
    D --> E
```

```mermaid
graph LR
    A[Superpowers vs gstack] --> B[维度1: 控制粒度]
    A --> C[维度2: 自动化程度]
    A --> D[维度3: 抽象层级]

    B --> B1[Superpowers: 任务执行粒度]
    B --> B2[gstack: 决策视角粒度]

    C --> C1[Superpowers: 隐式接管]
    C --> C2[gstack: 显式操盘]

    D --> D1[Superpowers: 底层runtime+workflow engine]
    D --> D2[gstack: 高层组织与决策分工]

    E[结果] --> E1[Superpowers: 自动触发技能,自动套用工程工作流]
    E --> E2[gstack: 显式调用角色,像管理团队一样管理agent]
```

```mermaid
mindmap
  root((AI编程方法论))
    Superpowers
      核心理念: 能力编排系统
      特点
        可组合的skills
        可复用
        可自动触发
      流程环节
        brainstorming
        using-git-worktrees
        writing-plans
        subagent-driven-development
        test-driven-development
        requesting-code-review
        finishing-a-development-branch
      优势
        让AI少跳步骤
        更严格的TDD/plan/review纪律
        跨平台可迁移性
        流程尽量自动内化
    gstack
      核心理念: 组织流程系统
      特点
        明确的角色分工
        CEO
        工程经理
        设计师
        Reviewer
        QA
        Security Officer
        Release Engineer
      流程环节
        /office-hours: 描述在做什么
        /plan-ceo-review: 从产品/业务视角审视
        /plan-eng-review: 架构与测试
        /plan-design-review: 设计维度
        /review: 代码审查
        /qa: 真实页面验证
        /ship: 发布
      优势
        明确角色视角
        强浏览器测试与QA
        显式管理工作流
        更适合Web产品和创业团队
    共同点
      反对"直接让AI写代码"
      都在试图解决"AI编程失控"问题
      AI需要流程,不只是prompt
      AI需要角色或技能约束
      AI编程的关键不是"生成",而是"决策质量"
```

---

## 三、关键问题与解答

### 问题1：Superpowers 和 gstack 到底分别在解决什么问题？

**现状/困境**：
AI 写代码的核心问题不是不会写，而是没有正确的约束和流程。直接对 AI 说"帮我把这个功能写了"，AI 会：
- 不澄清需求
- 不先写测试
- 不主动拆解任务
- 不区分设计问题、架构问题、实现问题、验证问题
- 最后生成一堆"看起来很忙，实际上不可维护"的代码

**解法/方案**：
Superpowers 和 gstack 都在做一件事：把这种混乱过程重新结构化。

**Superpowers 的解决方式**：
- 把开发过程拆成一系列可触发的技能
- 让这些技能在合适的时机自动生效，而不是每一步都要用户显式调用
- 强调"先设计，后实现；先测试，后代码"
- 通过 planning、TDD、subagent、review、branch finishing 等机制，把执行流程做稳

**gstack 的解决方式**：
- 把软件团队中的"分工"映射成 Claude Code 中的"操作入口"
- 不再对一个模糊的"AI 助手"说话，而是在调用某个明确职能的角色
- 提供从 office hours、plan、review、qa 到 ship/retro 的组织化步骤
- 让你需要时有意识地调用某个角色，让它从对应立场进行分析和执行

**对比分析**：

| 维度 | Superpowers | gstack |
|------|-----------|--------|
| 核心定位 | 能力编排系统 | 组织流程系统 |
| 约束方式 | skills（技能） | roles（角色） |
| 自动化程度 | 隐式接管，自动触发 | 显式操盘，需要手动调用角色 |
| 控制粒度 | 任务执行粒度 | 决策视角粒度 |
| 抽象层级 | 更底层，靠近工程动作本身 | 更高层，偏组织与决策分工 |
| 适合场景 | 后端系统、基础设施、编译器/内核/推理引擎、大型重构 | 创业者、技术负责人、产品/设计/工程混合角色、Web应用 |

---

### 问题2：Superpowers 是什么？它不是一组 prompt，而是一套"技能驱动"的开发方法论

**现状/困境**：
很多人以为 Superpowers 是"多写几个系统提示词"那么简单。

**解法/方案**：
根据项目 README，Superpowers 的核心定义是：**它是一套完整的软件开发工作流，建立在一组可组合的 skills 之上，并通过初始指令确保 agent 会去使用这些 skills**。

**核心特点**：

**1. 把开发过程拆成一系列可触发的技能**
Superpowers 官方 README 给出的基础流程包括这些环节：brainstorming、using-git-worktrees、writing-plans、subagent-driven-development/executing-plans、test-driven-development、requesting-code-review、finishing-a-development-branch。

这不是单纯的"问答式助手"，而是在模拟一个相对完整的软件开发流水线：
- 先讨论需求和设计
- 再进入工作区隔离和分支管理
- 再把任务切成细粒度计划
- 再由子 agent 分步骤执行
- 执行过程中强制 TDD
- 每个阶段之间插入 code review
- 最后再做分支收尾和提交选择

**2. 尽量让这些技能"自动触发"**
README 明确提到，Superpowers 的目标之一，是让这些技能在合适的时机自动生效，而不是每一步都要用户显式调用。

这点很重要。因为很多人以为 AI 工作流增强，就是记住一堆 `/command`。但 Superpowers 的设计更接近：**把最佳实践埋进 agent 的行为默认值里**。这比"你自己记得每一步都调用正确命令"更进一步。

**3. 强调"先设计，后实现；先测试，后代码"**
README 里写得非常明确：在设计确认后，agent 会先给出 implementation plan，并强调 true red/green TDD、YAGNI、DRY。

这其实暴露了 Superpowers 的工程立场：
- 它不相信"先写点代码看看"
- 它不鼓励一上来就全局重构
- 它希望 agent 像受过训练的工程师一样，先澄清设计、写测试、再推进实现

所以，**Superpowers 本质上不是在强化"生成能力"，而是在强化工程纪律**。

---

### 问题3：gstack 是什么？它不是技能库，而是一套"角色驱动"的 AI 工程组织

**现状/困境**：
很多 AI 写代码的问题，不是不会写，而是没有"站在正确角色视角上"思考。

**解法/方案**：
gstack 把 Claude Code 变成一个"虚拟工程团队"，其中包括 CEO、工程经理、设计师、Reviewer、QA、Security Officer、Release Engineer 等角色。

这个设计背后的思想，其实非常聪明：**很多 AI 写代码的问题，不是不会写，而是没有"站在正确角色视角上"思考**。

比如：
- 你让 AI 设计功能，它可能直接跳进实现细节
- 你让 AI 改 UI，它可能只会做"能运行"，但没有设计判断
- 你让 AI review 代码，它可能只检查语法，却没想到线上风险
- 你让 AI 做 QA，它可能压根不会真的打开浏览器验证交互

**gstack 的解决方案是**：不要让同一个 agent 用一种模糊的统一人格做所有事，而是给不同任务绑定不同角色。

**核心特点**：

**1. 核心不是"命令多"，而是"角色明确"**
README 里的 quick start 建议非常直接：
- `/office-hours`：先描述你在做什么
- `/plan-ceo-review`：从产品/业务视角重想一遍这个功能
- `/review`：对当前分支进行代码审查
- `/qa`：对 staging URL 做测试

同时，项目还列出了更多命令，例如：`/plan-eng-review`、`/plan-design-review`、`/ship`、`/browse`、`/retro`、`/autoplan`、`/setup-browser-cookies`、`/cso` 等。

这意味着 gstack 本质上在做一件事：**把软件团队中的"分工"映射成 Claude Code 中的"操作入口"**。你不再是对一个模糊的"AI 助手"说话，而是在调用某个明确职能的角色。

**2. 很强调真实开发中的"组织流程"**
比如：
- `/plan-ceo-review`：用 CEO 视角重构产品想法
- `/plan-eng-review`：用工程经理视角锁定架构、数据流、边界条件与测试
- `/plan-design-review`：会对设计维度打分并提出修改建议
- `/review`：做偏向资深工程师式的代码审查
- `/ship`：偏向发布和 PR
- `/retro`：做团队复盘

这里最值得注意的是，**gstack 并不试图"隐藏流程"。相反，它把流程显式地摆到用户面前**。所以它不像 Superpowers 那样偏"自动内化"，而更像：**把工程组织的方法论外显出来，让你像管理团队一样管理 agent**。

**3. 非常看重浏览器能力和持久会话**
gstack 的 ARCHITECTURE 文档有一个很重要的点：它认为浏览器自动化是"硬问题"，其他很多东西只是 Markdown。为了获得亚秒级延迟和持久状态，它采用了一个 long-lived Chromium daemon，让 CLI 通过 localhost HTTP 与之通信，从而避免每次工具调用都冷启动浏览器，也能保留 cookies、tabs 和登录状态。

这件事非常关键，因为它解释了为什么 gstack 不只是"几个 slash commands 的集合"。它背后其实还有一个相对清晰的运行时架构：
- CLI
- 本地 server
- 持久化 headless Chromium
- 会话状态管理

因此，当 gstack 在 README 里强调 `/browse`、`/qa`、`/setup-browser-cookies` 这些能力时，它不是停留在 prompt 层，而是已经把浏览器操作当成了一等公民。

---

### 问题4：Superpowers 和 gstack 的相同点是什么？

**现状/困境**：
AI 编程最大的问题是什么？

**解法/方案**：
尽管两者风格不同，但它们有一个共同点：**都在反对"直接对 AI 说一句：帮我把这个功能写了"**。

因为这种方式最大的问题是，AI 会：
- 不澄清需求
- 不先写测试
- 不主动拆解任务
- 不区分设计问题、架构问题、实现问题、验证问题
- 最后生成一堆"看起来很忙，实际上不可维护"的代码

Superpowers 和 gstack 都在做的，是把这种混乱过程重新结构化。

它们共同相信三件事：

**1. AI 需要流程，不只是 prompt**
从 README 可以看出，两者都不是单条提示工程，而是流程工程。Superpowers 提供的是从 brainstorming 到 development branch finishing 的完整链路；gstack 提供的是从 office hours、plan、review、qa 到 ship/retro 的组织化步骤。

**2. AI 需要角色或技能约束，而不是自由发挥**
Superpowers 用 skills 约束行为。gstack 用 roles 约束判断。本质上都在做一件事：**限制 agent 在错误的时间做错误的事**。

**3. AI 编程的关键不是"生成"，而是"决策质量"**
这其实是最核心的一点。很多开发者把 AI 编程理解成"自动写代码"。但真正成熟的工程实践里，更有价值的是：
- 什么时候该先问问题
- 什么时候该停下来设计
- 什么时候该拆任务
- 什么时候该 review
- 什么时候该用真实浏览器验证
- 什么时候该拒绝继续推进

Superpowers 和 gstack，都在增强 agent 的"决策过程"，而不只是"代码输出"。

---

### 问题5：两者最本质的区别是什么？

**现状/困境**：
很多人喜欢把它们的区别简单概括成：Superpowers = skills，gstack = roles。

**解法/方案**：
这当然没错，但还不够深。

更准确地说，它们的根本差异在于：**Superpowers 控制的是"任务执行粒度"，gstack 控制的是"决策视角粒度"**。

**1. Superpowers 更像"工程操作系统"**
Superpowers 的 skill 设计更接近一个可以不断扩展的操作层。

它关心的问题是：
- 当前应该进入 brainstorming 还是 implementation？
- 任务是否已经被拆成足够小的 steps？
- 是否应该切换到 git worktree？
- 是否应该启用 subagent-driven-development？
- 是否符合 TDD？
- 是否该触发 code review？
- 是否该 finish 当前分支？

这意味着 Superpowers 的抽象层更"底层"，更靠近工程动作本身。如果用程序设计来类比：
- gstack 更像面向对象中的"角色接口"
- Superpowers 更像底层 runtime + workflow engine

它管的是"怎么执行"。

**2. gstack 更像"AI 版软件组织架构"**
gstack 的高明之处，是它并不试图把每一步隐藏起来。

相反，它让你显式地进入不同角色：
- CEO 看价值和产品方向
- Eng Manager 看架构与测试
- Designer 看体验和视觉质量
- QA 看真实页面行为
- Reviewer 看代码风险
- Release Engineer 看交付和上线

这种设计更接近真实公司里的协作结构。

所以 gstack 的抽象层更"高层"，更偏组织与决策分工。

它管的是"谁来判断"。

**3. 一个是"能力内嵌"，一个是"流程外显"**
这是我认为最值得记住的一句话。

**Superpowers**：把工程最佳实践尽量内嵌到 agent 行为默认值里。你触发一个任务，agent 自动进入更合理的 skill 链条。

**gstack**：把工程流程显式展现在你面前。你需要有意识地调用某个角色，让它从对应立场进行分析和执行。

所以如果你喜欢一句话总结：
- Superpowers：让 AI 自己变得更像一个训练有素的工程师
- gstack：让 AI 看起来像一个组织良好的工程团队

---

### 问题6：从技术落地看，它们分别适合什么样的开发者？

**现状/困境**：
如果你只能选一个，怎么选？

**解法/方案**：

**适合 Superpowers 的人**：

**1. 你更关注"执行质量"**
比如你在做：
- 后端系统
- 基础设施
- 编译器/内核/推理引擎
- 大模型训练/serving/benchmark
- 大型重构

这些场景里，最怕的是 AI 乱改、跳步、没测试、没计划。Superpowers 通过 planning、TDD、subagent、review、branch finishing 等机制，天然更偏向"把执行流程做稳"。

**2. 你希望 agent 自动遵循流程**
如果你不想手动记很多命令，更想让 AI 自己进入合适流程，那 Superpowers 的"自动触发 skill"思路更适合你。

**3. 你想把方法论复用到不同 agent 平台**
Superpowers 不只面向 Claude Code。当前文档显示它还支持 Cursor、Codex、OpenCode、Gemini CLI 等平台。这意味着它更像一个跨平台的工作流层，而不是只绑定某个单一工具。

**适合 gstack 的人**：

**1. 你更关注"团队式决策"**
如果你是：
- 创业者
- 技术负责人
- 产品/设计/工程混合角色
- 独立开发者但想模拟团队协作

那么 gstack 会很有吸引力，因为它把你平时脑子里要切换的多重视角拆成了显式角色。

**2. 你需要强浏览器测试与 QA**
gstack 的 `/browse`、`/qa`、`/setup-browser-cookies`，加上它为浏览器持久状态专门设计的 daemon 架构，使它在"真实网页操作、登录态保持、页面验证"这条链路上明显更重。

如果你做的是：
- Web 应用
- SaaS 产品
- 管理后台
- 带复杂交互的前端
- 需要真实页面测试的产品

gstack 的优势会更直观。

**3. 你愿意显式管理工作流**
gstack 很适合喜欢"把过程看清楚"的人。它不是把一切都自动化，而是让你在关键节点明确选择：
- 现在先做产品复盘？
- 先做架构 review？
- 先 review 代码？
- 先 QA？
- 还是直接 ship？

这对于很多有经验的开发者来说，反而更安心。

---

### 问题7：怎么安装和使用？

**现状/困境**：
别只知道它们"很强"，你得知道它们是怎么落地的。

**解法/方案**：

**Superpowers 怎么用？**
Superpowers 当前支持多平台。以 Claude Code 为例，README 给出的安装方式包括：
- 官方 Claude marketplace：`/plugin install superpowers@claude-plugins-official`
- 或先添加 marketplace 再安装：`/plugin marketplace add obra/superpowers-marketplace`，`/plugin install superpowers@superpowers-marketplace`

如果是 Cursor，可以通过插件市场安装；如果是 Codex，则文档提供了通过 `~/.agents/skills/` 暴露 skills 的方式，并说明 Codex 会在启动时扫描这些 skills。

**Superpowers 的典型使用方式**
它最典型的使用姿势不是"背命令"，而是直接开始一个开发任务：
- "帮我规划这个功能"
- "我们来修这个 bug"
- "帮我实现这个 feature"

然后让 agent 自动进入：brainstorming → design validation → writing plans → subagent-driven-development → TDD → review → finish branch。

换句话说，Superpowers 更适合这样的交互方式：**你描述目标，agent 自动套用工程工作流**。

**gstack 怎么用？**
gstack 的 quick start 非常直接：
- 安装 gstack
- 运行 `/office-hours` 描述你在做什么
- 用 `/plan-ceo-review` 审视功能方向
- 用 `/review` 检查当前分支
- 用 `/qa` 检查 staging URL

README 还提供了一条非常明确的安装命令：将仓库 clone 到 `~/.claude/skills/gstack`，执行 `./setup`，再在 `CLAUDE.md` 中加入 gstack 配置和可用 skills 列表。

**gstack 的典型使用路径**
一个比较自然的工作流可能是：
- `/office-hours`：先统一上下文
- `/plan-ceo-review`：看这个需求是否值得这样做
- `/plan-eng-review`：锁定架构和测试策略
- `/plan-design-review`：避免界面和交互层面的 AI slop
- 开始实现
- `/review`：审代码
- `/qa` 或 `/browse`：做真实页面验证
- `/ship`：发 PR/发布

和 Superpowers 最大的差异是：**gstack 希望你"显式操盘"；Superpowers 更倾向于"隐式接管"**。

---

### 问题8：如果只能选一个，怎么选？

**现状/困境**：
给一个尽量实用、不绕弯的建议。

**解法/方案**：

**选 Superpowers，如果你更在意这些**：
- 让 agent 少跳步骤
- 让实现更规整
- 更严格的 TDD/plan/review 纪律
- 更强的 task decomposition
- 多平台可迁移性
- 希望流程尽量自动内化

**选 gstack，如果你更在意这些**：
- 把 AI 当作"虚拟团队"来协作
- 明确切换产品/架构/设计/QA/发布视角
- 强浏览器测试能力
- 更适合 Web 产品和创业团队语境
- 想显式控制每一步流程

---

### 问题9：真正高级的用法：不是二选一，而是组合使用

**现状/困境**：
很多人低估了一点：Superpowers 和 gstack 其实是有互补性的。

**解法/方案**：
一种非常合理的组合方式是：

**用 gstack 做高层决策**
- `/plan-ceo-review`：需求是否值得做
- `/plan-eng-review`：架构是否合理
- `/plan-design-review`：设计是否过关

**用 Superpowers 做中低层执行**
- brainstorming 的细化
- plan 的任务拆分
- subagent-driven-development
- TDD
- code review
- branch finishing

**再回到 gstack 做验证与交付**
- `/qa`/`/browse`：真实页面测试
- `/ship`：发 PR/发布
- `/retro`：团队复盘

这样你会得到一种非常强的组合：
- gstack 负责"想对"
- Superpowers 负责"做稳"
- gstack 再负责"验真"和"交付"

如果你做的是复杂 Web 产品，这套组合非常有潜力。

---

## 四、技术架构

```mermaid
graph TB
    A[Superpowers架构] --> B[Skills层]
    A --> C[流程引擎]
    A --> D[Agent]

    B --> B1[brainstorming]
    B --> B2[using-git-worktrees]
    B --> B3[writing-plans]
    B --> B4[subagent-driven-development]
    B --> B5[test-driven-development]
    B --> B6[requesting-code-review]
    B --> B7[finishing-a-development-branch]

    C --> C1[自动触发机制]
    C --> C2[技能编排]
    C --> C3[流程控制]

    D --> D1[遵守TDD]
    D --> D2[遵循工程纪律]
    D --> D3[执行plan]

    E[Superpowers特点] --> E1[跨平台支持]
    E --> E2[能力内嵌]
    E --> E3[隐式接管]
```

```mermaid
graph TB
    A[gstack架构] --> B[Roles层]
    A --> C[CLI层]
    A --> D[本地server]
    A --> E[持久化Chromium]

    B --> B1[CEO]
    B --> B2[工程经理]
    B --> B3[设计师]
    B --> B4[Reviewer]
    B --> B5[QA]
    B --> B6[Security Officer]
    B --> B7[Release Engineer]

    C --> C1[/office-hours]
    C --> C2[/plan-ceo-review]
    C --> C3[/plan-eng-review]
    C --> C4[/plan-design-review]
    C --> C5[/review]
    C --> C6[/qa]
    C --> C7[/ship]
    C --> C8[/browse]
    C --> C9[/retro]

    D --> D1[localhost HTTP通信]
    D --> D2[会话状态管理]

    E --> E1[cookies持久化]
    E --> E2[tabs持久化]
    E --> E3[登录状态保持]
    E --> E4[亚秒级延迟]

    F[gstack特点] --> F1[角色明确]
    F --> F2[流程外显]
    F --> F3[浏览器能力强]
    F --> F4[显式操盘]
```

```mermaid
graph LR
    A[组合使用架构] --> B[gstack做高层决策]
    A --> C[Superpowers做中低层执行]
    A --> D[gstack做验证与交付]

    B --> B1[需求是否值得做]
    B --> B2[架构是否合理]
    B --> B3[设计是否过关]

    C --> C1[brainstorming细化]
    C --> C2[plan任务拆分]
    C --> C3[subagent-driven-development]
    C --> C4[TDD]
    C --> C5[code review]
    C --> C6[branch finishing]

    D --> D1[/qa或/browse]
    D --> D2[/ship]
    D --> D3[/retro]

    E[结果] --> E1[gstack: 想对]
    E --> E2[Superpowers: 做稳]
    E --> E3[gstack: 验真和交付]
```

---

## 五、对比分析

### Superpowers vs gstack

| 维度 | Superpowers | gstack |
|------|-----------|--------|
| 核心理念 | 能力编排系统 | 组织流程系统 |
| 约束方式 | skills（技能） | roles（角色） |
| 控制粒度 | 任务执行粒度 | 决策视角粒度 |
| 自动化程度 | 隐式接管，自动触发 | 显式操盘，需要手动调用角色 |
| 抽象层级 | 更底层，靠近工程动作本身 | 更高层，偏组织与决策分工 |
| 流程特点 | 自动内化到 agent 行为默认值 | 显式展现在用户面前 |
| 适合场景 | 后端系统、基础设施、编译器/内核、大型重构 | Web 应用、SaaS 产品、管理后台、带复杂交互的前端 |

### 两者共同点

| 共同点 | 说明 |
|--------|------|
| 反对直接对 AI 说"帮我把这个功能写了" | 都认为这是 AI 编程失控的根源 |
| 都在试图解决"AI 编程失控"问题 | 把混乱过程重新结构化 |
| AI 需要流程，不只是 prompt | 都不是单条提示工程，而是流程工程 |
| AI 需要角色或技能约束 | 都在限制 agent 在错误的时间做错误的事 |
| AI 编程的关键不是"生成"，而是"决策质量" | 都在增强 agent 的"决策过程" |

---

## 六、数据与生态

### Superpowers 支持的平台
- Claude Code（官方 marketplace）
- Cursor（插件市场）
- Codex（`~/.agents/skills/`）
- OpenCode
- Gemini CLI

### gstack 提供的角色
- CEO：看价值和产品方向
- Eng Manager：看架构与测试
- Designer：看体验和视觉质量
- QA：看真实页面行为
- Reviewer：看代码风险
- Release Engineer：看交付和上线

---

## 七、行业趋势与预测

### AI 编程的演进方向

从这篇文章可以看出，AI 编程正在从"单次回答"演进到"结构化协作"。

过去我们说 prompt engineering。后来我们说 agent。现在更准确的词，其实是：
- workflow engineering（工作流工程）
- agent orchestration（agent 编排）
- decision scaffolding（决策脚手架）
- AI-native software process（AI 原生软件流程）

Superpowers 和 gstack，分别给出了两种可行答案：
- 一种答案是：把最佳实践封装成 skills，让 agent 按工程方法论自动执行
- 另一种答案是：把软件团队组织结构映射成 roles，让 agent 在不同职责下做判断

这两种路径，都比"直接叫 AI 写代码"成熟得多。

### 未来展望

真正高效的 AI 编程方式，未必是找到"最强模型"，而是找到"最适合你团队和项目的工作流结构"。

Superpowers 和 gstack 都说明了一件事：**AI 不缺写代码的能力，缺的是被放进一个正确的工程系统里**。谁先把这个系统搭好，谁就会在下一轮 AI 编程效率竞争里拉开差距。

---

## 八、思维导图

```mermaid
mindmap
  root((AI编程方法论))
    Superpowers
      核心理念: 能力编排系统
      技能列表
        brainstorming
        using-git-worktrees
        writing-plans
        subagent-driven-development
        test-driven-development
        requesting-code-review
        finishing-a-development-branch
      特点
        可组合
        可复用
        可自动触发
      优势
        让agent少跳步骤
        更严格的TDD/plan/review纪律
        跨平台可迁移性
        流程尽量自动内化
      适用场景
        后端系统
        基础设施
        编译器/内核/推理引擎
        大型重构
    gstack
      核心理念: 组织流程系统
      角色列表
        CEO
        工程经理
        设计师
        Reviewer
        QA
        Security Officer
        Release Engineer
      运行时架构
        CLI
        本地server
        持久化headless Chromium
        会话状态管理
      特点
        角色明确
        流程外显
        浏览器能力强
        显式操盘
      适用场景
        创业者
        技术负责人
        产品/设计/工程混合角色
        独立开发者但想模拟团队协作
        Web应用
        SaaS产品
        管理后台
        带复杂交互的前端
    共同点
      反对直接让AI写代码
      都在试图解决AI编程失控问题
      AI需要流程,不只是prompt
      AI需要角色或技能约束
      AI编程的关键不是生成,而是决策质量
    组合使用
      gstack做高层决策
        需求是否值得做
        架构是否合理
        设计是否过关
      Superpowers做中低层执行
        brainstorming的细化
        plan的任务拆分
        subagent-driven-development
        TDD
        code review
        branch finishing
      gstack做验证与交付
        /qa或/browse
        /ship
        /retro
      结果
        gstack负责想对
        Superpowers负责做稳
        gstack负责验真和交付
```

---

## 九、关键金句摘录

1. **核心区别**：Superpowers 是"能力编排系统"，gstack 是"组织流程系统"。

2. **再直白一点**：Superpowers 关心的是：AI 该按照什么方法做事；gstack 关心的是：AI 该以什么角色做判断。

3. **共同认知**：真正决定 AI 写代码质量的，往往不是模型本身，而是你如何组织它的工作方式。

4. **Superpowers 本质**：它是一套完整的软件开发工作流，建立在一组可组合的 skills 之上，并通过初始指令确保 agent 会去使用这些 skills。

5. **Superpowers 价值**：它的真正价值，不是某一个 skill 本身，而是 skill 之间形成了一个工程闭环。

6. **gstack 思想**：很多 AI 写代码的问题，不是不会写，而是没有"站在正确角色视角上"思考。

7. **gstack 解决方案**：不要让同一个 agent 用一种模糊的统一人格做所有事，而是给不同任务绑定不同角色。

8. **gstack 抽象**：它管的是"谁来判断"。

9. **Superpowers 抽象**：它管的是"怎么执行"。

10. **根本差异**：Superpowers 控制的是"任务执行粒度"，gstack 控制的是"决策视角粒度"。

11. **能力内嵌 vs 流程外显**：Superpowers 把工程最佳实践尽量内嵌到 agent 行为默认值里；gstack 把工程流程显式展现在你面前。

12. **一句话总结**：Superpowers 让 AI 更像工程师，gstack 让 AI 更像团队。

13. **组合优势**：gstack 负责"想对"，Superpowers 负责"做稳"，gstack 再负责"验真"和"交付"。

14. **行业趋势**：Superpowers 和 gstack 代表了一个趋势：AI 编程正在从"单次回答"演进到"结构化协作"。

15. **未来方向**：AI 不缺写代码的能力，缺的是被放进一个正确的工程系统里。谁先把这个系统搭好，谁就会在下一轮 AI 编程效率竞争里拉开差距。

---

## 十、总结与洞察

### 1. 范式转变：从"自动写代码"到"结构化协作"

这篇文章最核心的洞察是：AI 编程正在从"单次回答"演进到"结构化协作"。

过去我们说 prompt engineering。后来我们说 agent。现在更准确的词，其实是：
- workflow engineering（工作流工程）
- agent orchestration（agent 编排）
- decision scaffolding（决策脚手架）
- AI-native software process（AI 原生软件流程）

Superpowers 和 gstack，分别给出了两种可行答案：
- 一种答案是：把最佳实践封装成 skills，让 agent 按工程方法论自动执行
- 另一种答案是：把软件团队组织结构映射成 roles，让 agent 在不同职责下做判断

**启示**：AI 编程的成熟度，不在于你用了什么模型，而在于你设计了什么样的系统和流程来约束和引导 AI 的行为。

---

### 2. 控制粒度的两个维度：任务执行 vs 决策视角

这篇文章揭示了 AI 编程方法论的一个关键维度差异：**控制粒度**。

Superpowers 和 gstack 的根本差异在于：
- Superpowers 控制的是"任务执行粒度"
- gstack 控制的是"决策视角粒度"

这意味着：
- Superpowers 更像一个"工程操作系统"，管理的是"怎么执行"
- gstack 更像一个"AI 版软件组织架构"，管理的是"谁来判断"

**启示**：设计 AI 工作流时，要明确你是想控制 AI "如何执行任务"，还是想控制 AI "从什么视角做判断"。这两种控制方向是完全不同的。

---

### 3. 自动化程度：隐式接管 vs 显式操盘

文章对比了两种不同的自动化程度：

**Superpowers**：
- 把工程最佳实践尽量内嵌到 agent 行为默认值里
- 你触发一个任务，agent 自动进入更合理的 skill 链条
- 更倾向于"隐式接管"

**gstack**：
- 把工程流程显式展现在你面前
- 你需要有意识地调用某个角色
- 希望你"显式操盘"

**启示**：自动化不是唯一的优化方向。有时候"显式操盘"反而更适合有经验的开发者，因为它让过程更清晰、更可控。

---

### 4. 抽象层级：底层 runtime vs 高层组织

文章用程序设计类比说明了抽象层级的差异：

- Superpowers 更像底层 runtime + workflow engine
- gstack 更像面向对象中的"角色接口"

这意味着：
- Superpowers 的抽象层更"底层"，更靠近工程动作本身
- gstack 的抽象层更"高层"，更偏组织与决策分工

**启示**：AI 工作流设计需要在不同的抽象层级上做权衡。太底层可能太复杂，太高层可能不够精细。

---

### 5. 浏览器能力的重要性

文章特别强调了 gstack 对浏览器能力的重视：
- 采用 long-lived Chromium daemon
- 避免每次工具调用都冷启动浏览器
- 保留 cookies、tabs 和登录状态
- 获得亚秒级延迟和持久状态

这背后的认知是：**浏览器自动化是"硬问题"，其他很多东西只是 Markdown**。

**启示**：对于 Web 应用和 SaaS 产品，浏览器测试能力是 AI 工作流的关键。这不仅仅是"能不能打开页面"的问题，而是"能否保持状态、快速响应"的问题。

---

### 6. 工程纪律的价值

Superpowers 的工程立场非常明确：
- 不相信"先写点代码看看"
- 不鼓励一上来就全局重构
- 希望 agent 像受过训练的工程师一样，先澄清设计、写测试、再推进实现

这意味着 **Superpowers 本质上不是在强化"生成能力"，而是在强化工程纪律**。

**启示**：AI 工作流设计的核心目标之一，应该是把工程师的工程纪律内化到 AI 的行为里，让 AI 自动遵循最佳实践。

---

### 7. 组合使用：不是二选一，而是协同增效

这篇文章给出了一个非常实用的组合方式：

- **gstack 做高层决策**：需求是否值得做、架构是否合理、设计是否过关
- **Superpowers 做中低层执行**：brainstorming、plan、subagent-driven-development、TDD、review、branch finishing
- **gstack 再做验证与交付**：/qa 或 /browse、/ship、/retro

这样你会得到一种非常强的组合：
- gstack 负责"想对"
- Superpowers 负责"做稳"
- gstack 再负责"验真"和"交付"

**启示**：方法论不是二选一，而是要找到最适合自己的组合。不同的方法论可以在不同的层次上协同增效。

---

### 8. 适用场景的选择依据

文章给出了清晰的适用场景选择：

**选 Superpowers，如果你更在意这些**：
- 让 agent 少跳步骤
- 让实现更规整
- 更严格的 TDD/plan/review 纪律
- 更强的 task decomposition
- 多平台可迁移性
- 希望流程尽量自动内化

**选 gstack，如果你更在意这些**：
- 把 AI 当作"虚拟团队"来协作
- 明确切换产品/架构/设计/QA/发布视角
- 强浏览器测试能力
- 更适合 Web 产品和创业团队语境
- 想显式控制每一步流程

**启示**：方法论的选择应该基于你的实际需求和工作场景，而不是追求"最强"或"最新"。

---

### 9. AI 编程的真正差距：不在模型，在工作流

文章标题已经点明：**AI 编程真正的差距，不在模型，在工作流**。

这意味着：
- 模型会不断进步，但工作流设计需要人为思考和构建
- 谁先把这个系统搭好，谁就会在下一轮 AI 编程效率竞争里拉开差距

**启示**：不要把所有希望都寄托在"更强的模型"上。投资工作流设计和工程系统，才是更长期、更稳定的竞争力来源。

---

### 10. AI 编程的下一阶段：从"单次回答"到"结构化协作"

文章认为这两个项目真正有价值的地方，不在于"又出现了两个开源工具"，而在于它们代表了一个趋势：**AI 编程正在从"单次回答"演进到"结构化协作"**。

过去我们说 prompt engineering。后来我们说 agent。现在更准确的词是：workflow engineering、agent orchestration、decision scaffolding、AI-native software process。

**启示**：AI 编程的范式正在快速演进。要跟上这个趋势，需要不断学习新的方法论和工作流设计思路。

---

## 附录：核心概念解释

### Superpowers

- **定义**：一套完整的软件开发工作流，建立在一组可组合的 skills 之上，并通过初始指令确保 agent 会去使用这些 skills
- **核心理念**：能力编排系统
- **控制粒度**：任务执行粒度
- **特点**：可组合、可复用、可自动触发
- **技能列表**：brainstorming、using-git-worktrees、writing-plans、subagent-driven-development、test-driven-development、requesting-code-review、finishing-a-development-branch
- **优势**：跨平台支持、流程自动内化、强化工程纪律

---

### gstack

- **定义**：把 Claude Code 变成一个"虚拟工程团队"，其中包括 CEO、工程经理、设计师、Reviewer、QA、Security Officer、Release Engineer 等角色
- **核心理念**：组织流程系统
- **控制粒度**：决策视角粒度
- **特点**：角色明确、流程外显、浏览器能力强
- **运行时架构**：CLI、本地 server、持久化 headless Chromium、会话状态管理
- **主要命令**：/office-hours、/plan-ceo-review、/plan-eng-review、/plan-design-review、/review、/qa、/ship、/browse、/retro 等
- **优势**：明确角色视角、真实浏览器测试、适合 Web 产品和创业团队
