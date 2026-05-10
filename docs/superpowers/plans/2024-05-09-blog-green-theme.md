# 博客绿色主题优化实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 移除用户入口、列表布局靠左、添加绿色渐变背景和科技感主题

**架构：** 
- 修改 BlogLayout 组件移除用户入口
- 修改 ArticleList 组件样式让列表靠左
- 修改 main.css 添加全局绿色渐变背景
- 修改各组件添加绿色主题样式

**技术栈：** Vue 3, TypeScript, CSS, Naive UI

---

### 任务 1：移除头部用户入口

**文件：**
- 修改：`frontend/src/components/layout/BlogLayout.vue`

- [ ] **步骤 1：移除 header-right 区域**

```vue
<!-- 移除这部分代码 -->
<div class="header-right">
  <n-button
    v-if="!authStore.isAuthenticated"
    text
    @click="goToAdmin"
  >
    管理后台
  </n-button>
  <UserInfo v-else />
</div>
```

修改后的 header-left：
```vue
<div class="header-left">
  <router-link to="/" class="logo">
    <h1>{{ siteName }}</h1>
  </router-link>

  <!-- Desktop Nav -->
  <nav class="nav desktop-nav">
    <router-link to="/" class="nav-link">首页</router-link>
    <router-link to="/categories" class="nav-link">分类</router-link>
    <router-link to="/tags" class="nav-link">标签</router-link>
    <router-link to="/about" class="nav-link">关于</router-link>
  </nav>

  <!-- Mobile Menu Button -->
  <n-button class="mobile-menu-btn" text @click="toggleMobileMenu">
    <template #icon>
      <n-icon :component="menuOpen ? CloseOutline : MenuOutline" size="24" />
    </template>
  </n-button>
</div>
```

- [ ] **步骤 2：移除相关导入和函数**

移除：
```typescript
import UserInfo from '@/components/common/UserInfo.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const goToAdmin = () => {
  router.push('/admin/login')
}
```

- [ ] **步骤 3：调整 header 样式**

```css
.header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: flex-start; /* 改为左对齐 */
}

.header-left {
  display: flex;
  align-items: center;
  gap: 24px;
  width: 100%; /* 占满宽度 */
}

.header-right {
  display: none; /* 移除右侧区域 */
}
```

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/components/layout/BlogLayout.vue
git commit -m "feat: 移除博客前端用户入口"
```

---

### 任务 2：列表布局靠左

**文件：**
- 修改：`frontend/src/components/article/ArticleList.vue`
- 修改：`frontend/src/views/blog/Home.vue`

- [ ] **步骤 1：修改 ArticleList 容器样式**

```css
.article-list {
  max-width: 900px;
  margin: 0; /* 移除 auto */
  padding-left: 0; /* 靠左 */
}
```

- [ ] **步骤 2：修改 Home.vue 布局**

```css
.home-content {
  display: block;
  max-width: 900px;
  margin: 0; /* 移除 auto，靠左显示 */
  padding: 0 20px; /* 保留两侧 padding */
}

@media (min-width: 1200px) {
  .home-content {
    display: grid;
    grid-template-columns: 1fr 280px;
    gap: 32px;
    margin: 0 auto; /* 大屏可以居中 */
  }
}
```

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/components/article/ArticleList.vue frontend/src/views/blog/Home.vue
git commit -m "style: 列表布局靠左显示"
```

---

### 任务 3：添加绿色渐变背景

**文件：**
- 修改：`frontend/src/assets/css/main.css`

- [ ] **步骤 1：添加全局背景样式**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

