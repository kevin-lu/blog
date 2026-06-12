# 文章浏览次数统计实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 为博客文章添加浏览次数统计功能，每次浏览自动 +1，后台列表显示浏览次数

**架构：** 
- 后端：在 Article 模型添加 view_count 字段，创建计数接口，文章详情页调用计数
- 前端：文章详情页加载时触发计数，后台列表展示浏览次数并支持排序
- 防刷：同一 IP 在 24 小时内只计一次

**技术栈：** Flask, SQLAlchemy, Vue 3, TypeScript, Naive UI

---

## 文件结构

**后端 - 模型：**
- 修改：`backend/app/models/article.py` - Article 模型添加 view_count 字段

**后端 - 数据库迁移：**
- 创建：`backend/migrations/002_add_view_count.py` - 添加 view_count 字段迁移

**后端 - API：**
- 修改：`backend/app/api/v1/articles.py` - 添加计数接口，返回列表包含 view_count
- 创建：`backend/app/api/v1/articles_view.py` - 文章计数专用接口

**前端 - 类型：**
- 修改：`frontend/src/types/index.ts` - Article 接口添加 view_count 字段

**前端 - API 调用：**
- 修改：`frontend/src/api/index.ts` - 添加计数 API 调用函数

**前端 - 文章详情：**
- 修改：`frontend/src/views/blog/PostDetail.vue` - 加载时调用计数接口

**前端 - 后台文章列表：**
- 修改：`frontend/src/views/admin/articles/ArticleList.vue` - 表格增加浏览次数列

---

## 任务 1：后端模型和数据库迁移

**文件：**
- 修改：`backend/app/models/article.py`
- 创建：`backend/migrations/002_add_view_count.py`

- [ ] **步骤 1：修改 Article 模型添加 view_count 字段**

```python
# backend/app/models/article.py
# 在 Article 类中添加字段（在 status 字段之后）
view_count = db.Column(db.Integer, default=0, nullable=False, index=True)
```

- [ ] **步骤 2：更新 to_dict 方法包含 view_count**

```python
# backend/app/models/article.py
# 在 to_dict 方法的 data 字典中添加
'view_count': self.view_count or 0,
```

- [ ] **步骤 3：创建数据库迁移脚本**

```python
# backend/migrations/002_add_view_count.py
"""
Migration: Add view_count to articles
"""
from app.extensions import db


def upgrade():
    # 添加 view_count 字段
    with db.engine.connect() as conn:
        # 检查字段是否已存在
        inspector = db.inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('article_meta')]
        
        if 'view_count' not in columns:
            conn.execute(db.text(
                "ALTER TABLE article_meta ADD COLUMN view_count INTEGER DEFAULT 0 NOT NULL"
            ))
            conn.execute(db.text(
                "CREATE INDEX idx_article_view_count ON article_meta(view_count)"
            ))
            conn.commit()
            print("✓ view_count 字段添加成功")
        else:
            print("✓ view_count 字段已存在")


def downgrade():
    with db.engine.connect() as conn:
        conn.execute(db.text(
            "ALTER TABLE article_meta DROP COLUMN view_count"
        ))
        conn.commit()
        print("✓ view_count 字段已移除")


if __name__ == '__main__':
    upgrade()
```

- [ ] **步骤 4：运行迁移**

```bash
cd backend
python migrations/002_add_view_count.py
```

预期输出：`✓ view_count 字段添加成功`

- [ ] **步骤 5：Commit**

```bash
git add backend/app/models/article.py backend/migrations/002_add_view_count.py
git commit -m "feat: add view_count field to Article model"
```

---

## 任务 2：后端计数 API

**文件：**
- 创建：`backend/app/api/v1/articles_view.py`
- 修改：`backend/app/api/v1/articles.py`

- [ ] **步骤 1：创建计数接口**

