import { defineEventHandler, readBody, createError } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { z } from 'zod';
import { serializeArticle } from '~/server/utils/article-serializer';
import { getArticleRelations, syncArticleRelations } from '~/server/utils/article-relations';

const optionalDateSchema = z.union([z.string(), z.number(), z.null()]).optional();
const idListSchema = z.array(z.coerce.number().int().positive()).optional();

const createArticleSchema = z.object({
  slug: z.string().min(1, 'slug 不能为空').max(200),
  title: z.string().min(1, '标题不能为空').max(200),
  description: z.string().nullable().optional(),
  content: z.string().nullable().optional(),
  cover_image: z.string().nullable().optional(),
  status: z.enum(['draft', 'published', 'archived']).default('draft'),
  published_at: optionalDateSchema,
  categoryIds: idListSchema,
  tagIds: idListSchema,
});

export default defineEventHandler(async (event) => {
  try {
    if (event.node.req.method !== 'POST') {
      throw createError({
        statusCode: 405,
        message: 'Method not allowed',
      });
    }

    const body = await readBody(event);
    const result = createArticleSchema.safeParse(body);

    if (!result.success) {
      throw createError({
        statusCode: 400,
        message: '请求参数错误',
        data: result.error.flatten(),
      });
    }

    const { slug, title, description, content, cover_image, status, published_at, categoryIds, tagIds } = result.data;

    // 检查 slug 是否已存在
    const existing = await db.query.articleMeta.findFirst({
      where: eq(articleMeta.slug, slug),
    });

    if (existing) {
      throw createError({
        statusCode: 400,
        message: 'slug 已存在',
      });
    }

    const now = new Date();
    const publishedAt = status === 'published'
      ? parseOptionalDate(published_at) || now
      : parseOptionalDate(published_at);

    const [newArticle] = await db.insert(articleMeta).values({
      slug,
      title,
      description,
      content,
      coverImage: cover_image || null,
      status,
      publishedAt,
      createdAt: now,
      updatedAt: now,
    }).returning();

    await syncArticleRelations(newArticle.id, { categoryIds, tagIds });
    const relations = await getArticleRelations(newArticle.id);

    return {
      success: true,
      data: serializeArticle({
        ...newArticle,
        ...relations,
      }),
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('创建文章失败:', error);
    return {
      success: false,
      message: '创建文章失败',
    };
  }
});

// 需要导入 eq
import { eq } from 'drizzle-orm';

function parseOptionalDate(value: string | number | null | undefined): Date | null {
  if (!value) return null;

  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}
