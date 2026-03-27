interface DocIndex {
  slug: string
  title: string
  description: string
  content: string
  tags: string[]
  date: string
}

// 构建搜索索引
export function buildSearchIndex(): DocIndex[] {
  // 这个函数将在构建时被调用
  return []
}

// 简单的客户端搜索函数
export function searchDocs(query: string, index: DocIndex[]): DocIndex[] {
  if (!query.trim()) return index

  const terms = query.toLowerCase().split(/\s+/)

  return index
    .map((doc) => {
      let score = 0
      const titleLower = doc.title.toLowerCase()
      const contentLower = doc.content.toLowerCase()
      const tagsLower = doc.tags.map(t => t.toLowerCase())

      for (const term of terms) {
        if (titleLower.includes(term)) score += 10
        if (contentLower.includes(term)) score += 1
        if (tagsLower.some(tag => tag.includes(term))) score += 5
      }

      return { doc, score }
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .map(({ doc }) => doc)
}
