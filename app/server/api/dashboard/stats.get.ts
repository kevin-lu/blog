import { defineEventHandler } from 'h3';
import { getDashboardStats } from '~/server/utils/dashboard-stats';

export default defineEventHandler(async () => {
  try {
    return await getDashboardStats();
  } catch (error: any) {
    console.error('获取仪表盘数据失败:', error);
    return {
      success: false,
      message: '获取数据失败',
    };
  }
});
