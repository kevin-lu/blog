import { sqliteTable, integer, text } from 'drizzle-orm/sqlite-core';

export const categories = sqliteTable('categories', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  name: text('name').notNull().unique(),
  slug: text('slug').notNull().unique(),
  description: text('description'),
  parentId: integer('parent_id'),
  sortOrder: integer('sort_order').default(0),
  createdAt: text('created_at').$type<Date>(),
  updatedAt: text('updated_at').$type<Date>(),
});

export const tags = sqliteTable('tags', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  name: text('name').notNull().unique(),
  slug: text('slug').notNull().unique(),
  createdAt: text('created_at').$type<Date>(),
  updatedAt: text('updated_at').$type<Date>(),
});

// 文章和分类的多对多关系
export const articleCategories = sqliteTable('article_categories', {
  articleId: integer('article_id').notNull(),
  categoryId: integer('category_id').notNull(),
});

// 文章和标签的多对多关系
export const articleTags = sqliteTable('article_tags', {
  articleId: integer('article_id').notNull(),
  tagId: integer('tag_id').notNull(),
});

export type Category = typeof categories.$inferSelect;
export type NewCategory = typeof categories.$inferInsert;
export type Tag = typeof tags.$inferSelect;
export type NewTag = typeof tags.$inferInsert;

// 需要导入 articleMeta
import { articleMeta } from './articleMeta';
