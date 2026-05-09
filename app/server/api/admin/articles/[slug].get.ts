import { defineEventHandler, getRouterParam, createError } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { eq } from 'drizzle-orm';

export default defineEventHandler(async (event) => {
  try {
    const slug = getRouterParam(event, 'slug');

    if (!slug) {
      throw createError({
        statusCode: 400,
        message: '缺少文章标识',
      });
    }

    const article = await db.query.articleMeta.findFirst({
      where: eq(articleMeta.slug, slug),
    });

    if (!article) {
      throw createError({
        statusCode: 404,
        message: '文章不存在',
      });
    }

    return {
      success: true,
      data: article,
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('获取文章失败:', error);
    return {
      success: false,
      message: '获取文章失败',
    };
  }
});
