import { test, expect } from '@playwright/test'

test.describe('博客首页', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('应该正确显示页面标题', async ({ page }) => {
    await expect(page).toHaveTitle(/博客/)
  })

  test('应该显示导航栏', async ({ page }) => {
    const nav = page.locator('nav')
    await expect(nav).toBeVisible()
  })

  test('应该显示文章列表', async ({ page }) => {
    // 等待文章列表加载
    await page.waitForSelector('.article-card', { timeout: 5000 })
    
    const articles = page.locator('.article-card')
    await expect(articles).not.toHaveCount(0)
  })

  test('点击文章应该跳转到详情页', async ({ page }) => {
    // 等待文章列表加载
    await page.waitForSelector('.article-card', { timeout: 5000 })
    
    const firstArticle = page.locator('.article-card').first()
    await firstArticle.click()
    
    // 应该跳转到文章详情页
    await expect(page).toHaveURL(/\/posts\/.+/)
  })

  test('应该支持分页', async ({ page }) => {
    // 等待分页器出现
    await page.waitForSelector('.n-pagination', { timeout: 5000 })
    
    const pagination = page.locator('.n-pagination')
    await expect(pagination).toBeVisible()
  })
})

test.describe('响应式布局', () => {
  test('应该在移动端正确显示', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/')
    
    // 移动端菜单应该可见
    const mobileMenu = page.locator('.mobile-menu')
    await expect(mobileMenu).toBeVisible()
  })

  test('应该在桌面端正确显示', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 })
    await page.goto('/')
    
    // 桌面导航应该可见
    const desktopNav = page.locator('nav')
    await expect(desktopNav).toBeVisible()
    
    // 移动端菜单应该隐藏
    const mobileMenu = page.locator('.mobile-menu')
    await expect(mobileMenu).not.toBeVisible()
  })
})

test.describe('分类页面', () => {
  test('应该显示所有分类', async ({ page }) => {
    await page.goto('/categories')
    
    // 等待分类列表加载
    await page.waitForSelector('.category-item', { timeout: 5000 })
    
    const categories = page.locator('.category-item')
    await expect(categories).not.toHaveCount(0)
  })

  test('点击分类应该筛选文章', async ({ page }) => {
    await page.goto('/categories')
    
    // 等待分类列表加载
    await page.waitForSelector('.category-item', { timeout: 5000 })
    
    const firstCategory = page.locator('.category-item').first()
    await firstCategory.click()
    
    // 应该跳转到分类文章列表
    await expect(page).toHaveURL(/\/categories\/.+/)
  })
})

test.describe('标签页面', () => {
  test('应该显示所有标签', async ({ page }) => {
    await page.goto('/tags')
    
    // 等待标签列表加载
    await page.waitForSelector('.tag-item', { timeout: 5000 })
    
    const tags = page.locator('.tag-item')
    await expect(tags).not.toHaveCount(0)
  })

  test('点击标签应该筛选文章', async ({ page }) => {
    await page.goto('/tags')
    
    // 等待标签列表加载
    await page.waitForSelector('.tag-item', { timeout: 5000 })
    
    const firstTag = page.locator('.tag-item').first()
    await firstTag.click()
    
    // 应该跳转到标签文章列表
    await expect(page).toHaveURL(/\/tags\/.+/)
  })
})

test.describe('关于页面', () => {
  test('应该显示关于信息', async ({ page }) => {
    await page.goto('/about')
    
    // 等待关于页面加载
    await page.waitForSelector('.about-content', { timeout: 5000 })
    
    const content = page.locator('.about-content')
    await expect(content).toBeVisible()
  })
})
