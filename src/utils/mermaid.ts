import type { Root } from 'mdast'
import { visit } from 'unist-util-visit'
import { h } from 'hastscript'

export function remarkMermaid() {
  return (tree: Root) => {
    // 处理容器指令格式 :::mermaid
    visit(tree, 'containerDirective', (node) => {
      if (node.name !== 'mermaid') return

      const data = node.data || (node.data = {})
      const tagName = 'pre'

      data.hName = tagName
      data.hProperties = h(tagName, {
        class: ['mermaid'],
        'data-mermaid': JSON.stringify(node.children)
      }).properties
    })

    // 处理标准代码块格式 ```mermaid
    visit(tree, 'code', (node) => {
      if (node.lang !== 'mermaid') return

      const data = node.data || (node.data = {})
      const value = node.value || ''

      data.hName = 'pre'
      data.hChildren = [h('code', { class: 'mermaid' }, value)]
    })
  }
}
