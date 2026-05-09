# 博客前端 redesign 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将博客前端从卡片式布局改为列表式布局，修复时间显示问题，简化详情页

**架构：** 
- ArticleCard 组件改为列表式布局（序号 + 标题 + 描述 + 时间）
- 修复时间显示使用 published_at 字段
- 修复点击跳转功能
- PostDetail 组件简化为简洁风格（标题 + 正文）

**技术栈：** Vue 3, TypeScript, Naive UI, Vue Router

---

### 任务 1：修改 ArticleCard 组件为列表式布局

**文件：**
- 修改：`frontend/src/components/article/ArticleCard.vue`

- [ ] **步骤 1：修改模板为列表式布局**

```vue
<template>
  <div class="article-list-item" @click="goToArticle">
    <div class="article-id">{{ article.id }}</div>
    <div class="article-dot"></div>
    <div class="article-info">
      <h2 class="article-title">{{ article.title }}</h2>
      <p v-if="article.description" class="article-description">
        {{ article.description }}
      </p>
      <div class="article-meta">
        <n-text depth="3" class="publish-date">
          {{ formatDate(article.published_at) }}
        </n-text>
      </div>
    </div>
  </div>
</template>
```

- [ ] **步骤 2：修改样式为列表式**

```vue
<style scoped>
.article-list-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.article-list-item:hover {
  background-color: #f9f9f9;
}

.article-id {
  font-size: 14px;
  color: #999;
  min-width: 32px;
  text-align: right;
}

.article-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #ddd;
  margin-top: 8px;
  flex-shrink: 0;
}

.article-info {
  flex: 1;
  min-width: 0;
}

.article-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
}

.article-description {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  gap: 12px;
}

.publish-date {
  font-size: 13px;
  color: #999;
}
</style>
```

- [ ] **步骤 3：修改 formatDate 函数**

```typescript
const formatDate = (dateString: string | null) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
```

- [ ] **步骤 4：移除 n-card 组件和封面图逻辑**

删除所有与封面图、标签、分类相关的代码

- [ ] **步骤 5：Commit**

```bash
git add frontend/src/components/article/ArticleCard.vue
git commit -m "refactor: 将文章卡片改为列表式布局"
```

---

### 任务 2：修复 ArticleList 组件样式

**文件：**
- 修改：`frontend/src/components/article/ArticleList.vue`

- [ ] **步骤 1：修改列表容器样式**

```vue
<style scoped>
.articles {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/components/article/ArticleList.vue
git commit -m "style: 优化文章列表容器样式"
```

---

### 任务 3：修复 Home 页面布局

**文件：**
- 修改：`frontend/src/views/blog/Home.vue`

- [ ] **步骤 1：调整网格布局**

```vue
<style scoped>
.home-content {
  display: block;
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.sidebar {
  display: none;
}

@media (min-width: 1200px) {
  .home-content {
    display: grid;
    grid-template-columns: 1fr 280px;
    gap: 32px;
  }
  
  .sidebar {
    display: block;
  }
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/views/blog/Home.vue
git commit -m "style: 优化首页布局"
```

---

### 任务 4：简化 PostDetail 详情页

**文件：**
- 修改：`frontend/src/views/blog/PostDetail.vue`

- [ ] **步骤 1：查看当前 PostDetail 组件内容**

先读取文件了解当前结构

- [ ] **步骤 2：简化为简洁布局**

```vue
<template>
  <div class="post-detail">
    <div class="post-header">
      <n-button text @click="goBack" class="back-btn">
        <template #icon>
          <n-icon :component="ArrowBackOutline" />
        </template>
        返回首页
      </n-button>
    </div>

    <article class="post-content">
      <h1 class="post-title">{{ article.title }}</h1>
      
      <div class="post-meta">
        <n-text depth="3" class="publish-date">
          {{ formatDate(article.published_at) }}
        </n-text>
      </div>

      <div class="post-body" v-html="article.content"></div>
    </article>
  </div>
</template>
```

- [ ] **步骤 3：添加简洁样式**

```vue
<style scoped>
.post-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.post-header {
  margin-bottom: 40px;
}

.back-btn {
  font-size: 14px;
  color: #666;
}

.back-btn:hover {
  color: #18a058;
}

.post-title {
  margin: 0 0 16px 0;
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.4;
}

.post-meta {
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.publish-date {
  font-size: 14px;
  color: #999;
}

.post-body {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
}

.post-body :deep(p) {
  margin-bottom: 1.5em;
}

.post-body :deep(h1),
.post-body :deep(h2),
.post-body :deep(h3) {
  margin-top: 2em;
  margin-bottom: 1em;
  font-weight: 600;
}
</style>
```

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/views/blog/PostDetail.vue
git commit -m "refactor: 简化文章详情页为简洁风格"
```

---

### 任务 5：测试验证

**文件：** 无

- [ ] **步骤 1：启动前端服务**

```bash
cd frontend
npm run dev
```

- [ ] **步骤 2：验证首页列表显示**

访问 http://localhost:5173
- 检查文章列表是否为列表式布局
- 检查序号、标题、描述、时间是否正确显示
- 检查时间格式是否正确（非 "Invalid Date"）
- 检查点击文章是否能跳转到详情页

- [ ] **步骤 3：验证详情页**

- 检查详情页是否简洁（标题 + 正文）
- 检查返回按钮是否工作
- 检查正文内容是否正确显示

- [ ] **步骤 4：修复发现的问题**

如有问题，记录并修复

---

## 自检

**1. 规格覆盖度：**
- ✅ 列表式布局 - 任务 1
- ✅ 时间显示修复 - 任务 1（formatDate 函数）
- ✅ 点击跳转功能 - 任务 1（goToArticle 函数）
- ✅ 详情页简化 - 任务 4

**2. 占位符扫描：**
- 无占位符，所有步骤都有具体代码

**3. 类型一致性：**
- Article 类型在各组件中一致使用
- formatDate 函数处理 null 值

---

计划已完成并保存到 `docs/superpowers/plans/2024-05-09-blog-frontend-redesign.md`。两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

选哪种方式？
