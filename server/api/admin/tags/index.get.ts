import { defineEventHandler } from 'h3';
import { db } from '~/server/database/postgres';
import { tags } from '~/server/database/schema/tags';
import { asc } from 'drizzle-orm';

export default defineEventHandler(async () => {
  try {
    const tagList = await db
      .select()
      .from(tags)
      .orderBy(asc(tags.name));

    return {
      success: true,
      data: tagList,
    };
  } catch (error: any) {
    console.error('获取标签列表失败:', error);
    return {
      success: false,
      message: '获取标签列表失败',
    };
  }
});
