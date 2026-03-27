import type { Root } from 'hast'
import { visit } from 'unist-util-visit'

/**
 * Rehype 插件：将 mermaid 代码块转换为可渲染的格式
 * 必须在 rehype-expressive-code 之后运行
 */
export function rehypeMermaid() {
  return (tree: Root) => {
    visit(tree, 'element', (node) => {
      // 查找 pre > code 结构
      if (
        node.tagName === 'pre' &&
        node.children.length === 1 &&
        node.children[0].type === 'element' &&
        node.children[0].tagName === 'code'
      ) {
        const codeNode = node.children[0]
        const codeClass = codeNode.properties?.className

        // 确保 className 是数组并检查是否是 mermaid
        const classes = Array.isArray(codeClass) ? codeClass : []
        const isMermaid = classes.some(
          (c: string | number) => typeof c === 'string' && (c === 'language-mermaid' || c === 'mermaid' || c.includes('mermaid'))
        )

        if (isMermaid) {
          // 提取代码内容
          const text = codeNode.children?.[0]?.type === 'text'
            ? codeNode.children[0].value
            : ''

          // 替换为 mermaid 格式
          node.properties = { className: ['mermaid'] }
          node.children = [
            {
              type: 'text',
              value: text
            }
          ]
        }
      }
    })
  }
}
