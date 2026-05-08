import { hashPassword } from '../server/utils/password';
import { db } from '../server/database/postgres';
import { admins } from '../server/database/schema/admins';
import { eq } from 'drizzle-orm';

async function createAdmin() {
  const username = process.argv[2];
  const password = process.argv[3];
  const email = process.argv[4];

  if (!username || !password) {
    console.error('使用方法：npm run create-admin <用户名> <密码> [邮箱]');
    process.exit(1);
  }

  try {
    // 检查管理员是否已存在
    const existingAdmin = await db.query.admins.findFirst({
      where: eq(admins.username, username),
    });

    if (existingAdmin) {
      console.error('错误：管理员已存在');
      process.exit(1);
    }

    // 验证密码强度
    const { valid, errors } = await import('../server/utils/password').then(m => m.validatePasswordStrength(password));
    if (!valid) {
      console.error('密码强度不足：');
      errors.forEach(err => console.error(`  - ${err}`));
      process.exit(1);
    }

    // 加密密码
    const passwordHash = await hashPassword(password);

    // 创建管理员
    const [newAdmin] = await db.insert(admins).values({
      username,
      passwordHash,
      email: email || null,
      role: 'admin',
    }).returning();

    console.log('✓ 管理员创建成功！');
    console.log(`  用户名：${newAdmin.username}`);
    console.log(`  角色：${newAdmin.role}`);
    console.log(`  创建时间：${newAdmin.createdAt}`);
  } catch (error) {
    console.error('创建管理员失败:', error);
    process.exit(1);
  }
}

createAdmin();
