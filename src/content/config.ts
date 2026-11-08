import { defineCollection, z } from 'astro:content'
import { CATEGORIES, ARTICLE_TYPES } from '../site'

const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    date: z.any().optional(),
    tags: z.array(z.string()).optional(),
    category: z.enum(CATEGORIES).optional(),
    type: z.enum(ARTICLE_TYPES).optional(),
    // 原文在 ima 知识库的归档链接（管线入库时自动写入，供详情页跳转）
    ima_url: z.string().optional(),
    // ima 媒体 ID（签名 URL 过期后可凭此重建链接）
    ima_media_id: z.string().optional(),
  }),
})

export const collections = { posts: blog }
