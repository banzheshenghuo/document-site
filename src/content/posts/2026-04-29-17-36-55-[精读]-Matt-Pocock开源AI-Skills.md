---
title: 'TS 大神 Matt Pocock 开源自己的 AI Skills，主打反 Vibe Coding'
date: 2026-04-29T17:36:55+08:00
category: '技术实践'
tags: ['精读', 'AI', 'Agent', 'Claude-Code', 'TDD', 'Vibe-Coding', '工程实践']
description: 'Matt Pocock 开源 AI Skills 仓库，用工程纪律对抗 Vibe Coding，提供可组合的 AI 编程协作方法。'
---

## 📋 文章信息

- **来源**: 微信公众号 - Nodejs技术栈
- **作者**: 五月君
- **发布时间**: 2026年4月29日
- **阅读链接**: https://mp.weixin.qq.com/s/rv1_aVxu1lWxz1T9EnHiCA

---

## 🎯 核心摘要

Matt Pocock（Total TypeScript 作者）开源了 AI Skills 仓库（mattpocock/skills），提供一组可自由组合的 AI 编程协作技能片段。与 BMAD、Spec-Kit 等方法论不同，Skills 不定义流程黑盒，而是把工程师的好习惯拆解为可组合的小片段，适配 Claude Code、Codex 等工具。整套设计围绕 AI 编程的四个失败模式展开：意图偏离、token 浪费、代码质量差、架构腐坏。核心理念是"AI 用来强化工程纪律，而非代替工程纪律"。

## 📊 核心观点

### 1. Skills 是"拆给你拼的积木"，而非"替你跑的流水线"

**背景/现状**：
- BMAD、Spec-Kit、GSD 等框架试图将 AI 编程协作流程化，但它们替开发者拿走了控制权
- 流程一旦出错，难以钻进去调试和修复

**核心论述**：
- Skills 是一组很小、容易修改、自由组合的技能片段
- 不绑定特定模型，Claude Code、Codex 都能用
- 底层逻辑来自几十年工程经验的沉淀，不是 AI 时代的新魔法
- 一句话：BMAD 是"我帮你定义流程"，Skills 是"我把好习惯拆给你，你自己拼"

### 2. 反对 Vibe Coding，用工程纪律驾驭 AI

**背景/现状**：
- Vibe Coding（凭感觉跟 AI 聊一聊生成代码）盛行，爽但难以维护
- AI 写代码快，烂得也快，复杂度增长速度前所未有

**核心论述**：
- AI 不是用来代替工程纪律的，而是用来强化工程纪律的
- 真正的工程需求来自一线开发者：可控、可改、可组合
- 反对任何把流程变黑盒的做法

### 3. 需求偏差是 AI 编程最高频的失败模式

**背景/现状**：
- 用户想的是 A，说出来变成 B，AI 理解成 C，实现出来是 D
- 引用《程序员修炼之道》："没有人确切知道自己想要什么"

**核心论述**：
- 用 Grilling Session（"拷问"模式）让 AI 反过来追问用户
- `/grill-me`：让 agent 像面试官一样轮流追问设计的每个分支
- `/grill-with-docs`：将回答与项目 CONTEXT.md 对照，发现术语冲突
- 本质是将传统的"需求澄清"自动化

### 4. 建立共享语言是解决 token 浪费的根本手段

**背景/现状**：
- 引用《领域驱动设计》：开发和领域专家说的不是同一种语言
- AI 也一样，要花大量 token 推断项目"行话"

**核心论述**：
- 在 CONTEXT.md 中建立领域术语表，将复杂描述压缩为精确定义
- 例："课程章节被赋予文件系统位置时出现的问题" → "materialization cascade"
- 好处：省 token、命名更一致、导航更顺、思考更少
- 架构决策用 ADR 记录，三个标准：不可反悔、后人会疑惑、有过权衡

### 5. TDD 垂直切片是保证 AI 代码质量的正确姿势

**背景/现状**：
- 需求对齐了 AI 还是写崩，问题在反馈回路

**核心论述**：
- 反模式"水平切片"：先写完所有测试再写实现 → 产出垃圾测试
- 正确做法"垂直切片"（追踪弹）：写一个测试 → 最少代码通过 → 下一个测试
- `/diagnose` 调试框架：优先建立稳定的 pass/fail 反馈信号
- 90% 精力花在"怎么稳定复现"，10% 才是修

## 🧠 概念图谱

```mermaid
graph TD
    A[Matt Pocock AI Skills] --> B[核心理念]
    A --> C[四大顽疾]
    A --> D[实用工具]

    B --> B1[可组合的技能片段]
    B --> B2[强化工程纪律]
    B --> B3[不绑定特定模型]

    C --> C1[意图偏离]
    C --> C2[Token 浪费]
    C --> C3[代码质量差]
    C --> C4[架构腐坏]

    C1 --> C1a[Grilling Session]
    C1 --> C1b[/grill-me]
    C1 --> C1c[/grill-with-docs]

    C2 --> C2a[CONTEXT.md 共享语言]
    C2 --> C2b[ADR 架构决策记录]
    C2 --> C2c[领域术语压缩]

    C3 --> C3a[TDD 垂直切片]
    C3 --> C3b[/tdd]
    C3 --> C3c[/diagnose 调试框架]

    C4 --> C4a[/to-prd]
    C4 --> C4b[/zoom-out]
    C4 --> C4c[/improve-codebase-architecture]

    D --> D1[/caveman 穴居人模式]
    D --> D2[/git-guardrails 安全护栏]
    D --> D3[/write-a-skill 自举工具]
    D --> D4[/triage Issue 管理]
```

## 🏗️ 技术架构（技术类文章适用）

### 架构概述