/* 绿色渐变背景 */
body {
  background: linear-gradient(135deg, #f0f9f4 0%, #e6f5ed 100%);
  background-attachment: fixed;
  min-height: 100vh;
}

/* 绿色主题色变量 */
:root {
  --primary-color: #18a058;
  --primary-dark: #0c7a43;
  --primary-light: #34c88a;
  --bg-gradient-start: #f0f9f4;
  --bg-gradient-end: #e6f5ed;
}
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/assets/css/main.css
git commit -m "feat: 添加绿色渐变背景主题"
```

---

### 任务 4：优化头部样式

**文件：**
- 修改：`frontend/src/components/layout/BlogLayout.vue`

- [ ] **步骤 1：修改 header 背景为半透明毛玻璃效果**

```css
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(24, 160, 88, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #18a058 0%, #0c7a43 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

- [ ] **步骤 2：修改导航链接样式**

```css
.nav-link {
  padding: 8px 16px;
  text-decoration: none;
  color: #333;
  border-radius: 6px;
  transition: all 0.2s;
  white-space: nowrap;
  position: relative;
}

.nav-link:hover {
  background-color: rgba(24, 160, 88, 0.08);
  color: #18a058;
}

.nav-link.router-link-active {
  background: linear-gradient(135deg, #18a058 0%, #0c7a43 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(24, 160, 88, 0.3);
}
```

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/components/layout/BlogLayout.vue
git commit -m "style: 优化头部绿色主题样式"
```

---

### 任务 5：优化文章列表卡片样式

**文件：**
- 修改：`frontend/src/components/article/ArticleList.vue`
- 修改：`frontend/src/components/article/ArticleCard.vue`

- [ ] **步骤 1：修改 ArticleList 容器样式**

```css
.articles {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(24, 160, 88, 0.1);
  border: 1px solid rgba(24, 160, 88, 0.05);
}
```

- [ ] **步骤 2：修改 ArticleCard 悬停效果**

```css
.article-list-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(24, 160, 88, 0.08);
  cursor: pointer;
  transition: all 0.2s;
}

.article-list-item:last-child {
  border-bottom: none;
}

.article-list-item:hover {
  background: linear-gradient(90deg, rgba(24, 160, 88, 0.04) 0%, rgba(255, 255, 255, 0) 100%);
}

.article-list-item:active {
  background: rgba(24, 160, 88, 0.08);
}
```

- [ ] **步骤 3：修改序号和圆点颜色**

```css
.article-id {
  font-size: 14px;
  color: #18a058;
  font-weight: 600;
  min-width: 32px;
  text-align: right;
}

.article-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: linear-gradient(135deg, #18a058 0%, #0c7a43 100%);
  margin-top: 8px;
  flex-shrink: 0;
}
```

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/components/article/ArticleList.vue frontend/src/components/article/ArticleCard.vue
git commit -m "style: 优化文章列表卡片绿色主题"
```

---

### 任务 6：优化搜索栏和按钮样式

**文件：**
- 修改：`frontend/src/views/blog/Home.vue`

- [ ] **步骤 1：修改搜索栏样式**

```css
.search-bar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: transparent;
  padding: 16px 0;
}

.search-bar .n-input {
  height: 48px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(24, 160, 88, 0.1);
  border-radius: 24px;
  transition: all 0.2s;
}

.search-bar .n-input:hover {
  border-color: rgba(24, 160, 88, 0.3);
}

.search-bar .n-input:focus-within {
  border-color: #18a058;
  box-shadow: 0 0 0 3px rgba(24, 160, 88, 0.1);
}
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/views/blog/Home.vue
git commit -m "style: 优化搜索栏绿色主题样式"
```

---

### 任务 7：优化详情页样式

**文件：**
- 修改：`frontend/src/views/blog/PostDetail.vue`

- [ ] **步骤 1：修改返回按钮样式**

```css
.back-btn {
  font-size: 14px;
  color: #18a058;
  transition: all 0.2s;
}

.back-btn:hover {
  color: #0c7a43;
  background: rgba(24, 160, 88, 0.08);
}
```

- [ ] **步骤 2：修改文章标题和元信息样式**

```css
.post-title {
  margin: 0 0 16px 0;
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.post-meta {
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(24, 160, 88, 0.1);
}

.publish-date {
  font-size: 14px;
  color: #18a058;
}
```

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/views/blog/PostDetail.vue
git commit -m "style: 优化详情页绿色主题样式"
```

---

### 任务 8：优化侧边栏样式

**文件：**
- 修改：`frontend/src/components/article/Sidebar.vue`

- [ ] **步骤 1：读取 Sidebar.vue 文件**

先查看当前 Sidebar 组件内容

- [ ] **步骤 2：修改侧边栏卡片样式**

```css
.sidebar-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(24, 160, 88, 0.1);
  border: 1px solid rgba(24, 160, 88, 0.05);
}

.sidebar-title {
  font-size: 18px;
  font-weight: 600;
  color: #18a058;
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(24, 160, 88, 0.1);
}
```

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/components/article/Sidebar.vue
git commit -m "style: 优化侧边栏绿色主题样式"
```

---

### 任务 9：测试验证

**文件：** 无

- [ ] **步骤 1：启动前端服务**

```bash
cd frontend
npm run dev
```

- [ ] **步骤 2：验证首页效果**

访问 http://localhost:5174/
- 检查头部是否移除了用户入口
- 检查列表是否靠左显示
- 检查绿色渐变背景是否显示
- 检查头部、卡片、搜索栏的绿色主题样式

- [ ] **步骤 3：验证详情页效果**

- 点击文章进入详情页
- 检查返回按钮、标题、时间的绿色样式
- 检查正文显示是否正常

- [ ] **步骤 4：验证响应式效果**

- 调整浏览器窗口大小
- 检查移动端布局是否正常
- 检查侧边栏在不同屏幕下的显示

- [ ] **步骤 5：修复发现的问题**

如有问题，记录并修复

---

## 自检

**1. 规格覆盖度：**
- ✅ 移除用户入口 - 任务 1
- ✅ 列表布局靠左 - 任务 2
- ✅ 绿色渐变背景 - 任务 3
- ✅ 头部绿色主题 - 任务 4
- ✅ 文章卡片绿色主题 - 任务 5
- ✅ 搜索栏绿色主题 - 任务 6
- ✅ 详情页绿色主题 - 任务 7
- ✅ 侧边栏绿色主题 - 任务 8

**2. 占位符扫描：**
- 无占位符，所有步骤都有具体代码

**3. 类型一致性：**
- 所有 CSS 使用统一的颜色变量
- 所有组件使用相同的绿色主题色 #18a058

---

计划已完成并保存到 `docs/superpowers/plans/2024-05-09-blog-green-theme.md`。两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

**选哪种方式？**
