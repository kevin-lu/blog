# 首页标签筛选功能实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 在首页搜索栏下方添加标签筛选区，移除独立的标签页面

**架构：** 
1. 在 Home.vue 的搜索栏下方添加标签筛选组件
2. 创建 TagFilter 组件，展示所有标签并支持点击筛选
3. 移除侧边栏中的标签卡片（Tags Card）
4. 删除独立的 Tags.vue 页面及相关路由

**技术栈：** Vue 3, TypeScript, Naive UI

---

## 文件结构

**修改的文件：**
- `frontend/src/views/blog/Home.vue` - 添加标签筛选区
- `frontend/src/components/article/Sidebar.vue` - 移除标签卡片
- `frontend/src/router/index.ts` - 移除标签页面路由

**创建的文件：**
- `frontend/src/components/article/TagFilter.vue` - 标签筛选组件

**删除的文件：**
- `frontend/src/views/blog/Tags.vue` - 独立标签页面

---

### 任务 1：创建 TagFilter 组件

**文件：**
- 创建：`frontend/src/components/article/TagFilter.vue`

- [ ] **步骤 1：创建组件基础结构**

```vue
<template>
  <div class="tag-filter">
    <div class="tag-list">
      <n-tag
        v-for="tag in tags"
        :key="tag.id"
        :bordered="false"
        round
        checkable
        :checked="activeTag === tag.slug"
        @click="handleTagClick(tag.slug)"
      >
        {{ tag.name }}
      </n-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { Tag } from '@/types'
import { tagApi } from '@/api'

const router = useRouter()
const route = useRoute()

const tags = ref<Tag[]>([])
const activeTag = ref('')

const handleTagClick = (slug: string) => {
  if (activeTag.value === slug) {
    // 取消选中
    const newQuery = { ...route.query }
    delete newQuery.tag
    router.push({ query: newQuery })
  } else {
    // 选中
    router.push({
      query: {
        ...route.query,
        tag: slug,
        page: '1',
      },
    })
  }
}

onMounted(async () => {
  try {
    const response = await tagApi.getList()
    tags.value = response.data
  } catch (error) {
    console.error('Failed to load tags:', error)
  }
  
  // 从路由获取当前选中的标签
  if (route.query.tag) {
    activeTag.value = route.query.tag as string
  }
})
</script>

<style scoped>
.tag-filter {
  margin-bottom: 24px;
  padding: 16px 0;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-list .n-tag {
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(24, 160, 88, 0.08);
  color: #18a058;
}

.tag-list .n-tag:hover {
  transform: scale(1.05);
  background: rgba(24, 160, 88, 0.15);
}

.tag-list .n-tag.n-tag--checked {
  background: #18a058;
  color: white;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/components/article/TagFilter.vue
git commit -m "feat: add tag filter component"
```

---

### 任务 2：在 Home.vue 中集成标签筛选

**文件：**
- 修改：`frontend/src/views/blog/Home.vue`

- [ ] **步骤 1：导入 TagFilter 组件**

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { SearchOutline } from '@vicons/ionicons5'
import ArticleList from '@/components/article/ArticleList.vue'
import Sidebar from '@/components/article/Sidebar.vue'
import TagFilter from '@/components/article/TagFilter.vue'  // 新增

// ... 其他代码
</script>
```

- [ ] **步骤 2：在模板中添加 TagFilter**

```vue
<template>
  <div class="home-page">
    <div class="home-content">
      <div class="main-content">
        <!-- Search Bar -->
        <div class="search-bar">
          <n-input
            v-model:value="searchQuery"
            placeholder="搜索文章..."
            round
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <n-icon :component="SearchOutline" />
            </template>
            <template #suffix>
              <n-button text type="primary" @click="handleSearch">
                搜索
              </n-button>
            </template>
          </n-input>
        </div>

        <!-- Tag Filter (新增) -->
        <TagFilter />

        <!-- Article List -->
        <ArticleList />
      </div>

      <!-- Sidebar -->
      <aside class="sidebar">
        <Sidebar />
      </aside>
    </div>
  </div>
</template>
```

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/views/blog/Home.vue
git commit -m "feat: integrate tag filter in home page"
```

---

### 任务 3：移除侧边栏的标签卡片

