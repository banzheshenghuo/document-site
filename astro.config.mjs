import { defineConfig } from 'astro/config'
import mdx from '@astrojs/mdx'
import expressiveCode from 'astro-expressive-code'
import remarkDirective from 'remark-directive'
import { remarkMermaid } from './src/utils/mermaid'

// https://astro.build/config
export default defineConfig({
  site: 'https://yourusername.github.io/ai-document',
  base: '/ai-document',
  integrations: [
    expressiveCode({
      themes: ['dark-plus', 'light-plus'],
      styleOverrides: {
        borderRadius: '0.5rem',
        frames: {
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        }
      }
    }),
    mdx()
  ],
  output: 'static',
  markdown: {
    remarkPlugins: [remarkMermaid, remarkDirective]
  }
})
