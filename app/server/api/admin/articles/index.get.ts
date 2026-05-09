import { defineEventHandler, getQuery } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
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
      whereClause = (articleMeta: any) => articleMeta.status === status;
    }

    // 查询总数
    const total = await db.select().from(articleMeta).where(whereClause);
    
    // 查询数据
    const articles = await db
      .select()
      .from(articleMeta)
      .where(whereClause)
      .orderBy(desc(articleMeta.createdAt))
      .limit(pageSize)
      .offset((page - 1) * pageSize);

    return {
      success: true,
      data: {
        data: articles,
        total: total.length,
        page,
        pageSize,
        totalPages: Math.ceil(total.length / pageSize),
      },
    };
  } catch (error: any) {
    console.error('获取文章列表失败:', error);
    return {
      success: false,
      message: '获取文章列表失败',
    };
  }
});
