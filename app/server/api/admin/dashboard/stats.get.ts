import { defineEventHandler, getQuery } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta, categories, tags, comments } from '~/server/database/schema';
import { sql, desc, count } from 'drizzle-orm';

export default defineEventHandler(async (event) => {
  try {
    // 获取文章数量
    const articleCountResult = await db.select({ count: count() }).from(articleMeta);
    const articleCount = articleCountResult[0]?.count || 0;

    // 获取分类数量
    const categoryCountResult = await db.select({ count: count() }).from(categories);
    const categoryCount = categoryCountResult[0]?.count || 0;

    // 获取标签数量
    const tagCountResult = await db.select({ count: count() }).from(tags);
    const tagCount = tagCountResult[0]?.count || 0;

    // 获取评论数量
    const commentCountResult = await db.select({ count: count() }).from(comments);
    const commentCount = commentCountResult[0]?.count || 0;

    // 获取最近的文章
    const recentArticlesResult = await db
      .select()
      .from(articleMeta)
      .orderBy(desc(articleMeta.createdAt))
      .limit(5);

    // 获取最近的评论
    const recentCommentsResult = await db
      .select()
      .from(comments)
      .orderBy(desc(comments.createdAt))
      .limit(5);

    return {
      success: true,
      stats: {
        articleCount,
        categoryCount,
        tagCount,
        commentCount,
      },
      recent_articles: recentArticlesResult.map((article: any) => ({
        id: article.id,
        title: article.title,
        slug: article.slug,
        status: article.status,
        created_at: article.createdAt,
      })),
      recent_comments: recentCommentsResult.map((comment: any) => ({
        id: comment.id,
        content: comment.content,
        author_name: comment.authorName || '匿名',
        status: comment.status,
        created_at: comment.createdAt,
      })),
    };
  } catch (error: any) {
    console.error('获取仪表盘数据失败:', error);
    return {
      success: false,
      message: '获取数据失败',
    };
  }
});