import { config } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import naive from 'naive-ui'
import { vi } from 'vitest'
import { createTestingPinia } from '@pinia/testing'

// 创建 Router 实例
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: { template: '<div>Home</div>' },
    },
    {
      path: '/posts/:slug',
      name: 'post-detail',
      component: { template: '<div>Post Detail</div>' },
    },
    {
      path: '/categories',
      name: 'categories',
      component: { template: '<div>Categories</div>' },
    },
    {
      path: '/tags',
      name: 'tags',
      component: { template: '<div>Tags</div>' },
    },
    {
      path: '/about',
      name: 'about',
      component: { template: '<div>About</div>' },
    },
  ],
})

// 全局配置
config.global.plugins = [
  createTestingPinia({
    createSpy: vi.fn,
    stubActions: false,
  }),
  router,
  naive,
]
config.global.stubs = {
  RouterLink: true,
  NIcon: true,
  NButton: true,
  NInput: true,
  NCard: true,
  NSpace: true,
  NTag: true,
  NSpin: true,
  NPagination: true,
  NDataList: true,
  NBreadcrumb: true,
  NBreadcrumbItem: true,
  NGrid: true,
  NGi: true,
}

// 全局 mock
global.fetch = vi.fn()
window.matchMedia = vi.fn().mockImplementation((query) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}))
