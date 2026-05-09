import { defineEventHandler, readBody, createError, getRouterParam } from 'h3';
import { db } from '~/server/database/postgres';
import { comments } from '~/server/database/schema/comments';
import { eq } from 'drizzle-orm';
import { z } from 'zod';

const updateCommentSchema = z.object({
  status: z.enum(['pending', 'approved', 'rejected']).optional(),
  isPinned: z.boolean().optional(),
});

export default defineEventHandler(async (event) => {
  try {
    if (event.node.req.method !== 'PUT') {
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

    const body = await readBody(event);
    const result = updateCommentSchema.safeParse(body);

    if (!result.success) {
      throw createError({
        statusCode: 400,
        message: '请求参数错误',
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

    const [updated] = await db
      .update(comments)
      .set(result.data)
      .where(eq(comments.id, numId))
      .returning();

    return {
      success: true,
      data: updated,
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('更新评论失败:', error);
    return {
      success: false,
      message: '更新评论失败',
    };
  }
});
