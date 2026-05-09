import { defineEventHandler } from 'h3';

export default defineEventHandler(async () => {
  // 登出操作由前端清除 token 即可
  return {
    success: true,
    message: '已登出',
  };
});
