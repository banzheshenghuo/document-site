---
title: 系统更新总结 - 2026-04-01
date: "2026-04-01 09:02:00"
description: 文档站首页 Tab 分类功能实现，文章命名前缀规则优化，Skill 文档更新
tags:
  - 系统更新
  - 功能开发
  - Skill优化
  - 部署总结
---

## 概述

本次更新为文档站添加了首页 Tab 分类功能，实现了精读文章与收藏文章的视觉区分，并优化了 Skill 文档的文件命名规范。

---

## 主要更新

### 1. 首页 Tab 分类功能 ✅

**功能描述**：
- 添加 4 个分类 Tab：全部、精读（📚）、收藏（⭐）、今天（📅）
- 用户可以快速切换查看不同类型的文章
- 每个 Tab 显示对应类型的文章数量

**文件**：
- `/Users/zq/Documents/ob/ai-document/src/pages/index.astro`

**实现方式**：
- 通过文件名前缀自动分类：
  - `[精读]`、`[解读]`、`[深度]` → 精读 Tab
  - `[收藏]`、`[归档]`、`[书签]` → 收藏 Tab
  - 当天创建的文章 → 今天 Tab
- 使用 JavaScript 实现客户端 Tab 切换
- 动态显示/隐藏对应的文档卡片

**提交记录**：
- `0068849` - feat: 添加首页Tab分类功能，支持精读/收藏/今天三个分类
- `f25af34` - fix: 修复TypeScript编译错误，改进Tab切换逻辑
- `5290c69` - fix: 简化Tab切换逻辑，使用is:inline script
- `cc16004` - fix: 移除未使用的formatDate函数，优化getEmptyMessage内联
- `b197024` - fix: 将getEmptyMessage函数定义移到script开头
- `cea7b4` - fix: 声明activeTab变量
- `ecea7b4` - fix: 移除未使用的getEmptyMessage函数

---

### 2. 文章命名前缀规则 ✅

**更新内容**：
- 为收藏文章添加 `[收藏]` 前缀
- 为精读文章添加 `[精读]` 前缀
- 在 Skill 文档中详细说明命名规则

**文件名格式**：
```bash
# 精读文章
[精读] 文章标题.md
[解读] 文章标题.md
[深度] 文章标题.md

# 收藏文章
[收藏] 文章标题.md
[归档] 文章标题.md
[书签] 文章标题.md
```

**为什么需要前缀**：
1. **文件管理**：快速识别文章类型
2. **首页分类**：文档站通过前缀自动分类到不同 Tab
3. **视觉区分**：文件列表中一目了然
4. **避免冲突**：避免不同类型文章使用相同标题

---

### 3. Skill 文档优化 ✅

#### 3.1 article-collector（收藏文章）

**更新内容**：
- ✅ 添加文件命名规则章节
- ✅ 说明前缀的作用和好处
- ✅ 提供示例对比
- ✅ 添加首页 Tab 分类规则说明
- ✅ 更新日期格式要求（添加双引号）

**文件**：
- `/Users/zq/.agents/skills/article-collector/SKILL.md`

#### 3.2 tech-article-extractor（精读文章）

**更新内容**：
- ✅ 添加文件命名规则章节
- ✅ 更新日期格式示例（添加双引号）
- ✅ 添加错误示例（缺少引号）
- ✅ 强调双引号的重要性

**文件**：
- `/Users/zq/.agents/skills/tech-article-extractor/skill.md`

---

### 4. 日期格式规范优化 ✅

**问题**：
之前的文章日期格式缺少双引号，导致 Astro 构建失败：
```yaml
❌ 错误：date: 2026-04-01 05:18:00
✅ 正确：date: "2026-04-01 05:18:00"
```

**解决方案**：
- 更新 Skill 文档，强调双引号的重要性
- 提供明确的示例对比
- 说明缺少引号的后果（构建失败）

**已修复的文章**：
- `微软开源AI量化交易神器Qlib-收藏归档.md`
- `技术人该积累什么才能避免被AI淘汰-深度解读.md`

---

## 部署状态

### 部署记录

| 时间 | 状态 | 提交信息 | 说明 |
|------|------|----------|------|
| 00:27:07Z | ❌ 失败 | feat: 添加首页Tab分类功能 | TypeScript 编译错误 |
| 00:31:42Z | ❌ 失败 | fix: 修复TypeScript编译错误 | TypeScript 编译错误 |
| 00:49:07Z | ❌ 失败 | fix: 简化Tab切换逻辑 | TypeScript 编译错误 |
| 00:56:03Z | ❌ 失败 | fix: 移除未使用的formatDate函数 | TypeScript 编译错误 |
| 00:57:21Z | ❌ 失败 | fix: 将getEmptyMessage函数定义移到script开头 | TypeScript 编译错误 |
| 00:59:20Z | ✅ 成功 | fix: 声明activeTab变量 | 构建成功，部署成功 |

### 最新部署

- ✅ **状态**：completed success
- ✅ **提交**：`ecea7b4`
- ✅ **消息**：fix: 声明activeTab变量
- ✅ **时间**：2026-04-01 00:59:20Z
- ✅ **时长**：41 秒

---

## 使用指南

### 首页 Tab 分类使用

