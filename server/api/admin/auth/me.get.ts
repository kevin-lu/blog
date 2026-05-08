import { defineEventHandler } from 'h3';
import { db } from '~/server/database/postgres';
import { admins } from '~/server/database/schema/admins';
import { eq } from 'drizzle-orm';

export default defineEventHandler(async (event) => {
  const adminId = event.context.admin?.adminId;

  if (!adminId) {
    return {
      success: false,
      message: '未登录',
    };
  }

  const admin = await db.query.admins.findFirst({
    where: eq(admins.id, adminId),
    columns: {
      id: true,
      username: true,
      email: true,
      avatar: true,
      role: true,
      createdAt: true,
    },
  });

  if (!admin) {
    return {
      success: false,
      message: '用户不存在',
    };
  }

  return {
    success: true,
    data: admin,
  };
});
