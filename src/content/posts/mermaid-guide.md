---
title: 'Mermaid 图表完整指南'
description: '了解如何在文档中使用 Mermaid 创建各种类型的图表，包括流程图、序列图、类图、状态图等。'
date: '2026-03-27'
tags: ['Mermaid', '图表', '教程']
---

## Mermaid 图表指南

Mermaid 是一个基于 JavaScript 的图表绘制工具，可以通过简单的文本语法创建各种类型的图表。

### 支持的图表类型

### 1. 流程图 (Flowchart)

使用 `graph` 或 `flowchart` 关键字，支持 `TD`(自上而下) 和 `LR`(自左向右) 方向。

```mermaid
graph LR
    A[开始] --> B[处理]
    B --> C{判断}
    C -->|是| D[分支 A]
    C -->|否| E[分支 B]
    D --> F[结束]
    E --> F
```

### 2. 序列图 (Sequence Diagram)

展示对象之间的交互顺序。

```mermaid
sequenceDiagram
    actor 用户
    participant 前端
    participant 后端
    participant 数据库

    用户->>前端: 登录请求
    前端->>后端: API 调用
    后端->>数据库: 验证用户
    数据库-->>后端: 返回用户信息
    后端-->>前端: 返回 Token
    前端-->>用户: 登录成功
```

### 3. 类图 (Class Diagram)

用于展示类的结构和关系。

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +eat()
        +sleep()
    }
    class Dog {
        +bark()
        +fetch()
    }
    class Cat {
        +meow()
        +scratch()
    }
    Animal <|-- Dog
    Animal <|-- Cat
```

### 4. 状态图 (State Diagram)

展示对象的状态转换。

```mermaid
stateDiagram-v2
    [*] --> 待处理
    待处理 --> 处理中: 开始处理
    处理中 --> 已完成: 处理成功
    处理中 --> 失败: 处理失败
    失败 --> 待处理: 重试
    已完成 --> [*]
```

### 5. 实体关系图 (ER Diagram)

用于数据库设计。

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "is in"
    CUSTOMER {
        string name
        string email
        int id PK
    }
    ORDER {
        int id PK
        date created
        int customer_id FK
    }
```

### 6. 甘特图 (Gantt Chart)

用于项目进度管理。

```mermaid
gantt
    title 项目开发计划
    dateFormat YYYY-MM-DD
    section 需求分析
    需求调研           :done,    des1, 2026-03-01, 2026-03-05
    需求文档编写       :done,    des2, 2026-03-06, 3d
    section 设计阶段
    系统设计           :active,  des3, 2026-03-09, 5d
    数据库设计         :         des4, 2026-03-10, 4d
    section 开发阶段
    后端开发           :         des5, 2026-03-15, 10d
    前端开发           :         des6, 2026-03-18, 8d
    section 测试阶段
    集成测试           :         des7, 2026-03-28, 5d
```

### 7. 饼图 (Pie Chart)

展示数据占比。

```mermaid
pie title 技术栈分布
    "JavaScript" : 40
    "Python" : 25
    "Go" : 20
    "Rust" : 10
    "其他" : 5
```

### 8. 思维导图 (Mindmap)

层级结构展示。

```mermaid
mindmap
  root((项目))
    前端
      React
      Vue
      Angular
    后端
      Node.js
      Python
      Go
    数据库
      MySQL
      PostgreSQL
      MongoDB
```

### 样式自定义

你可以在图表中使用类来定义样式：

```mermaid
graph TD
    A[开始]:::start
    B[处理]:::process
    C[结束]:::end

    A --> B
    B --> C

    classDef start fill:#90EE90,stroke:#333,stroke-width:2px
    classDef process fill:#87CEEB,stroke:#333,stroke-width:2px
    classDef end fill:#FFB6C1,stroke:#333,stroke-width:2px
```

### 最佳实践

1. **保持简单**：复杂的图表可以拆分为多个小图
2. **使用描述性文字**：节点和边的标签要清晰易懂
3. **注意方向**：选择合适的图表方向 (TD/LR)
4. **适当使用样式**：用颜色突出重点
5. **测试渲染**：确保图表在主题切换时都能正常显示
