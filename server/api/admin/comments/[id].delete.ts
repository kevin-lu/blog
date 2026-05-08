import { defineEventHandler, createError, getRouterParam } from 'h3';
import { db } from '~/server/database/postgres';
import { comments } from '~/server/database/schema/comments';
import { eq } from 'drizzle-orm';

export default defineEventHandler(async (event) => {
  try {
    if (event.node.req.method !== 'DELETE') {
      throw createError({
        statusCode: 405,
        message: 'Method not allowed',
      });
    }

    const id = getRouterParam(event, 'id');
    const numId = parseInt(id);

    if (isNaN(numId)) {
      throw createError({
        statusCode: 400,
        message: '无效的评论 ID',
      });
    }

    // 检查评论是否存在
    const existing = await db.query.comments.findFirst({
      where: eq(comments.id, numId),
    });

    if (!existing) {
      throw createError({
        statusCode: 404,
        message: '评论不存在',
      });
    }

    await db.delete(comments).where(eq(comments.id, numId));

    return {
      success: true,
      message: '评论已删除',
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('删除评论失败:', error);
    return {
      success: false,
      message: '删除评论失败',
    };
  }
});
