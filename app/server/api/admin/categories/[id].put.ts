import { defineEventHandler, readBody, createError, getRouterParam } from 'h3';
import { eq } from 'drizzle-orm';
import { z } from 'zod';
import { db } from '~/server/database/postgres';
import { categories } from '~/server/database/schema/categories';

const updateCategorySchema = z.object({
  name: z.string().min(1).max(50).optional(),
  slug: z.string().min(1).max(50).optional(),
  description: z.string().nullable().optional(),
  parentId: z.number().nullable().optional(),
  parent_id: z.number().nullable().optional(),
  sortOrder: z.number().optional(),
  sort_order: z.number().optional(),
});

export default defineEventHandler(async (event) => {
  try {
    const id = Number(getRouterParam(event, 'id'));
    if (!Number.isInteger(id) || id <= 0) {
      throw createError({
        statusCode: 400,
        message: '分类 ID 无效',
      });
    }

    const body = await readBody(event);
    const result = updateCategorySchema.safeParse(body);

    if (!result.success) {
      throw createError({
        statusCode: 400,
        message: '请求参数错误',
      });
    }

    const { parent_id, sort_order, ...data } = result.data;
    const updateData: any = {
      ...data,
      updatedAt: new Date(),
    };

    if ('parent_id' in result.data) {
      updateData.parentId = parent_id ?? null;
    }

    if ('sort_order' in result.data) {
      updateData.sortOrder = sort_order ?? 0;
    }

    const [updated] = await db
      .update(categories)
      .set(updateData)
      .where(eq(categories.id, id))
      .returning();

    if (!updated) {
      throw createError({
        statusCode: 404,
        message: '分类不存在',
      });
    }

    return {
      success: true,
      data: updated,
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('更新分类失败:', error);
    return {
      success: false,
      message: '更新分类失败',
    };
  }
});
