import { defineConfig } from 'astro/config'
import mdx from '@astrojs/mdx'
import expressiveCode from 'astro-expressive-code'
import remarkDirective from 'remark-directive'
import { remarkMermaid } from './src/utils/mermaid'
import rehypeAutolinkHeadings from 'rehype-autolink-headings'
import rehypeSlug from 'rehype-slug'

// https://astro.build/config
export default defineConfig({
  site: 'https://banzheshenghuo.github.io',
  base: '/document-site',
  integrations: [
    expressiveCode({
      themes: ['dark-plus', 'light-plus'],
      styleOverrides: {
        borderRadius: '0.5rem',
        frames: {
          shadowColor: 'rgba(0, 0, 0, 0.3)',
          editorBackground: 'var(--color-code-bg)'
        }
      },
      // 启用代码块功能
      features: {
        // 复制按钮
        copyButton: {
          visible: true,
          feedbackDuration: 3000,
          symbol: '⧉'
        }
      },
      // 自定义样式
      customStyleOverrides: {
        'code-block': {
          'font-family': "'JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', monospace"
        },
        'code-block-header': {
          'background': 'var(--color-bg-secondary)'
        }
      }
    }),
    mdx()
  ],
  output: 'static',
  markdown: {
    remarkPlugins: [remarkMermaid, remarkDirective],
    rehypePlugins: [
      rehypeSlug,
      [rehypeAutolinkHeadings, {
        behavior: 'wrap',
        properties: {
          className: ['heading-link']
        }
      }]
    ]
  }
})
