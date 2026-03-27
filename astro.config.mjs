import { defineConfig } from 'astro/config'
import mdx from '@astrojs/mdx'
import expressiveCode from 'astro-expressive-code'
import remarkDirective from 'remark-directive'
import { rehypeMermaid } from './src/utils/rehype-mermaid'
import rehypeAutolinkHeadings from 'rehype-autolink-headings'
import rehypeSlug from 'rehype-slug'
import { ExpressiveCodeBlock } from 'expressive-code'

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
      // 跳过 mermaid 代码块
      customCreateBlock: ({ input }) => {
        // 如果是 mermaid 代码块，返回 null 让后续插件处理
        if (input.lang === 'mermaid') {
          return null
        }
        return new ExpressiveCodeBlock(input)
      },
      features: {
        copyButton: {
          visible: true,
          feedbackDuration: 3000,
          symbol: '⧉'
        }
      },
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
    remarkPlugins: [remarkDirective],
    rehypePlugins: [
      rehypeSlug,
      [rehypeAutolinkHeadings, {
        behavior: 'wrap',
        properties: {
          className: ['heading-link']
        }
      }],
      rehypeMermaid
    ]
  }
})
