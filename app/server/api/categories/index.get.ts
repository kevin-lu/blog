import { defineEventHandler } from 'h3';
import { db } from '~/server/database/postgres';
import { categories } from '~/server/database/schema/categories';
import { asc } from 'drizzle-orm';

export default defineEventHandler(async () => {
  try {
    const categoryList = await db
      .select()
      .from(categories)
      .orderBy(asc(categories.sortOrder), asc(categories.name));

    return {
      success: true,
      data: categoryList,
    };
  } catch (error: any) {
    console.error('获取分类列表失败:', error);
    return {
      success: false,
      message: '获取分类列表失败',
    };
  }
});
