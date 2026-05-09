import { defineEventHandler, getRouterParam } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { eq } from 'drizzle-orm';

export default defineEventHandler(async (event) => {
  try {
    const slug = getRouterParam(event, 'slug');
    
    if (!slug) {
      return {
        success: false,
        message: '文章 slug 不能为空',
      };
    }

    const article = await db
      .select()
      .from(articleMeta)
      .where(eq(articleMeta.slug, slug))
      .limit(1);

    if (!article || article.length === 0) {
      return {
        success: false,
        message: '文章不存在',
      };
    }

    return {
      success: true,
      data: article[0],
    };
  } catch (error: any) {
    console.error('获取文章详情失败:', error);
    return {
      success: false,
      message: '获取文章详情失败',
    };
  }
});
