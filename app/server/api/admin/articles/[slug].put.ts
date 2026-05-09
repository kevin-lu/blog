import { defineEventHandler, readBody, createError, getRouterParam } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { eq } from 'drizzle-orm';
import { z } from 'zod';

const updateArticleSchema = z.object({
  title: z.string().min(1).max(200).optional(),
  slug: z.string().optional(),
  description: z.string().optional(),
  content: z.string().optional(),
  cover_image: z.string().optional().or(z.literal('')),
  status: z.enum(['draft', 'published']).optional(),
  published_at: z.string().optional(),
});

export default defineEventHandler(async (event) => {
  try {
    if (event.node.req.method !== 'PUT') {
      throw createError({
        statusCode: 405,
        message: 'Method not allowed',
      });
    }

    const slug = getRouterParam(event, 'slug');

    if (!slug) {
      throw createError({
        statusCode: 400,
        message: '缺少文章标识',
      });
    }

    const body = await readBody(event);
    const result = updateArticleSchema.safeParse(body);

    if (!result.success) {
      throw createError({
        statusCode: 400,
        message: '请求参数错误',
      });
    }

    // 检查文章是否存在
    const existing = await db.query.articleMeta.findFirst({
      where: eq(articleMeta.slug, slug),
    });

    if (!existing) {
      throw createError({
        statusCode: 404,
        message: '文章不存在',
      });
    }

    const updateData: any = { ...result.data };
    
    // 如果状态改为 published 且之前未发布，设置发布时间
    if (updateData.status === 'published' && !existing.publishedAt) {
      updateData.publishedAt = new Date();
    }

    const [updated] = await db
      .update(articleMeta)
      .set(updateData)
      .where(eq(articleMeta.slug, slug))
      .returning();

    return {
      success: true,
      data: updated,
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('更新文章失败:', error);
    return {
      success: false,
      message: '更新文章失败',
    };
  }
});
