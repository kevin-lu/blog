import { defineEventHandler, readBody, createError } from 'h3';
import { db } from '~/server/database/postgres';
import { siteSettings } from '~/server/database/schema/siteSettings';
import { eq } from 'drizzle-orm';

export default defineEventHandler(async (event) => {
  try {
    if (event.node.req.method !== 'PUT') {
      throw createError({
        statusCode: 405,
        message: 'Method not allowed',
      });
    }

    const body = await readBody(event);

    if (!body || typeof body !== 'object') {
      throw createError({
        statusCode: 400,
        message: '请求参数错误',
      });
    }

    // 批量更新配置
    const updates: Promise<any>[] = [];

    for (const [key, value] of Object.entries(body)) {
      updates.push(
        db
          .insert(siteSettings)
          .values({
            keyName: key,
            keyValue: value as string,
            updatedAt: new Date(),
          })
          .onConflictDoUpdate({
            target: siteSettings.keyName,
            set: {
              keyValue: value as string,
              updatedAt: new Date(),
            },
          })
      );
    }

    await Promise.all(updates);

    // 重新读取配置
    const settings = await db.select().from(siteSettings);
    const config: Record<string, any> = {};
    for (const setting of settings) {
      config[setting.keyName] = setting.keyValue;
    }

    return {
      success: true,
      data: config,
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    console.error('更新站点配置失败:', error);
    return {
      success: false,
      message: '更新站点配置失败',
    };
  }
});
