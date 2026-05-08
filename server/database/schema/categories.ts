import { pgTable, serial, varchar, timestamp, integer } from 'drizzle-orm/pg-core';

export const categories = pgTable('categories', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 50 }).unique().notNull(),
  slug: varchar('slug', { length: 50 }).unique().notNull(),
  description: varchar('description', { length: 255 }),
  parentId: integer('parent_id').references((): any => categories.id),
  sortOrder: integer('sort_order').default(0),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
});

export const tags = pgTable('tags', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 50 }).unique().notNull(),
  slug: varchar('slug', { length: 50 }).unique().notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
});

// 文章和分类的多对多关系
export const articleCategories = pgTable('article_categories', {
  articleId: integer('article_id').notNull().references(() => articleMeta.id, { onDelete: 'cascade' }),
  categoryId: integer('category_id').notNull().references(() => categories.id, { onDelete: 'cascade' }),
});

// 文章和标签的多对多关系
export const articleTags = pgTable('article_tags', {
  articleId: integer('article_id').notNull().references(() => articleMeta.id, { onDelete: 'cascade' }),
  tagId: integer('tag_id').notNull().references(() => tags.id, { onDelete: 'cascade' }),
});

export type Category = typeof categories.$inferSelect;
export type NewCategory = typeof categories.$inferInsert;
export type Tag = typeof tags.$inferSelect;
export type NewTag = typeof tags.$inferInsert;

// 需要导入 articleMeta
import { articleMeta } from './articleMeta';
