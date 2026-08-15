export const SITE = {
  title: '安昙的知识库',
  description: '由 AI 生成的技术文档集合',
  defaultLang: 'zh-CN'
}

// 全站文章分类枚举（唯一来源，修改需同步 DESIGN.md）
export const CATEGORIES = [
  'AI与Agent',
  '技术',
  '开源库与工具',
  '金融',
  '认知迭代',
  '知识管理',
  '职业发展',
  '心理学',
  '生活',
  '其他',
] as const

export type Category = (typeof CATEGORIES)[number]

// 文章阅读类型（与主题分类正交：read=精读深加工，collect=原文归档）
export const ARTICLE_TYPES = ['read', 'collect'] as const

export type ArticleType = (typeof ARTICLE_TYPES)[number]

export const HOME = {
  intro: '欢迎来到安昙的知识库',
  subtitle: '探索、学习、分享技术知识',
  searchPlaceholder: '搜索文档...'
}
