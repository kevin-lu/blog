# 前端测试指南

本文档介绍如何运行前端项目的测试。

## 测试框架

- **单元测试**: Vitest
- **E2E 测试**: Playwright
- **组件测试**: @vue/test-utils

## 安装依赖

首次使用需要安装测试依赖：

```bash
# 安装单元测试依赖
npm install --save-dev vitest @vitejs/plugin-vue @vue/test-utils jsdom @types/jsdom @vitest/coverage-v8 @pinia/testing

# 安装 E2E 测试依赖
npm install --save-dev @playwright/test
npx playwright install
```

## 运行单元测试

### 运行所有单元测试

```bash
npm run test
```

### 监听模式（自动重新运行）

```bash
npm run test -- --watch
```

### 生成测试覆盖率报告

```bash
npm run test:coverage
```

覆盖率报告将生成在 `coverage/` 目录下，打开 `coverage/index.html` 查看 HTML 报告。

### 使用 UI 界面运行

```bash
npm run test:ui
```

## 运行 E2E 测试

### 安装 Playwright 浏览器

首次使用需要安装浏览器：

```bash
npx playwright install
```

### 运行所有 E2E 测试

```bash
npm run test:e2e
```

### 使用 UI 界面运行

```bash
npm run test:e2e:ui
```

### 在有头模式下运行（显示浏览器）

```bash
npm run test:e2e:headed
```

### 运行特定测试文件

```bash
npm run test:e2e -- e2e/blog.spec.ts
```

### 运行特定测试用例

```bash
npm run test:e2e -- --grep "博客首页"
```

## 测试文件组织

```
frontend/
├── src/
│   ├── tests/
│   │   ├── setup.ts              # 测试配置
│   │   └── unit/
│   │       ├── components/       # 组件测试
│   │       ├── stores/           # Store 测试
│   │       ├── utils/            # 工具函数测试
│   │       └── views/            # 页面测试
│   └── ...
├── e2e/
│   ├── blog.spec.ts              # 博客 E2E 测试
│   ├── admin.spec.ts             # 管理后台 E2E 测试
│   └── helpers.ts                # E2E 测试辅助工具
├── vitest.config.ts              # Vitest 配置
├── playwright.config.ts          # Playwright 配置
└── package.json
```

## 编写测试

### 组件测试示例

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  it('应该正确渲染', () => {
    const wrapper = mount(MyComponent, {
      props: {
        title: '测试标题'
      }
    })
    
    expect(wrapper.find('.title').text()).toBe('测试标题')
  })
})
```

### Store 测试示例

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMyStore } from '@/stores/my'

describe('MyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('应该初始化状态', () => {
    const store = useMyStore()
    expect(store.count).toBe(0)
  })
})
```

### E2E 测试示例

```typescript
import { test, expect } from '@playwright/test'

test('应该显示首页', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/博客/)
})
```

## 测试辅助工具

### E2E 测试辅助函数

在 `e2e/helpers.ts` 中提供了常用的 E2E 测试辅助函数：

```typescript
import { login, logout, createTestArticle } from './helpers'

test('测试登录', async ({ page }) => {
  await login(page)
  // 执行需要登录的操作
})

test('创建文章', async ({ page }) => {
  await login(page)
  await createTestArticle(page, '测试文章', '内容')
})
```

## 常见问题

### 1. 测试运行时提示模块找不到

确保已安装所有依赖：

```bash
npm install
```

### 2. Playwright 浏览器安装失败

尝试使用国内镜像：

```bash
PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright npx playwright install
```

### 3. 测试覆盖率报告为空

确保 `vitest.config.ts` 中正确配置了覆盖率选项，并且测试文件覆盖了所有源代码。

### 4. E2E 测试超时

在 `playwright.config.ts` 中增加超时时间：

```typescript
export default defineConfig({
  timeout: 60 * 1000, // 60 秒
})
```

## 最佳实践

1. **单元测试应该快速且独立** - 不依赖外部服务
2. **使用 Mock 数据** - 避免依赖真实 API
3. **测试用户行为** - 而不是实现细节
4. **保持测试简洁** - 每个测试只验证一个功能点
5. **使用有意义的测试名称** - 描述测试的目的
6. **定期运行测试** - 在 CI/CD 中集成测试

## CI/CD 集成

在 GitHub Actions 中运行测试：

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright browsers
        run: npx playwright install --with-deps
      
      - name: Run unit tests
        run: npm run test:coverage
      
      - name: Run E2E tests
        run: npm run test:e2e
```

## 参考资源

- [Vitest 文档](https://vitest.dev/)
- [Playwright 文档](https://playwright.dev/)
- [@vue/test-utils 文档](https://test-utils.vuejs.org/)
- [Testing Library](https://testing-library.com/)