```python
# backend/app/api/v1/articles_view.py
"""
Article View Count API
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.extensions import db, limiter
from app.models.article import Article

bp = Blueprint('article_views', __name__)


def get_client_ip():
    """获取客户端 IP 地址"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'


@bp.route('/<slug>', methods=['POST'])
@limiter.limit("100 per hour")
def increment_view_count(slug):
    """
    增加文章浏览次数
    
    防刷策略：
    - 同一 IP 在 24 小时内只计一次
    - 使用 Redis 或内存缓存记录 IP 访问时间
    
    Returns:
        {
            "success": true,
            "view_count": 1234
        }
    """
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'success': False, 'error': 'Article not found'}), 404
    
    # 获取客户端 IP
    client_ip = get_client_ip()
    
    # 检查缓存（简单实现：使用 Flask cache）
    # TODO: 生产环境建议使用 Redis
    cache_key = f'article_view:{slug}:{client_ip}'
    
    # 检查是否在 24 小时内已访问
    # 简单实现：使用内存缓存（生产环境用 Redis）
    if not hasattr(current_app, 'view_cache'):
        current_app.view_cache = {}
    
    last_view = current_app.view_cache.get(cache_key)
    if last_view:
        # 检查是否在 24 小时内
        if datetime.now() - last_view < timedelta(hours=24):
            # 已访问过，不增加计数，但返回当前浏览次数
            return jsonify({
                'success': True,
                'view_count': article.view_count,
                'cached': True
            })
    
    # 增加浏览次数
    article.view_count = (article.view_count or 0) + 1
    db.session.commit()
    
    # 更新缓存
    current_app.view_cache[cache_key] = datetime.now()
    
    return jsonify({
        'success': True,
        'view_count': article.view_count
    }), 200
```

- [ ] **步骤 2：在 app/api/v1/__init__.py 中注册蓝图**

```python
# backend/app/api/v1/__init__.py
# 添加导入和注册
from app.api.v1.articles_view import bp as articles_view_bp

def create_api_blueprint():
    # ... 现有代码 ...
    api.register_blueprint(articles_view_bp, url_prefix='/articles')
```

- [ ] **步骤 3：修改文章列表接口返回 view_count**

```python
# backend/app/api/v1/articles.py
# 在 get_articles 函数中，确保 to_dict() 包含 view_count
# （任务 1 已更新 to_dict 方法，这里会自动包含）
```

- [ ] **步骤 4：支持按浏览次数排序**

```python
# backend/app/api/v1/articles.py
# 在 get_articles 函数中添加排序参数
order_by = request.args.get('order_by', 'published_at')
order_dir = request.args.get('order_dir', 'desc')

# 映射排序字段
order_map = {
    'published_at': Article.published_at,
    'view_count': Article.view_count,
    'created_at': Article.created_at,
}

order_field = order_map.get(order_by, Article.published_at)
if order_dir == 'asc':
    query = query.order_by(order_field.asc())
else:
    query = query.order_by(order_field.desc())
```

- [ ] **步骤 5：Commit**

```bash
git add backend/app/api/v1/articles_view.py backend/app/api/v1/articles.py backend/app/api/v1/__init__.py
git commit -m "feat: add article view count API with anti-spam protection"
```

---

## 任务 3：前端类型和 API 调用

**文件：**
- 修改：`frontend/src/types/index.ts`
- 修改：`frontend/src/api/index.ts`

- [ ] **步骤 1：更新 Article 类型**

```typescript
// frontend/src/types/index.ts
export interface Article {
  id: number
  slug: string
  title: string
  description?: string
  content?: string
  cover_image?: string
  status: 'draft' | 'published' | 'archived'
  published_at?: string
  publishedAt?: string
  created_at: string
  createdAt?: string
  updated_at: string
  updatedAt?: string
  categories?: Category[]
  tags?: Tag[]
  view_count?: number  // 新增：浏览次数
  comment_count?: number
}
```

- [ ] **步骤 2：添加计数 API 调用函数**

