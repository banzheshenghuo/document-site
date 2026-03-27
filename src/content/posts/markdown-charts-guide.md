---
title: 'Markdown 图表完全指南'
description: '展示所有支持的图表类型，包括 Mermaid 流程图、序列图、类图、ER图、思维导图等'
date: '2026-03-27'
tags: ['Mermaid', '图表', '文档', '指南']
category: '文档'
---

# Markdown 图表完全指南

本文档展示了所有支持的图表类型和功能。

---

## 一、Mermaid 图表

### 1.1 流程图 (Flowchart)

基础流程图：

```mermaid
graph LR
    A[开始] --> B{判断条件}
    B -->|是| C[执行操作A]
    B -->|否| D[执行操作B]
    C --> E[结束]
    D --> E
```

复杂流程图：

```mermaid
graph TD
    A[用户访问] --> B{已登录?}
    B -->|是| C[显示首页]
    B -->|否| D[跳转登录页]
    D --> E[登录成功]
    E --> C
    C --> F[浏览内容]
    F --> G{购买商品?}
    G -->|是| H[加入购物车]
    G -->|否| F
    H --> I[结算]
```

### 1.2 序列图 (Sequence Diagram)

```mermaid
sequenceDiagram
    participant 用户
    participant 浏览器
    participant 服务器
    participant 数据库

    用户->>浏览器: 输入网址
    浏览器->>服务器: 发送HTTP请求
    服务器->>数据库: 查询数据
    数据库-->>服务器: 返回结果
    服务器-->>浏览器: 返回HTML
    浏览器-->>用户: 显示页面
```

### 1.3 类图 (Class Diagram)

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +eat()
        +sleep()
    }
    class Dog {
        +String breed
        +bark()
        +fetch()
    }
    class Cat {
        +Boolean indoor
        +meow()
        +scratch()
    }
    Animal <|-- Dog
    Animal <|-- Cat
```

### 1.4 ER图 (Entity Relationship)

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string name
        string email
        string password
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int id PK
        int userId FK
        datetime created_at
        string status
    }
    ORDER_ITEM {
        int id PK
        int orderId FK
        int productId FK
        int quantity
    }
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
    PRODUCT {
        int id PK
        string name
        decimal price
        int stock
    }
}
```

### 1.5 状态图 (State Diagram)

```mermaid
stateDiagram-v2
    [*] --> 待处理
    待处理 --> 处理中: 分配处理人
    待处理 --> 已取消: 用户取消
    处理中 --> 已完成: 处理完成
    处理中 --> 已拒绝: 拒绝请求
    已完成 --> [*]
    已取消 --> [*]
    已拒绝 --> [*]
```

### 1.6 思维导图 (Mindmap)

```mermaid
mindmap
  root((AI技术))
    大语言模型
      GPT系列
      Claude系列
      Gemini
      文心一言
    Agent架构
      Single Agent
      Multi-Agent
      Agent Skills
      Agent Teams
    应用领域
      代码生成
      文档处理
      数据分析
      客服机器人
```

### 1.7 甘特图 (Gantt Chart)

```mermaid
gantt
    title 项目开发计划
    dateFormat  YYYY-MM-DD
    section 需求分析
    需求收集      :a1, 2026-03-01, 5d
    需求评审      :a2, after a1, 2d
    section 设计阶段
    系统设计      :b1, after a2, 5d
    UI设计        :b2, after a2, 7d
    section 开发阶段
    后端开发      :c1, after b1, 10d
    前端开发      :c2, after b2, 10d
    section 测试上线
    集成测试      :d1, after c1, 5d
    上线部署      :d2, after d1, 2d
```

### 1.8 时间线 (Timeline)

```mermaid
timeline
    title AI 发展历程
    2022 : ChatGPT 发布
    2023 : GPT-4 发布
         : Claude 2 发布
    2024 : GPT-4o 发布
         : Claude 3.5 Sonnet 发布
         : Gemini 发布
    2025 : Agent 技术爆发
         : 多模态 AI 普及
```

### 1.9 饼图 (Pie Chart)

```mermaid
pie title 技术栈分布
    "JavaScript" : 45
    "Python" : 25
    "Java" : 15
    "Go" : 10
    "其他" : 5
```

### 1.10 关系图 (Relationship Diagram)

```mermaid
graph TD
    A[AI应用层] --> B[大语言模型]
    A --> C[Agent框架]
    C --> D[Single Agent]
    C --> E[Multi-Agent]
    C --> F[Agent Skills]
    C --> G[Agent Teams]

    B --> H[GPT系列]
    B --> I[Claude系列]
    B --> J[Gemini系列]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
```

---

## 二、Markdown 基础语法

### 2.1 表格

| 功能 | 插件 | 状态 |
|------|------|------|
| 代码高亮 | Expressive Code | ✅ 已启用 |
| 流程图 | Mermaid | ✅ 已启用 |
| 数学公式 | - | ⚠️ 待添加 |
| 标题锚点 | rehype-autolink-headings | ✅ 已启用 |

### 2.2 引用块

> 这是一个普通的引用块。

::: info
这是一个信息提示框，用于展示提示信息。
:::

::: warning
这是一个警告提示框，用于展示需要注意的事项。
:::

::: success
这是一个成功提示框，用于展示成功信息。
:::

### 2.3 代码块

```javascript
// 代码块支持语法高亮
function greet(name) {
  return `Hello, ${name}!`;
}

console.log(greet('World'));
```

### 2.4 列表

无序列表：
- 第一项
- 第二项
  - 子项 A
  - 子项 B
- 第三项

有序列表：
1. 第一步
2. 第二步
3. 第三步

---

## 三、使用技巧

### 3.1 标题锚点

将鼠标悬停在标题上，左侧会显示 `#` 符号，点击即可复制该章节的链接。

### 3.2 代码复制

所有代码块右上角都有复制按钮，点击即可复制代码内容。

### 3.3 深色模式

所有图表都支持深色模式自动切换。
