import { defineEventHandler, readBody, createError } from 'h3';
import { db } from '~/server/database/postgres';
import { admins } from '~/server/database/schema/admins';
import { eq } from 'drizzle-orm';
import { verifyPassword } from '~/server/utils/password';
import { generateToken } from '~/server/utils/jwt';
import { z } from 'zod';

const loginSchema = z.object({
  username: z.string().min(1, '用户名不能为空'),
  password: z.string().min(1, '密码不能为空'),
});

export default defineEventHandler(async (event) => {
  if (event.node.req.method !== 'POST') {
    throw createError({
      statusCode: 405,
      message: 'Method not allowed',
    });
  }

  try {
    const body = await readBody(event);
    const result = loginSchema.safeParse(body);

    if (!result.success) {
      throw createError({
        statusCode: 400,
        message: '请求参数错误',
        data: result.error.errors,
      });
    }

    const { username, password } = result.data;

    // 查找管理员
    const admin = await db.query.admins.findFirst({
      where: eq(admins.username, username),
    });

    if (!admin) {
      throw createError({
        statusCode: 401,
        message: '用户名或密码错误',
      });
    }

    // 验证密码
    const isValid = await verifyPassword(password, admin.passwordHash);

    if (!isValid) {
      throw createError({
        statusCode: 401,
        message: '用户名或密码错误',
      });
    }

    // 生成 token
    const token = generateToken({
      adminId: admin.id,
      username: admin.username,
      role: admin.role || 'admin',
    });

    return {
      success: true,
      data: {
        token,
        admin: {
          id: admin.id,
          username: admin.username,
          email: admin.email,
          avatar: admin.avatar,
          role: admin.role,
        },
      },
    };
  } catch (error: any) {
    if (error.statusCode) {
      throw error;
    }
    
    console.error('登录错误:', error);
    throw createError({
      statusCode: 500,
      message: '服务器错误',
    });
  }
});
