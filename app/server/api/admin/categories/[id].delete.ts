import { defineEventHandler, createError, getRouterParam } from 'h3';
import { eq } from 'drizzle-orm';
import { db } from '~/server/database/postgres';
import { articleCategories, categories } from '~/server/database/schema/categories';

export default defineEventHandler(async (event) => {
  try {
    const id = Number(getRouterParam(event, 'id'));
    if (!Number.isInteger(id) || id <= 0) {
      throw createError({
        statusCode: 400,
        message: '分类 ID 无效',
      });
    }

    await db.delete(articleCategories).where(eq(articleCategories.categoryId, id));
    const [deleted] = await db
      .delete(categories)
      .where(eq(categories.id, id))
      .returning();

    if (!deleted) {
      throw createError({
        statusCode: 404,
        message: '分类不存在',
      });
    }

    return {
      success: true,
      message: '删除成功',
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('删除分类失败:', error);
    return {
      success: false,
      message: '删除分类失败',
    };
  }
});