Matt Pocock 的 Skills 不是一个完整框架，而是一组独立的 Skill 文件（SKILL.md），每个文件定义一个可被 AI agent 识别和执行的技能。通过 `/setup-matt-pocock-skills` 初始化器统一配置项目上下文，确保各 Skill 之间的约定一致。

### 核心组件

| 组件 | 职责 | 关键技术 |
|------|------|----------|
| `/setup-matt-pocock-skills` | 初始化器，配置 issue tracker、label、文档目录 | SKILL.md 规范 |
| `/grill-me` | 需求拷问，逐分支追问设计决策 | Prompt Engineering |
| `/grill-with-docs` | 结合 CONTEXT.md 的需求拷问 + 术语沉淀 | 领域驱动设计 |
| CONTEXT.md | 项目共享语言和领域术语表 | DDD 统一语言 |
| docs/adr/ | 架构决策记录 | ADR 规范 |
| `/tdd` | TDD 垂直切片指导 | 测试驱动开发 |
| `/diagnose` | 调试框架，六阶段方法论 | 反馈信号优先级 |
| `/caveman` | 压缩 AI 输出的冗余信息 | Token 优化 |
| `/git-guardrails` | 拦截危险 git 操作 | PreToolUse Hook |

## 🔑 关键洞察

### 1. "可控性"才是 AI 编程工具的核心竞争力

**分析**：
- 当前 AI 编程工具的竞争已从"能做什么"转向"怎么可控地做"
- BMAD 等框架的失败不在于思路错，而在于让开发者交出了控制权
- Skills 的设计哲学更接近 Unix 哲学：小工具、自由组合、人掌控流程
- 这反映了成熟开发者对 AI 的态度演变：从新奇探索到工程化应用

### 2. 共享语言是 AI 协作的"协议层"

**分析**：
- CONTEXT.md + ADR 的组合本质上是给 AI 和人类之间建立了一套协议
- 这不是新发明，而是 DDD 中"统一语言"在 AI 时代的新应用
- 关键洞察：token 效率只是表象，真正的价值是降低沟通歧义
- 当项目有 10+ 个 AI agent 同时工作时，没有统一语言的后果会很严重

### 3. TDD 的价值在 AI 时代被放大了

**分析**：
- 人类写的代码至少经过大脑"编译"一次，AI 写的可能没有
- TDD 的"红绿重构"循环本质上是给代码加了自动化的"编译检查"
- 垂直切片比水平切片重要的原因是：反馈频率决定学习效率
- `/diagnose` 中"反馈信号优先级排序"是对传统调试经验的优秀提炼

## 🚧 不足与局限

### 1. Skill 的发现机制依赖关键词匹配

- `/write-a-skill` 的"描述字段必须包含触发关键词"说明当前 Skill 发现机制比较原始
- 当 Skill 数量增多后，agent 选择加载哪个 Skill 可能不够精确
- 缺少类似依赖管理或冲突检测的机制

### 2. 对个人开发者的价值高于大团队

- Skills 设计更偏向个人或小团队的 AI 协作场景
- 大团队需要更强的规范化约束，Skills 的"自由组合"特性反而可能增加一致性风险
- 缺少团队级别的 Skill 同步和版本管理方案

## 🔮 延伸思考

### 方向1: Skills 生态可能催生"AI 工程师认证"

- 如果 Skills 成为行业标准，可能会出现类似 AWS Certification 的认证体系
- "会写 Skill"可能成为新的工程技能

### 方向2: CONTEXT.md 可能成为项目的"AI README"

- 未来开源项目可能标配 CONTEXT.md 和 ADR 目录
- AI agent clone 仓库后首先读取这些文件来理解项目
- 这会改变项目文档的写法

### 方向3: 反 Vibe Coding vs Vibe Coding 不是非此即彼

- 原型阶段 Vibe Coding 仍然有优势（快速验证想法）
- 关键是知道什么时候从 Vibe 切换到 Engineering 模式
- 理想状态是两种模式无缝切换

## 💡 实践启示

### 1. 立即为你的 AI 项目建立 CONTEXT.md

**要点**：
- 列出项目中所有领域术语及其精确定义
- 每次 agent 产出含糊代码时，反思是否缺少术语定义
- 这是一个持续积累的过程，从第一个项目就开始

### 2. 在 AI 编程工作流中加入"拷问环节"

**要点**：
- 不要急着让 AI 写代码，先让它追问你的设计
- 用 `/grill-me` 的思路，一次问一个问题，走完决策树
- 这比直接扔需求给 AI 的最终产出质量高得多

### 3. 用垂直切片做 TDD

**要点**：
- 坚决避免"先写所有测试再写实现"的水平切片
- 每次只写一个测试，写最少代码让它通过
- 这是保证 AI 生成代码可测试性的最简单方法

### 4. 定期给 AI 项目"清淤"

**要点**：
- 每隔几天跑一次架构审视，AI 写的代码腐坏速度更快
- 用"删除测试"判断模块是否有价值：删掉它，看复杂度去哪了
- 把 ADR 写作标准纳入日常工作流

## 📝 关键金句

> "AI 不是用来代替工程纪律的，而是用来强化工程纪律的。"

> "没有人确切知道自己想要什么。"—— 《程序员修炼之道》，AI 时代的甲方换成了 agent。

> "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:" —— /caveman 穴居人模式的技术信息一字不少，水分全部蒸发。

## 🏷️ 标签

AI、Agent、Claude Code、TDD、Vibe Coding、工程实践、TypeScript、领域驱动设计

---

## 🔗 相关资源

- **GitHub 仓库**: https://github.com/mattpocock/skills
- **拓展阅读**: 《程序员修炼之道》、《领域驱动设计》、《软件设计哲学》
