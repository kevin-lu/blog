import { pgTable, serial, varchar, text, timestamp, integer, boolean } from 'drizzle-orm/pg-core';

export const articleMeta = pgTable('article_meta', {
  id: serial('id').primaryKey(),
  slug: varchar('slug', { length: 200 }).unique().notNull(),
  title: varchar('title', { length: 200 }).notNull(),
  description: text('description'),
  coverImage: varchar('cover_image', { length: 255 }),
  status: varchar('status', { length: 20 }).default('draft'),
  publishedAt: timestamp('published_at', { withTimezone: true }),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
});

export type ArticleMeta = typeof articleMeta.$inferSelect;
export type NewArticleMeta = typeof articleMeta.$inferInsert;