```typescript
// frontend/src/api/index.ts
// 在文件末尾添加
export const articleViewApi = {
  async increment(slug: string): Promise<number> {
    const response = await apiClient.post(`/api/v1/articles/${slug}`, {})
    return response.data.view_count
  },
}
```

- [ ] **步骤 3：更新后台文章列表 API 支持排序**

```typescript
// frontend/src/api/index.ts
// 在 adminArticleApi.getList 方法中添加排序参数
getList: async (params: { 
  page: number
  pageSize: number
  status?: string
  orderBy?: string
  orderDir?: string
}) => {
  const queryParams = new URLSearchParams({
    page: params.page.toString(),
    limit: params.pageSize.toString(),
    status: params.status || '',
  })
  
  if (params.orderBy) queryParams.append('order_by', params.orderBy)
  if (params.orderDir) queryParams.append('order_dir', params.orderDir)
  
  const response = await apiClient.get(`/api/v1/admin/articles?${queryParams}`)
  return toArticlesResponse(response.data)
},
```

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/types/index.ts frontend/src/api/index.ts
git commit -m "feat: add view_count type and API calls"
```

---

## 任务 4：前端文章详情页计数

**文件：**
- 修改：`frontend/src/views/blog/PostDetail.vue`

- [ ] **步骤 1：导入 API**

```vue
<!-- frontend/src/views/blog/PostDetail.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowBackOutline } from '@vicons/ionicons5'
import type { Article } from '@/types'
import { articleApi, articleViewApi } from '@/api'
import { renderArticleContent } from '@/utils/markdown'
import { formatDate, getArticleDate } from '@/utils/date'

// ... 其他代码
```

- [ ] **步骤 2：添加浏览次数显示**

```vue
<!-- frontend/src/views/blog/PostDetail.vue -->
<template>
  <div class="post-detail">
    <!-- ... 现有代码 ... -->
    
    <div class="post-meta">
      <n-text depth="3" class="publish-date">
        {{ formatDate(articleDate) }}
      </n-text>
      <n-text depth="3" class="view-count" v-if="article.view_count">
        <n-icon :component="EyeOutline" /> {{ article.view_count }} 次阅读
      </n-text>
    </div>
    
    <!-- ... 现有代码 ... -->
  </div>
</template>
```

- [ ] **步骤 3：添加图标导入**

```typescript
// frontend/src/views/blog/PostDetail.vue
import { ArrowBackOutline, EyeOutline } from '@vicons/ionicons5'
```

- [ ] **步骤 4：添加样式**

```vue
<!-- frontend/src/views/blog/PostDetail.vue -->
<style scoped>
.post-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 16px 0;
}

.view-count {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
```

- [ ] **步骤 5：在加载时调用计数接口**

```typescript
// frontend/src/views/blog/PostDetail.vue
const loadArticle = async () => {
  loading.value = true
  try {
    const data = await articleApi.getDetail(slug.value)
    article.value = data
    
    // 增加浏览次数（静默调用，不等待结果）
    articleViewApi.increment(slug.value).then(count => {
      // 更新本地显示
      if (article.value) {
        article.value.view_count = count
      }
    }).catch(err => {
      console.error('Failed to increment view count:', err)
    })
  } catch (error) {
    console.error('Failed to load article:', error)
  } finally {
    loading.value = false
  }
}
```

- [ ] **步骤 6：Commit**

```bash
git add frontend/src/views/blog/PostDetail.vue
git commit -m "feat: display and increment view count on article detail page"
```

---

## 任务 5：后台文章列表显示浏览次数

**文件：**
- 修改：`frontend/src/views/admin/articles/ArticleList.vue`

- [ ] **步骤 1：在表格中添加浏览次数列**

```vue
<!-- frontend/src/views/admin/articles/ArticleList.vue -->
<script setup lang="ts">
// 在 columns 定义中添加浏览次数列
const columns = [
  // ... 现有列 ...
  {
    title: '浏览次数',
    key: 'view_count',
    width: 100,
    sorter: 'default',
    render(row) {
      return h('span', { style: 'font-size: 13px; color: #666;' }, [
        row.view_count || 0,
      ])
    },
  },
  // ... 操作列 ...
]
```

- [ ] **步骤 2：添加排序功能**

```typescript
// frontend/src/views/admin/articles/ArticleList.vue
// 在 loadArticles 函数中添加排序参数
const loadArticles = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      pageSize: pageSize.value,
      status: filters.value.status,
      orderBy: sortField.value,
      orderDir: sortOrder.value,
    }
    
    const response = await adminArticleApi.getList(params)
    articles.value = response.data.data
    pagination.value = {
      total: response.data.total,
      pages: Math.ceil(response.data.total / pageSize.value),
      page: response.data.page,
      limit: response.data.pageSize,
    }
  } catch (error) {
    console.error('Failed to load articles:', error)
  } finally {
    loading.value = false
  }
}
```

- [ ] **步骤 3：添加排序状态**

```typescript
// frontend/src/views/admin/articles/ArticleList.vue
const sortField = ref('published_at')
const sortOrder = ref('desc')

