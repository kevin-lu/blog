import { sqliteTable, integer, text } from 'drizzle-orm/sqlite-core';

export const comments = sqliteTable('comments', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  articleSlug: text('article_slug').notNull(),
  githubId: text('github_id'),
  status: text('status').default('pending'),
  isPinned: integer('is_pinned').default(0),
  createdAt: text('created_at').$type<Date>(),
  updatedAt: text('updated_at').$type<Date>(),
});

export type Comment = typeof comments.$inferSelect;
export type NewComment = typeof comments.$inferInsert;
