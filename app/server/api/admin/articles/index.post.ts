import { defineEventHandler, readBody, createError } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { z } from 'zod';

const createArticleSchema = z.object({
  slug: z.string().min(1, 'slug 不能为空').max(200),
  title: z.string().min(1, '标题不能为空').max(200),
  description: z.string().optional(),
  content: z.string().optional(),
  cover_image: z.string().optional().or(z.literal('')),
  status: z.enum(['draft', 'published']).default('draft'),
  published_at: z.string().optional(),
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

    const { slug, title, description, content, cover_image, status, published_at } = result.data;

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
    const [newArticle] = await db.insert(articleMeta).values({
      slug,
      title,
      description,
      content,
      cover_image: cover_image || null,
      status,
      publishedAt: status === 'published' ? now : (published_at ? new Date(published_at) : null),
    }).returning();

    return {
      success: true,
      data: newArticle,
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
