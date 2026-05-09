import { defineEventHandler, getQuery } from 'h3';
import { db } from '~/server/database/postgres';
import { comments } from '~/server/database/schema/comments';
import { desc } from 'drizzle-orm';

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event);
    const page = Number(query.page) || 1;
    const pageSize = Number(query.pageSize) || 20;
    const status = query.status as string;

    // 构建查询条件
    let whereClause;
    if (status) {
      whereClause = (comments: any) => comments.status === status;
    }

    // 查询数据
    const commentList = await db
      .select()
      .from(comments)
      .where(whereClause)
      .orderBy(desc(comments.createdAt))
      .limit(pageSize)
      .offset((page - 1) * pageSize);

    // 查询总数
    const total = await db.select().from(comments).where(whereClause);

    return {
      success: true,
      data: {
        data: commentList,
        total: total.length,
        page,
        pageSize,
        totalPages: Math.ceil(total.length / pageSize),
      },
    };
  } catch (error: any) {
    console.error('获取评论列表失败:', error);
    return {
      success: false,
      message: '获取评论列表失败',
    };
  }
});
