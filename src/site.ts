export const SITE = {
  title: '安昙',
  description: '由 AI 生成的技术文档集合',
  defaultLang: 'zh-CN'
}

// 全站文章分类枚举（唯一来源，修改需同步 DESIGN.md）
export const CATEGORIES = [
  'AI与Agent',
  '技术',
  '金融',
  '认知迭代',
  '职业发展',
  '其他',
] as const

export type Category = (typeof CATEGORIES)[number]

// 文章类型（与主题分类正交：read=精读解读，daily-finance=每日金融日报）。
// 原文全文（逐字稿/收藏）不上站，统一归档到 ima 知识库。
export const ARTICLE_TYPES = ['read', 'daily-finance'] as const

export type ArticleType = (typeof ARTICLE_TYPES)[number]

export const HOME = {
  intro: '欢迎来到安昙的知识库',
  subtitle: '探索、学习、分享技术知识',
  searchPlaceholder: '搜索文档...'
}
