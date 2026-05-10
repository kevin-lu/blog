import { sqliteTable, integer, text } from 'drizzle-orm/sqlite-core';

export const articleMeta = sqliteTable('article_meta', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  slug: text('slug').notNull().unique(),
  title: text('title').notNull(),
  description: text('description'),
  content: text('content'),
  coverImage: text('cover_image'),
  status: text('status').default('draft'),
  publishedAt: text('published_at').$type<Date>(),
  createdAt: text('created_at').$type<Date>(),
  updatedAt: text('updated_at').$type<Date>(),
  
  // AI 改写相关字段
  sourceUrl: text('source_url'), // 参考文章来源
  aiGenerated: integer('ai_generated').default(0), // 是否 AI 生成 (0/1)
  aiModel: text('ai_model'), // AI 模型名称
  rewriteStrategy: text('rewrite_strategy').default('standard'), // 改写策略
  templateType: text('template_type').default('tutorial'), // 模板类型
  wordCount: integer('word_count'), // 字数统计
  autoPublished: integer('auto_published').default(0), // 是否自动发布
});

export type ArticleMeta = typeof articleMeta.$inferSelect;
export type NewArticleMeta = typeof articleMeta.$inferInsert;
