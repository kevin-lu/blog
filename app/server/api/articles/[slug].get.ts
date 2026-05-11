import { defineEventHandler, getRouterParam } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { eq } from 'drizzle-orm';
import { serializeArticle } from '~/server/utils/article-serializer';
import { getArticleRelations } from '~/server/utils/article-relations';

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

    const relations = await getArticleRelations(article[0].id);

    return {
      success: true,
      data: serializeArticle({
        ...article[0],
        ...relations,
      }),
    };
  } catch (error: any) {
    console.error('获取文章详情失败:', error);
    return {
      success: false,
      message: '获取文章详情失败',
    };
  }
});
