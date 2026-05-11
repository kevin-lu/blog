import { defineEventHandler, readBody, createError } from 'h3';
import { db } from '~/server/database/postgres';
import { categories } from '~/server/database/schema/categories';
import { z } from 'zod';

const createCategorySchema = z.object({
  name: z.string().min(1).max(50),
  slug: z.string().min(1).max(50),
  description: z.string().nullable().optional(),
  parentId: z.number().optional(),
  parent_id: z.number().nullable().optional(),
  sortOrder: z.number().optional(),
  sort_order: z.number().optional(),
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
    const result = createCategorySchema.safeParse(body);

    if (!result.success) {
      throw createError({
        statusCode: 400,
        message: '请求参数错误',
      });
    }

    const { name, slug, description, parentId, parent_id, sortOrder, sort_order } = result.data;

    // 检查 slug 是否已存在
    const existing = await db.query.categories.findFirst({
      where: eq(categories.slug, slug),
    });

    if (existing) {
      throw createError({
        statusCode: 400,
        message: 'slug 已存在',
      });
    }

    const [newCategory] = await db.insert(categories).values({
      name,
      slug,
      description: description || null,
      parentId: parentId ?? parent_id ?? null,
      sortOrder: sortOrder ?? sort_order ?? 0,
    }).returning();

    return {
      success: true,
      data: newCategory,
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('创建分类失败:', error);
    return {
      success: false,
      message: '创建分类失败',
    };
  }
});

import { eq } from 'drizzle-orm';
