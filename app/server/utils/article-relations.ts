import { eq } from 'drizzle-orm';
import { db } from '~/server/database/postgres';
import {
  articleCategories,
  articleTags,
  categories,
  tags,
} from '~/server/database/schema/categories';

export async function syncArticleRelations(articleId: number, relations: {
  categoryIds?: number[];
  tagIds?: number[];
}) {
  if (relations.categoryIds) {
    await db.delete(articleCategories).where(eq(articleCategories.articleId, articleId));
    const categoryValues = uniqueIds(relations.categoryIds).map(categoryId => ({
      articleId,
      categoryId,
    }));
    if (categoryValues.length) {
      await db.insert(articleCategories).values(categoryValues);
    }
  }

  if (relations.tagIds) {
    await db.delete(articleTags).where(eq(articleTags.articleId, articleId));
    const tagValues = uniqueIds(relations.tagIds).map(tagId => ({
      articleId,
      tagId,
    }));
    if (tagValues.length) {
      await db.insert(articleTags).values(tagValues);
    }
  }
}

export async function getArticleRelations(articleId: number) {
  const categoryList = await db
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
    })
    .from(articleCategories)
    .innerJoin(categories, eq(articleCategories.categoryId, categories.id))
    .where(eq(articleCategories.articleId, articleId));

  const tagList = await db
    .select({
      id: tags.id,
      name: tags.name,
      slug: tags.slug,
      createdAt: tags.createdAt,
      created_at: tags.createdAt,
      updatedAt: tags.updatedAt,
      updated_at: tags.updatedAt,
    })
    .from(articleTags)
    .innerJoin(tags, eq(articleTags.tagId, tags.id))
    .where(eq(articleTags.articleId, articleId));

  return {
    categories: categoryList,
    tags: tagList,
  };
}

export async function serializeArticleWithRelations(article: any) {
  const relations = await getArticleRelations(article.id);
  return {
    ...article,
    ...relations,
  };
}

function uniqueIds(ids: number[]) {
  return [...new Set(ids.filter(id => Number.isInteger(id) && id > 0))];
}
