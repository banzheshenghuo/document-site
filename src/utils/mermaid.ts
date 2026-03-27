import type { Root } from 'mdast'
import { visit } from 'unist-util-visit'
import { h } from 'hastscript'

export function remarkMermaid() {
  return (tree: Root) => {
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
  }
}
