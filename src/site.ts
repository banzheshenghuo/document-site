export const SITE = {
  title: '安昙',
  description: '精读解读 · 金融日报 · 开源库解读——AI 时代的信息站',
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

// 文章类型（与主题分类正交）。信息站三类信息流：
// read=精读解读，daily-finance=每日金融日报，oss-review=开源库解读。
// 原文全文（逐字稿/收藏）不上站，统一归档到 ima 知识库。
export const ARTICLE_TYPES = ['read', 'daily-finance', 'oss-review'] as const

export type ArticleType = (typeof ARTICLE_TYPES)[number]

// 类型中文标签唯一来源（Header 切换器、卡片 chip、空状态文案共用）
export const ARTICLE_TYPE_LABELS: Record<ArticleType, string> = {
  read: '精读',
  'daily-finance': '金融日报',
  'oss-review': '开源解读',
}

export const HOME = {
  intro: '欢迎来到安昙的信息站',
  subtitle: '精读解读 · 金融日报 · 开源库解读',
  searchPlaceholder: '搜索信息...'
}
