# AI 文档网站

基于 Astro 构建的轻量级文档网站，支持 Markdown、Mermaid 图表、代码高亮、深色模式和搜索功能。

## 功能特性

- ✨ **Markdown 支持**：完整的 Markdown 语法支持
- 🎨 **代码高亮**：基于 Expressive Code 的优美代码块
- 🌙 **深色模式**：支持深色/浅色主题切换
- 🔍 **搜索功能**：客户端全文搜索
- 📊 **Mermaid 图表**：支持流程图、序列图、类图等
- 📱 **响应式设计**：完美适配各种设备
- ⚡ **快速构建**：Astro 静态生成，性能优异

## 本地开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 添加文档

在 `src/content/posts` 目录下创建新的 Markdown 文件：

```markdown
---
title: '文档标题'
description: '文档描述'
date: '2026-03-27'
tags: ['标签1', '标签2']
---

# 文档内容

在这里编写你的 Markdown 内容...
```

### Mermaid 图表

支持多种 Mermaid 图表类型：

\`\`\`mermaid
graph TD
    A[开始] --> B[结束]
\`\`\`

## 部署到 GitHub Pages

1. 将代码推送到 GitHub 仓库
2. 在仓库设置中启用 GitHub Pages
3. 配置 GitHub Actions 工作流（已包含在 `.github/workflows/deploy.yml`）
4. 确保 `astro.config.mjs` 中的 `site` 和 `base` 配置正确

```js
export default defineConfig({
  site: 'https://yourusername.github.io',  // 修改为你的 GitHub Pages 域名
  base: '/ai-document',  // 修改为你的仓库名
  // ...
})
```

## 目录结构

```
.
├── public/           # 静态资源
├── src/
│   ├── components/   # Astro 组件
│   ├── content/      # Markdown 文档内容
│   │   └── posts/    # 博客文章/文档
│   ├── layouts/      # 页面布局
│   ├── pages/        # 页面路由
│   ├── styles/       # 全局样式
│   └── utils/        # 工具函数
├── astro.config.mjs  # Astro 配置
└── package.json
```

## 快捷键

- `⌘K` / `Ctrl+K` - 打开搜索框
- `Esc` - 关闭搜索框

## 技术栈

- [Astro](https://astro.build) - 静态站点生成器
- [Expressive Code](https://expressive-code.com) - 代码高亮
- [Mermaid](https://mermaid.js.org) - 图表渲染
- [TypeScript](https://www.typescriptlang.org) - 类型安全

## 许可证

MIT
