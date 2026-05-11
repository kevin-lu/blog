import { asc, eq, sql } from 'drizzle-orm';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { articleCategories, categories } from '~/server/database/schema/categories';

export async function getCategoryList(options: { publishedOnly?: boolean } = {}) {
  const articleCount = options.publishedOnly
    ? sql<number>`COALESCE(COUNT(DISTINCT CASE WHEN ${articleMeta.status} = 'published' THEN ${articleCategories.articleId} END), 0)`.as('article_count')
    : sql<number>`COALESCE(COUNT(DISTINCT ${articleCategories.articleId}), 0)`.as('article_count');

  return await db
    .select({
      id: categories.id,
      name: categories.name,
      slug: categories.slug,
      description: categories.description,
      parentId: categories.parentId,
      parent_id: categories.parentId,
      sortOrder: categories.sortOrder,
      sort_order: categories.sortOrder,
      createdAt: categories.createdAt,
      created_at: categories.createdAt,
      updatedAt: categories.updatedAt,
      updated_at: categories.updatedAt,
      article_count: articleCount,
    })
    .from(categories)
    .leftJoin(articleCategories, eq(categories.id, articleCategories.categoryId))
    .leftJoin(articleMeta, eq(articleCategories.articleId, articleMeta.id))
    .groupBy(categories.id)
    .orderBy(asc(categories.sortOrder), asc(categories.name));
}
