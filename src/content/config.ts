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
  }),
})

export const collections = { posts: blog }
