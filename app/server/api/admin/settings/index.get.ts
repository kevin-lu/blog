import { defineEventHandler } from 'h3';
import { db } from '~/server/database/postgres';
import { siteSettings } from '~/server/database/schema/siteSettings';

export default defineEventHandler(async () => {
  try {
    const settings = await db.select().from(siteSettings);

    // 转换为键值对格式
    const config: Record<string, any> = {};
    for (const setting of settings) {
      config[setting.keyName] = setting.keyValue;
    }

    return {
      success: true,
      data: config,
    };
  } catch (error: any) {
    console.error('获取站点配置失败:', error);
    return {
      success: false,
      message: '获取站点配置失败',
    };
  }
});
