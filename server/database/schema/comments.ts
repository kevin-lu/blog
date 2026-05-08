import { pgTable, serial, varchar, boolean, timestamp } from 'drizzle-orm/pg-core';

export const comments = pgTable('comments', {
  id: serial('id').primaryKey(),
  articleSlug: varchar('article_slug', { length: 100 }).notNull(),
  githubId: varchar('github_id', { length: 50 }),
  status: varchar('status', { length: 20 }).default('pending'),
  isPinned: boolean('is_pinned').default(false),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
});

export type Comment = typeof comments.$inferSelect;
export type NewComment = typeof comments.$inferInsert;