**文件：**
- 修改：`frontend/src/components/article/Sidebar.vue`

- [ ] **步骤 1：移除标签卡片模板**

删除以下部分：
```vue
<!-- Tags -->
<n-card class="tags-card" title="标签" content-style="padding: 16px;">
  <div class="tag-cloud">
    <n-tag
      v-for="tag in tags"
      :key="tag.id"
      :bordered="false"
      round
      checkable
      :checked="activeTag === tag.slug"
      @click="goToTag(tag.slug)"
    >
      {{ tag.name }}
    </n-tag>
  </div>
</n-card>
```

- [ ] **步骤 2：清理相关代码**

删除：
```typescript
const activeTag = ref('')

const goToTag = (slug: string) => {
  router.push(`/tags/${slug}`)
}

// 在 onMounted 中删除：
if (route.params.name && route.path.includes('/tags/')) {
  activeTag.value = route.params.name as string
}
```

- [ ] **步骤 3：清理样式**

删除：
```css
.tags-card :deep(.n-card__header) {
  font-size: 18px;
  font-weight: 600;
  color: #18a058;
  padding: 16px 20px !important;
  border-bottom: 2px solid rgba(24, 160, 88, 0.1);
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-cloud .n-tag {
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(24, 160, 88, 0.08);
  color: #18a058;
}

.tag-cloud .n-tag:hover {
  transform: scale(1.05);
  background: rgba(24, 160, 88, 0.15);
}

.tag-cloud .n-tag.n-tag--checked {
  background: #18a058;
  color: white;
}
```

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/components/article/Sidebar.vue
git commit -m "refactor: remove tags card from sidebar"
```

---

### 任务 4：删除标签页面和路由

**文件：**
- 删除：`frontend/src/views/blog/Tags.vue`
- 修改：`frontend/src/router/index.ts`

- [ ] **步骤 1：检查路由配置**

```bash
# 查看路由配置中关于 tags 的路由
grep -n "tags" frontend/src/router/index.ts
```

- [ ] **步骤 2：移除标签页面路由**

在路由配置中删除：
```typescript
{
  path: '/tags',
  name: 'Tags',
  component: () => import('@/views/blog/Tags.vue'),
},
{
  path: '/tags/:name',
  name: 'TagPosts',
  component: () => import('@/views/blog/TagPosts.vue'),
},
```

- [ ] **步骤 3：删除 Tags.vue 文件**

```bash
rm frontend/src/views/blog/Tags.vue
```

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/router/index.ts
git rm frontend/src/views/blog/Tags.vue
git commit -m "chore: remove tags page and routes"
```

---

### 任务 5：测试验证

**测试步骤：**

- [ ] **步骤 1：启动开发服务器**

```bash
cd frontend
npm run dev
```

- [ ] **步骤 2：访问首页**

访问 http://localhost:5175/
- 验证搜索栏下方显示标签筛选区
- 验证所有标签正确显示
- 验证侧边栏不再显示标签卡片

- [ ] **步骤 3：测试标签筛选**

1. 点击任意标签
2. 验证 URL 变为 `/?tag=xxx&page=1`
3. 验证文章列表只显示该标签的文章
4. 验证选中的标签高亮显示

- [ ] **步骤 4：测试取消筛选**

1. 点击已选中的标签
2. 验证 URL 中的 tag 参数被移除
3. 验证文章列表恢复显示所有文章

- [ ] **步骤 5：测试组合筛选**

1. 先选择分类
2. 再选择标签
3. 验证 URL 包含 category 和 tag 参数
4. 验证筛选结果正确

- [ ] **步骤 6：测试响应式**

1. 调整浏览器窗口大小
2. 验证标签筛选区在不同屏幕尺寸下正常显示

---

## 自检

**规格覆盖度检查：**
- ✅ 创建 TagFilter 组件 - 任务 1
- ✅ 在 Home.vue 集成 - 任务 2
- ✅ 移除侧边栏标签卡片 - 任务 3
- ✅ 删除标签页面和路由 - 任务 4
- ✅ 测试验证 - 任务 5

**占位符扫描：** 无占位符

**类型一致性：** 所有类型引用与现有代码一致

---

计划已完成并保存到 `docs/superpowers/plans/2026-05-13-home-tag-filter.md`。两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

选哪种方式？
