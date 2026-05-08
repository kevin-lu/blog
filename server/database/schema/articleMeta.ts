import { sqliteTable, integer, text } from 'drizzle-orm/sqlite-core';

export const articleMeta = sqliteTable('article_meta', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  slug: text('slug').notNull().unique(),
  title: text('title').notNull(),
  description: text('description'),
  coverImage: text('cover_image'),
  status: text('status').default('draft'),
  publishedAt: text('published_at').$type<Date>(),
  createdAt: text('created_at').$type<Date>(),
  updatedAt: text('updated_at').$type<Date>(),
});

export type ArticleMeta = typeof articleMeta.$inferSelect;
export type NewArticleMeta = typeof articleMeta.$inferInsert;
