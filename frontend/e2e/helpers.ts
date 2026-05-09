import { Page, Locator } from '@playwright/test'

/**
 * E2E 测试辅助工具
 */

/**
 * 模拟登录
 */
export async function login(page: Page, username: string = 'admin', password: string = 'admin123') {
  await page.goto('/admin/login')
  await page.fill('input[type="text"]', username)
  await page.fill('input[type="password"]', password)
  await page.click('button[type="submit"]')
  await page.waitForURL('/admin')
}

/**
 * 模拟登出
 */
export async function logout(page: Page) {
  const logoutButton = page.locator('.logout-button')
  await logoutButton.click()
  await page.waitForURL('/admin/login')
}

/**
 * 等待表格加载完成
 */
export async function waitForTable(page: Page, selector: string = '.n-data-table') {
  await page.waitForSelector(selector, { timeout: 5000 })
  const table = page.locator(selector)
  await expect(table).toBeVisible()
}

/**
 * 等待模态框出现
 */
export async function waitForModal(page: Page, selector: string = '.n-modal') {
  await page.waitForSelector(selector, { timeout: 5000 })
  const modal = page.locator(selector)
  await expect(modal).toBeVisible()
}

/**
 * 等待 Toast 提示出现
 */
export async function waitForToast(page: Page, message: string) {
  await page.waitForSelector('.n-message', { timeout: 5000 })
  const toast = page.locator('.n-message')
  await expect(toast).toContainText(message)
}

/**
 * 等待加载完成
 */
export async function waitForLoading(page: Page) {
  const spin = page.locator('.n-spin')
  await expect(spin).not.toBeVisible()
}

/**
 * 创建测试文章
 */
export async function createTestArticle(
  page: Page,
  title: string = '测试文章',
  content: string = '测试内容'
) {
  await page.goto('/admin/articles')
  await page.click('.create-button')
  await page.waitForURL(/\/admin\/articles\/new/)
  
  await page.fill('input[placeholder="文章标题"]', title)
  await page.fill('textarea[placeholder="文章描述"]', '测试描述')
  
  // 填充 Markdown 编辑器
  const editor = page.locator('.CodeMirror')
  await editor.click()
  await page.keyboard.type(content)
  
  await page.click('button[type="submit"]')
  await waitForToast(page, '创建成功')
}

/**
 * 创建测试分类
 */
export async function createTestCategory(page: Page, name: string = '测试分类') {
  await page.goto('/admin/categories')
  await page.click('.create-button')
  
  await page.fill('input[placeholder="分类名称"]', name)
  await page.fill('input[placeholder="分类别名"]', slugify(name))
  
  await page.click('button[type="submit"]')
  await waitForToast(page, '创建成功')
}

/**
 * 创建测试标签
 */
export async function createTestTag(page: Page, name: string = '测试标签') {
  await page.goto('/admin/tags')
  await page.click('.create-button')
  
  await page.fill('input[placeholder="标签名称"]', name)
  
  await page.click('button[type="submit"]')
  await waitForToast(page, '创建成功')
}

/**
 * 将中文转换为 slug
 */
function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
}

/**
 * 删除测试数据
 */
export async function cleanupTestData(page: Page) {
  // 清除 localStorage
  await page.evaluate(() => {
    localStorage.clear()
    sessionStorage.clear()
  })
}
