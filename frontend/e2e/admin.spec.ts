import { test, expect } from '@playwright/test'

test.describe('管理员登录', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/admin/login')
  })

  test('应该显示登录表单', async ({ page }) => {
    await expect(page.locator('input[type="text"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('应该成功登录', async ({ page }) => {
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')
    
    // 应该跳转到管理后台首页
    await expect(page).toHaveURL('/admin')
  })

  test('应该显示错误信息（密码错误）', async ({ page }) => {
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'wrong')
    await page.click('button[type="submit"]')
    
    // 应该显示错误信息
    const error = page.locator('.error-message')
    await expect(error).toBeVisible()
  })

  test('应该验证必填字段', async ({ page }) => {
    await page.click('button[type="submit"]')
    
    // 表单验证应该阻止提交
    const usernameInput = page.locator('input[type="text"]')
    await expect(usernameInput).toHaveAttribute('required')
  })
})

test.describe('管理后台首页', () => {
  test.beforeEach(async ({ page }) => {
    // 模拟已登录状态
    await page.goto('/admin')
    await page.evaluate(() => {
      localStorage.setItem('blog_access_token', 'test-token')
      localStorage.setItem('blog_user', JSON.stringify({
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        role: 'admin',
      }))
    })
    await page.reload()
  })

  test('应该显示管理后台标题', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('管理后台')
  })

  test('应该显示侧边栏菜单', async ({ page }) => {
    const sidebar = page.locator('.admin-sidebar')
    await expect(sidebar).toBeVisible()
  })

  test('应该显示统计卡片', async ({ page }) => {
    // 等待统计卡片加载
    await page.waitForSelector('.stat-card', { timeout: 5000 })
    
    const statCards = page.locator('.stat-card')
    await expect(statCards).not.toHaveCount(0)
  })

  test('应该可以退出登录', async ({ page }) => {
    const logoutButton = page.locator('.logout-button')
    await logoutButton.click()
    
    // 应该清除本地存储并跳转到登录页
    await expect(page).toHaveURL('/admin/login')
  })
})

test.describe('文章管理', () => {
  test.beforeEach(async ({ page }) => {
    // 模拟已登录状态
    await page.goto('/admin/articles')
    await page.evaluate(() => {
      localStorage.setItem('blog_access_token', 'test-token')
      localStorage.setItem('blog_user', JSON.stringify({
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        role: 'admin',
      }))
    })
    await page.reload()
  })

  test('应该显示文章列表', async ({ page }) => {
    // 等待文章列表加载
    await page.waitForSelector('.article-table', { timeout: 5000 })
    
    const table = page.locator('.article-table')
    await expect(table).toBeVisible()
  })

  test('应该可以创建新文章', async ({ page }) => {
    const createButton = page.locator('.create-button')
    await createButton.click()
    
    // 应该跳转到编辑页面
    await expect(page).toHaveURL(/\/admin\/articles\/new/)
  })

  test('应该可以编辑文章', async ({ page }) => {
    // 等待文章列表加载
    await page.waitForSelector('.article-table', { timeout: 5000 })
    
    const editButton = page.locator('.edit-button').first()
    await editButton.click()
    
    // 应该跳转到编辑页面
    await expect(page).toHaveURL(/\/admin\/articles\/\d+\/edit/)
  })

  test('应该可以删除文章', async ({ page }) => {
    // 等待文章列表加载
    await page.waitForSelector('.article-table', { timeout: 5000 })
    
    const deleteButton = page.locator('.delete-button').first()
    await deleteButton.click()
    
    // 应该显示确认对话框
    const confirmDialog = page.locator('.n-modal')
    await expect(confirmDialog).toBeVisible()
  })
})

test.describe('分类管理', () => {
  test.beforeEach(async ({ page }) => {
    // 模拟已登录状态
    await page.goto('/admin/categories')
    await page.evaluate(() => {
      localStorage.setItem('blog_access_token', 'test-token')
      localStorage.setItem('blog_user', JSON.stringify({
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        role: 'admin',
      }))
    })
    await page.reload()
  })

  test('应该显示分类列表', async ({ page }) => {
    // 等待分类列表加载
    await page.waitForSelector('.category-table', { timeout: 5000 })
    
    const table = page.locator('.category-table')
    await expect(table).toBeVisible()
  })

  test('应该可以创建新分类', async ({ page }) => {
    const createButton = page.locator('.create-button')
    await createButton.click()
    
    // 应该显示创建表单
    const form = page.locator('.category-form')
    await expect(form).toBeVisible()
  })

  test('应该可以编辑分类', async ({ page }) => {
    // 等待分类列表加载
    await page.waitForSelector('.category-table', { timeout: 5000 })
    
    const editButton = page.locator('.edit-button').first()
    await editButton.click()
    
    // 应该显示编辑表单
    const form = page.locator('.category-form')
    await expect(form).toBeVisible()
  })
})

test.describe('标签管理', () => {
  test.beforeEach(async ({ page }) => {
    // 模拟已登录状态
    await page.goto('/admin/tags')
    await page.evaluate(() => {
      localStorage.setItem('blog_access_token', 'test-token')
      localStorage.setItem('blog_user', JSON.stringify({
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        role: 'admin',
      }))
    })
    await page.reload()
  })

  test('应该显示标签列表', async ({ page }) => {
    // 等待标签列表加载
    await page.waitForSelector('.tag-table', { timeout: 5000 })
    
    const table = page.locator('.tag-table')
    await expect(table).toBeVisible()
  })

  test('应该可以创建新标签', async ({ page }) => {
    const createButton = page.locator('.create-button')
    await createButton.click()
    
    // 应该显示创建表单
    const form = page.locator('.tag-form')
    await expect(form).toBeVisible()
  })
})
