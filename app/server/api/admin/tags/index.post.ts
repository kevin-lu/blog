import { defineEventHandler, readBody, createError } from 'h3';
import { db } from '~/server/database/postgres';
import { tags } from '~/server/database/schema/categories';
import { z } from 'zod';

const createTagSchema = z.object({
  name: z.string().min(1).max(50),
  slug: z.string().min(1).max(50),
});

export default defineEventHandler(async (event) => {
  try {
    if (event.node.req.method !== 'POST') {
      throw createError({
        statusCode: 405,
        message: 'Method not allowed',
      });
    }

    const body = await readBody(event);
    const result = createTagSchema.safeParse(body);

    if (!result.success) {
      throw createError({
        statusCode: 400,
        message: '请求参数错误',
      });
    }

    const { name, slug } = result.data;

    // 检查 slug 是否已存在
    const existing = await db.query.tags.findFirst({
      where: eq(tags.slug, slug),
    });

    if (existing) {
      throw createError({
        statusCode: 400,
        message: 'slug 已存在',
      });
    }

    const [newTag] = await db.insert(tags).values({
      name,
      slug,
    }).returning();

    return {
      success: true,
      data: newTag,
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('创建标签失败:', error);
    return {
      success: false,
      message: '创建标签失败',
    };
  }
});

import { eq } from 'drizzle-orm';
