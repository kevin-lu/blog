import { defineEventHandler } from 'h3';
import { getCategoryList } from '~/server/utils/category-list';

export default defineEventHandler(async () => {
  try {
    return {
      success: true,
      data: await getCategoryList(),
    };
  } catch (error: any) {
    console.error('获取分类列表失败:', error);
    return {
      success: false,
      message: '获取分类列表失败',
    };
  }
});
