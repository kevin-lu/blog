import { defineEventHandler, createError, getRouterParam } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { eq } from 'drizzle-orm';

export default defineEventHandler(async (event) => {
  try {
    if (event.node.req.method !== 'DELETE') {
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

    await db.delete(articleMeta).where(eq(articleMeta.slug, slug));

    return {
      success: true,
      message: '文章已删除',
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('删除文章失败:', error);
    return {
      success: false,
      message: '删除文章失败',
    };
  }
});
