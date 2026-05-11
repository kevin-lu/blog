import { defineEventHandler, getQuery } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { eq, like, desc, and, type SQL } from 'drizzle-orm';
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
    
    // 查询总数
    const total = await db
      .select({ count: articleMeta.id })
      .from(articleMeta)
      .where(whereClause);
    
    return {
      success: true,
      data: {
        data: articles.map(serializeArticle),
        total: total[0]?.count || 0,
        page,
        pageSize: limit,
        totalPages: Math.ceil((total[0]?.count || 0) / limit),
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
