import { db } from '../database/postgres'
import { admins } from '../database/schema/admins'
import { hashPassword } from '../utils/password'

async function initAdmin() {
  const username = 'admin'
  const password = 'admin123456'
  
  const passwordHash = await hashPassword(password)
  
  try {
    // 插入管理员
    await db.insert(admins).values({
      username,
      passwordHash,
      email: 'admin@example.com',
      role: 'admin',
    })
    
    console.log('✓ 初始化管理员账号成功')
    console.log('')
    console.log('═══════════════════════════════════════')
    console.log('  管理后台登录信息')
    console.log('═══════════════════════════════════════')
    console.log(`  用户名：${username}`)
    console.log(`  密码：${password}`)
    console.log('═══════════════════════════════════════')
    console.log('')
    console.log('⚠️  请及时修改密码！')
    console.log('')
  } catch (error: any) {
    console.error('❌ 初始化管理员失败:', error.message)
    process.exit(1)
  }
  
  process.exit(0)
}

initAdmin()
