import { defineEventHandler, getHeader, createError } from 'h3';
import { verifyToken } from '../utils/jwt';

export default defineEventHandler(async (event) => {
  // 跳过登录接口
  if (event.node.req.url?.startsWith('/api/admin/auth/login')) {
    return;
  }

  // 跳过 OPTIONS 预检请求（CORS）
  if (event.node.req.method === 'OPTIONS') {
    return;
  }

  // 所有 /api/admin/* 请求需要认证
  if (!event.node.req.url?.startsWith('/api/admin')) {
    return;
  }

  const authHeader = getHeader(event, 'Authorization');
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    throw createError({
      statusCode: 401,
      message: '未提供认证 token',
    });
  }

  const token = authHeader.substring(7);
  const payload = verifyToken(token);

  if (!payload) {
    throw createError({
      statusCode: 401,
      message: 'Token 无效或已过期',
    });
  }

  // 将用户信息添加到上下文中
  event.context.admin = payload;
});

declare module 'h3' {
  interface H3EventContext {
    admin?: {
      adminId: number;
      username: string;
      role: string;
    };
  }
}
