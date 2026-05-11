import { desc, count } from 'drizzle-orm';
import { db } from '~/server/database/postgres';
import { articleMeta, categories, tags, comments } from '~/server/database/schema';

export async function getDashboardStats() {
  const articleCountResult = await db.select({ count: count() }).from(articleMeta);
  const categoryCountResult = await db.select({ count: count() }).from(categories);
  const tagCountResult = await db.select({ count: count() }).from(tags);
  const commentCountResult = await db.select({ count: count() }).from(comments);

  const recentArticlesResult = await db
    .select()
    .from(articleMeta)
    .orderBy(desc(articleMeta.createdAt))
    .limit(5);

  const recentCommentsResult = await db
    .select()
    .from(comments)
    .orderBy(desc(comments.createdAt))
    .limit(5);

  return {
    success: true,
    stats: {
      articleCount: articleCountResult[0]?.count || 0,
      categoryCount: categoryCountResult[0]?.count || 0,
      tagCount: tagCountResult[0]?.count || 0,
      commentCount: commentCountResult[0]?.count || 0,
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
}