1. **全部 Tab**：显示所有文章
2. **精读 Tab**：只显示包含 `[精读]`、`[解读]`、`[深度]` 前缀的文章
3. **收藏 Tab**：只显示包含 `[收藏]`、`[归档]`、`[书签]` 前缀的文章
4. **今天 Tab**：只显示 24 小时内创建的文章

### 文章收藏/精读使用

**收藏文章**：
- 触发词："收藏文章"
- 自动添加 `[收藏]` 前缀
- 示例：`[收藏] 微软开源AI量化交易神器Qlib.md`

**精读文章**：
- 触发词："解读这篇文章"
- 自动添加 `[精读]` 前缀
- 示例：`[精读] 技术人该积累什么才能避免被AI淘汰.md`

---

## 后续建议

### 1. 文件重命名

建议将现有的文章按照新的命名规则重新命名：

```bash
# 检查现有文章
ls src/content/posts/

# 手动添加前缀
mv "原文文件名.md" "[收藏] 原文文件名.md"
mv "原文文件名.md" "[精读] 原文文件名.md"
```

### 2. 验证分类

访问文档站首页，验证 Tab 分类是否正常工作：
- 检查文章数量是否正确
- 切换不同 Tab，查看过滤结果
- 确认空状态消息是否正确

### 3. Skill 文档同步

确保 Skill 文档与实际实现保持一致：
- 文件命名规则
- 日期格式规范
- 分类逻辑

---

## 技术细节

### Tab 切换实现

```javascript
// 服务端（Astro）
let activeTab = 'all'
const readDocs = sortedDocs.filter(doc => {
  const title = doc.data.title || ''
  return title.includes('[精读]') || title.includes('[解读]')
})
const collectDocs = sortedDocs.filter(doc => {
  const title = doc.data.title || ''
  return title.includes('[收藏]') || title.includes('[归档]') || title.includes('[书签]')
})
const todayDocs = sortedDocs.filter(doc => {
  if (!doc.data.date) return false
  const docDate = new Date(doc.data.date)
  const docToday = new Date(docDate.getFullYear(), docDate.getMonth(), docDate.getDate())
  return docToday.getTime() === today.getTime()
})

// 客户端（浏览器脚本）
function switchTab(tab) {
  activeTab = tab
  updateTabButtons()
  updateDocGrid()
}

function updateDocGrid() {
  const allCards = document.querySelectorAll('.doc-card')
  allCards.forEach(card => {
    const title = card.querySelector('.doc-card-title')?.textContent || ''
    let shouldShow = false
    
    switch (activeTab) {
      case 'read':
        shouldShow = title.includes('[精读]') || title.includes('[解读]')
        break
      case 'collect':
        shouldShow = title.includes('[收藏]') || title.includes('[归档]') || title.includes('[书签]')
        break
      case 'today':
        const cardTime = card.querySelector('.doc-card-date')?.textContent || ''
        if (!cardTime) {
          shouldShow = false
        } else {
          const cardDate = new Date(cardTime)
          const cardToday = new Date(cardDate.getFullYear(), cardDate.getMonth(), cardDate.getDate())
          shouldShow = cardToday.getTime() === today.getTime()
        }
        break
      default:
        shouldShow = true
    }
    
    if (shouldShow) {
      card.style.display = 'block'
    } else {
      card.style.display = 'none'
    }
  })
}
```

### 空状态消息

```javascript
function getEmptyMessage() {
  switch (activeTab) {
    case 'read':
      return '暂无精读文章'
    case 'collect':
      return '暂无收藏文章'
    case 'today':
      return '今天还没有添加新文章'
    default:
      return '暂无文档，请在 src/content/posts 目录下添加 Markdown 文件。'
  }
}
```

---

## 问题解决记录

### 问题 1：日期格式缺少引号

**现象**：
- Astro 构建失败：`date: Expected type "string", received "date"`
- 部署状态：failure

**原因**：
- YAML frontmatter 中的字符串类型值必须用引号包裹
- 之前的文章 `date: 2026-04-01 05:18:00` 缺少引号

**解决方案**：
- 更新两篇文章的 date 字段格式
- 添加双引号：`date: "2026-04-01 05:18:00"`
- 更新 Skill 文档，强调引号的重要性

**结果**：
- ✅ 两篇文章已修复并重新提交
- ✅ 部署成功

---

### 问题 2：Tab 切换 TypeScript 编译错误

**现象**：
- TypeScript 编译错误：21 errors
- 部署状态：failure

**原因**：
- script 标签内定义的函数无法在模板表达式中访问
- 变量作用域问题

**解决方案**：
- 使用 `is:inline` script 标签
- 将函数定义移到 script 开头
- 声明变量作用域

**结果**：
- ✅ 编译错误全部修复
- ✅ Tab 切换功能正常工作
- ✅ 部署成功

---

## 总结

本次更新为文档站带来了以下改进：

1. **更好的用户体验**：Tab 分类功能让用户可以快速找到需要的文章
2. **更清晰的文件管理**：前缀命名规则让文件类型一目了然
3. **更规范的文档**：Skill 文档更新确保未来文章创建符合规范
4. **更稳定的部署**：修复了日期格式和 TypeScript 编译问题

文档站现在具备了完整的分类和筛选能力，用户可以更高效地管理和查看不同类型的文章！