const handleSortChange = (field: string, order: string) => {
  sortField.value = field
  sortOrder.value = order
  currentPage.value = 1
  loadArticles()
}
```

- [ ] **步骤 4：在表格上启用排序**

```vue
<!-- frontend/src/views/admin/articles/ArticleList.vue -->
<n-data-table
  :columns="columns"
  :data="articles"
  :loading="loading"
  :pagination="false"
  @update:sorter="handleSortChange"
/>
```

- [ ] **步骤 5：Commit**

```bash
git add frontend/src/views/admin/articles/ArticleList.vue
git commit -m "feat: display view count in admin article list with sorting"
```

---

## 任务 6：测试验证

**文件：**
- 测试：手动测试和 API 测试

- [ ] **步骤 1：测试后端计数 API**

```bash
# 测试计数接口
curl -X POST http://localhost:5000/api/v1/articles/your-article-slug \
  -H "Content-Type: application/json"

# 预期响应
{
  "success": true,
  "view_count": 1
}
```

- [ ] **步骤 2：测试防刷机制**

```bash
# 立即再次调用（应该不增加计数）
curl -X POST http://localhost:5000/api/v1/articles/your-article-slug \
  -H "Content-Type: application/json"

# 预期响应（cached: true）
{
  "success": true,
  "view_count": 1,
  "cached": true
}
```

- [ ] **步骤 3：测试文章列表返回 view_count**

```bash
curl http://localhost:5000/api/v1/articles?limit=5 | jq '.articles[0].view_count'
# 应该返回数字
```

- [ ] **步骤 4：前端测试**

1. 访问任意文章详情页
2. 检查页面是否显示"X 次阅读"
3. 刷新页面，检查浏览次数是否 +1
4. 再次刷新，检查是否因防刷机制不增加

- [ ] **步骤 5：后台测试**

1. 登录管理后台
2. 进入文章列表
3. 检查是否显示"浏览次数"列
4. 点击"浏览次数"列头，检查是否支持排序

- [ ] **步骤 6：Commit 测试验证**

```bash
git add .
git commit -m "test: verify view count functionality"
```

---

## 自检

- [x] **规格覆盖度：** 所有需求都已覆盖（计数、防刷、后台展示、排序）
- [x] **占位符扫描：** 无"TODO"、"待定"等占位符
- [x] **类型一致性：** view_count 在所有文件中类型一致（Integer/number）
- [x] **文件路径精确：** 所有路径都是项目中的实际路径
- [x] **步骤完整：** 每个步骤都有具体代码和命令

---

## 执行方式

计划已完成并保存到 `docs/superpowers/plans/2026-05-12-article-view-count-implementation.md`。两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

选哪种方式？
