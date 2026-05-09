import { db } from '../database/postgres'
import { admins } from '../database/schema/admins'
import { hashPassword } from '../utils/password'
import { eq } from 'drizzle-orm'

async function createAdmin() {
  const username = 'admin'
  const password = 'admin123456' // 默认密码
  
  const passwordHash = await hashPassword(password)
  
  try {
    // 更新现有管理员密码
    await db.update(admins).set({
      passwordHash,
      email: 'admin@example.com',
      role: 'admin',
    }).where(eq(admins.username, username))
    
    console.log('✓ 管理员密码已重置')
    console.log(`用户名：${username}`)
    console.log(`密码：${password}`)
    console.log('\n请及时修改密码！')
  } catch (error) {
    console.error('创建管理员失败:', error)
    process.exit(1)
  }
  
  process.exit(0)
}

createAdmin()
