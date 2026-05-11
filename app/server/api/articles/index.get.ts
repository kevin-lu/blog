import { defineEventHandler, getQuery } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { eq, like, desc, and, type SQL, sql } from 'drizzle-orm';
import { serializeArticle } from '~/server/utils/article-serializer';

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event);
    const page = Number(query.page) || 1;
    const limit = Number(query.limit) || 10;
    const search = query.search as string;
    const category = query.category as string;
    const tag = query.tag as string;
    
    // 构建查询条件
    const conditions: SQL[] = [eq(articleMeta.status, 'published')];
    
    if (search) {
      conditions.push(like(articleMeta.title, `%${search}%`));
    }
    
    // TODO: 添加分类和标签过滤
    
    const whereClause = and(...conditions);
    
    // 查询数据
    const articles = await db
      .select()
      .from(articleMeta)
      .where(whereClause)
      .orderBy(desc(articleMeta.createdAt))
      .limit(limit)
      .offset((page - 1) * limit);
    
    // 查询总数 - 使用正确的 count() 聚合
    const totalResult = await db
      .select({ count: sql<number>`COUNT(*)` })
      .from(articleMeta)
      .where(whereClause);
    
    const totalCount = totalResult[0]?.count || 0;
    
    return {
      success: true,
      data: {
        data: articles.map(serializeArticle),
        total: totalCount,
        page,
        pageSize: limit,
        totalPages: Math.ceil(totalCount / limit),
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
