import { defineEventHandler } from 'h3';
import { db } from '~/server/database/postgres';
import { categories, articleCategories } from '~/server/database/schema/categories';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { asc, eq, sql, and } from 'drizzle-orm';

export default defineEventHandler(async () => {
  try {
    const categoryList = await db
      .select({
        id: categories.id,
        name: categories.name,
        slug: categories.slug,
        description: categories.description,
        parentId: categories.parentId,
        sortOrder: categories.sortOrder,
        createdAt: categories.createdAt,
        updatedAt: categories.updatedAt,
        article_count: sql<number>`COALESCE(COUNT(DISTINCT CASE WHEN ${articleMeta.status} = 'published' THEN ${articleCategories.articleId} END), 0)`.as('article_count'),
      })
      .from(categories)
      .leftJoin(articleCategories, eq(categories.id, articleCategories.categoryId))
      .leftJoin(articleMeta, eq(articleCategories.articleId, articleMeta.id))
      .groupBy(categories.id)
      .orderBy(asc(categories.sortOrder), asc(categories.name));

    return {
      success: true,
      data: categoryList,
    };
  } catch (error: any) {
    console.error('获取分类列表失败:', error);
    return {
      success: false,
      message: '获取分类列表失败',
    };
  }
});
