# 文章评论系统实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 为博客文章添加完整的评论系统，支持用户发表评论、回复评论，后台可查看和管理评论

**架构：** 
- 后端扩展 Comment 模型添加内容、作者、回复关系字段
- 新增评论创建 API 和树形评论列表 API
- 前端在文章详情页添加评论组件（列表 + 表单）
- 后台文章列表显示评论数统计

**技术栈：** Flask, SQLAlchemy, Vue 3, TypeScript, Naive UI

**需求确认：**
1. 评论无需登录，填写昵称和邮箱即可
2. 所有评论自动通过，后台可删除
3. 邮箱选填（不填则用默认头像）

---

## 文件结构

**后端文件：**
- 修改：`backend/app/models/comment.py` - 扩展 Comment 模型
- 修改：`backend/app/api/v1/comments.py` - 新增评论创建和树形列表 API
- 创建：`backend/scripts/add_comment_fields_migration.py` - 数据库迁移脚本

**前端文件：**
- 修改：`frontend/src/types/index.ts` - 扩展 Comment 类型定义
- 修改：`frontend/src/api/index.ts` - 新增评论 API 调用
- 创建：`frontend/src/views/blog/components/CommentSection.vue` - 评论区主组件
- 创建：`frontend/src/views/blog/components/CommentForm.vue` - 评论表单组件
- 创建：`frontend/src/views/blog/components/CommentList.vue` - 评论列表组件
- 创建：`frontend/src/views/blog/components/CommentItem.vue` - 单条评论组件
- 修改：`frontend/src/views/blog/PostDetail.vue` - 集成评论区

**后台文件：**
- 修改：`frontend/src/views/admin/articles/ArticleList.vue` - 添加评论数列

---

## 任务分解

### 任务 1：后端数据库迁移

**文件：**
- 创建：`backend/scripts/add_comment_fields_migration.py`
- 修改：`backend/app/models/comment.py`

- [ ] **步骤 1：创建数据库迁移脚本**

```python
#!/usr/bin/env python
"""
Add comment fields migration
添加评论系统所需字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        # 添加 content 字段
        db.session.execute(text(
            "ALTER TABLE comments ADD COLUMN content TEXT"
        ))
        
        # 添加 author_name 字段
        db.session.execute(text(
            "ALTER TABLE comments ADD COLUMN author_name VARCHAR(100)"
        ))
        
        # 添加 author_email 字段
        db.session.execute(text(
            "ALTER TABLE comments ADD COLUMN author_email VARCHAR(100)"
        ))
        
        # 添加 parent_id 字段（回复关系）
        db.session.execute(text(
            "ALTER TABLE comments ADD COLUMN parent_id INTEGER"
        ))
        
        # 添加 reply_to 字段
        db.session.execute(text(
            "ALTER TABLE comments ADD COLUMN reply_to VARCHAR(100)"
        ))
        
        # 添加 parent_id 索引
        db.session.execute(text(
            "CREATE INDEX idx_comments_parent_id ON comments(parent_id)"
        ))
        
        db.session.commit()
        print("✅ 数据库迁移完成")

if __name__ == '__main__':
    migrate()
```

- [ ] **步骤 2：运行迁移脚本**

```bash
cd backend
./venv/bin/python scripts/add_comment_fields_migration.py
```

预期输出：`✅ 数据库迁移完成`

- [ ] **步骤 3：验证数据库表结构**

```bash
cd backend
./venv/bin/python << 'EOF'
from app import create_app
from app.extensions import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('comments')
    print("comments 表结构:")
    for col in columns:
        print(f"  {col['name']}: {col['type']}")
EOF
```

预期输出包含：content, author_name, author_email, parent_id, reply_to

- [ ] **步骤 4：更新 Comment 模型**

```python
"""Comment Model"""
from datetime import datetime
from app.extensions import db


class Comment(db.Model):
    """Comment model"""
    
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_slug = db.Column(db.String(200), db.ForeignKey('article_meta.slug'), nullable=False)
    content = db.Column(db.Text)  # 评论内容
    author_name = db.Column(db.String(100))  # 作者名称
    author_email = db.Column(db.String(100))  # 作者邮箱
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # 父评论 ID
    reply_to = db.Column(db.String(100))  # 回复对象名称
    status = db.Column(db.String(20), default='approved')  # 默认自动通过
    is_pinned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 自引用关系
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy='dynamic'))
    
    def to_dict(self, include_replies=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'article_slug': self.article_slug,
            'content': self.content,
            'author_name': self.author_name,
            'author_email': self.author_email,
            'parent_id': self.parent_id,
            'reply_to': self.reply_to,
            'status': self.status,
            'is_pinned': bool(self.is_pinned),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_replies and hasattr(self, 'replies'):
            data['replies'] = [reply.to_dict(include_replies=False) for reply in self.replies]
        
        return data
    
    def __repr__(self):
        return f'<Comment {self.id} for {self.article_slug}>'
```

- [ ] **步骤 5：Commit**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog
git add backend/scripts/add_comment_fields_migration.py backend/app/models/comment.py
git commit -m "feat: add comment fields and migration script"
```

---

### 任务 2：后端评论 API

**文件：**
- 修改：`backend/app/api/v1/comments.py`

- [ ] **步骤 1：添加创建评论 API**

```python
@bp.route('', methods=['POST'])
@limiter.limit("10 per hour")
def create_comment():
    """
    创建评论或回复
    
    Request Body:
        {
            "article_slug": "article-slug",
            "content": "评论内容",
            "author_name": "张三",
            "author_email": "zhangsan@example.com",  # 可选
            "parent_id": null,  # 如果是回复，则为父评论 ID
            "reply_to": null    # 如果是回复，则为被回复者名称
        }
    
    Returns:
        {
            "success": true,
            "comment": { ... }
        }
    """
    from datetime import datetime
    
    data = request.get_json()
    
    # 验证必填字段
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    
    article_slug = data.get('article_slug')
    content = data.get('content')
    author_name = data.get('author_name')
    
    if not article_slug or not content or not author_name:
        return jsonify({
            'success': False,
            'error': 'Missing required fields: article_slug, content, author_name'
        }), 400
    
    # 验证 parent_id（如果有）
    parent_id = data.get('parent_id')
    if parent_id:
        parent_comment = Comment.query.get(parent_id)
        if not parent_comment:
            return jsonify({'success': False, 'error': 'Parent comment not found'}), 404
    
    # 创建评论
    comment = Comment(
        article_slug=article_slug,
        content=content,
        author_name=author_name,
        author_email=data.get('author_email'),
        parent_id=parent_id,
        reply_to=data.get('reply_to'),
        status='approved',  # 自动通过
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': comment.to_dict()
    }), 201
```

- [ ] **步骤 2：添加获取文章评论树形列表 API**

```python
@bp.route('/article/<slug>', methods=['GET'])
@limiter.limit("60 per minute")
def get_article_comments(slug):
    """
    获取文章评论列表（树形结构）
    
    Query Parameters:
        page: 页码
        limit: 每页数量
    
    Returns:
        {
            "comments": [...],  # 树形结构
            "total": 100,
            "page": 1,
            "limit": 20
        }
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # 获取顶级评论（parent_id 为 null）
    query = Comment.query.filter_by(
        article_slug=slug,
        parent_id=None,
        status='approved'
    )
    
    query = query.order_by(Comment.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    
    # 构建树形结构
    comments = []
    for comment in pagination.items:
        comment_dict = comment.to_dict(include_replies=True)
        # 将 replies 从动态加载器转换为列表
        if 'replies' in comment_dict:
            comment_dict['replies'] = [
                reply.to_dict(include_replies=False) 
                for reply in comment.replies.order_by(Comment.created_at.asc()).all()
            ]
        comments.append(comment_dict)
    
    return jsonify({
        'comments': comments,
        'total': pagination.total,
        'page': page,
        'limit': limit
    }), 200
```

- [ ] **步骤 3：添加获取评论数 API**

```python
@bp.route('/article/<slug>/count', methods=['GET'])
@limiter.limit("60 per minute")
def get_article_comment_count(slug):
    """
    获取文章评论数
    
    Returns:
        {
            "count": 10
        }
    """
    count = Comment.query.filter_by(
        article_slug=slug,
        status='approved'
    ).count()
    
    return jsonify({'count': count}), 200
```

- [ ] **步骤 4：更新现有 GET API 支持 parent_id 过滤**

在 `get_comments` 函数中添加：
```python
parent_id = request.args.get('parent_id', type=int)
if parent_id is not None:
    query = query.filter_by(parent_id=parent_id)
```

- [ ] **步骤 5：Commit**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog
git add backend/app/api/v1/comments.py
git commit -m "feat: add comment creation and tree list API"
```

---

### 任务 3：前端类型和 API

**文件：**
- 修改：`frontend/src/types/index.ts`
- 修改：`frontend/src/api/index.ts`

- [ ] **步骤 1：扩展 Comment 类型定义**

```typescript
export interface Comment {
  id: number
  article_slug: string
  content: string
  author_name: string
  author_email?: string
  parent_id?: number | null
  reply_to?: string | null
  status: 'pending' | 'approved' | 'rejected'
  is_pinned: boolean
  created_at: string
  updated_at?: string
  replies?: Comment[]  // 回复列表
}
```

- [ ] **步骤 2：扩展 commentApi**

```typescript
export const commentApi = {
  // 现有方法...
  getList(params?: { article_slug?: string; status?: string; page?: number; limit?: number }) {
    return apiClient.get<CommentsResponse>('comments', {
      params,
    })
  },

  delete(id: number) {
    return apiClient.delete<{ message: string }>(`comments/${id}`)
  },

  approve(id: number) {
    return apiClient.put<{ comment: Comment }>(`comments/${id}/approve`)
  },

  reject(id: number) {
    return apiClient.put<{ comment: Comment }>(`comments/${id}/reject`)
  },

  // 新增方法
  async getArticleComments(slug: string, params?: { page?: number; limit?: number }) {
    const response = await apiClient.get<{ 
      comments: Comment[]
      total: number
      page: number
      limit: number
    }>(`comments/article/${slug}`, { params })
    return response
  },

  async getCommentCount(slug: string) {
    const response = await apiClient.get<{ count: number }>(`comments/article/${slug}/count`)
    return response.count
  },

  async create(data: {
    article_slug: string
    content: string
    author_name: string
    author_email?: string
    parent_id?: number | null
    reply_to?: string | null
  }) {
    const response = await apiClient.post<{ comment: Comment }>('comments', data)
    return response.comment
  },
}
```

- [ ] **步骤 3：Commit**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog
git add frontend/src/types/index.ts frontend/src/api/index.ts
git commit -m "feat: add comment types and API methods"
```

---

### 任务 4：前端评论组件

**文件：**
- 创建：`frontend/src/views/blog/components/CommentSection.vue`
- 创建：`frontend/src/views/blog/components/CommentForm.vue`
- 创建：`frontend/src/views/blog/components/CommentList.vue`
- 创建：`frontend/src/views/blog/components/CommentItem.vue`

- [ ] **步骤 1：创建 CommentForm 组件**

```vue
<template>
  <div class="comment-form">
    <n-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-placement="top"
    >
      <n-form-item label="昵称" path="author_name">
        <n-input
          v-model:value="formData.author_name"
          placeholder="请输入昵称"
          clearable
        />
      </n-form-item>

      <n-form-item label="邮箱（选填）" path="author_email">
        <n-input
          v-model:value="formData.author_email"
          placeholder="用于显示 Gravatar 头像"
          clearable
        />
      </n-form-item>

      <n-form-item label="评论内容" path="content">
        <n-input
          v-model:value="formData.content"
          type="textarea"
          placeholder="写下你的评论..."
          :rows="4"
          show-count
          maxlength="1000"
        />
      </n-form-item>

      <n-form-item>
        <n-space>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isReply ? '回复' : '发表评论' }}
          </n-button>
          <n-button v-if="isReply" @click="handleCancel">取消</n-button>
        </n-space>
      </n-form-item>
    </n-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useMessage } from 'naive-ui'
import type { FormRules, FormItemRule } from 'naive-ui'
import { commentApi } from '@/api'

interface Props {
  articleSlug: string
  parentId?: number | null
  replyTo?: string | null
  isReply?: boolean
  onSuccess?: () => void
  onCancel?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  parentId: null,
  replyTo: null,
  isReply: false,
})

const emit = defineEmits<{
  (e: 'success'): void
  (e: 'cancel'): void
}>()

const message = useMessage()

const formData = reactive({
  author_name: '',
  author_email: '',
  content: '',
})

const formRules: FormRules = {
  author_name: {
    required: true,
    message: '请输入昵称',
    trigger: 'blur',
  },
  content: {
    required: true,
    message: '请输入评论内容',
    trigger: 'blur',
  },
}

const formRef = ref(null)
const submitting = ref(false)

const handleSubmit = async () => {
  try {
    submitting.value = true
    
    await commentApi.create({
      article_slug: props.articleSlug,
      content: formData.content,
      author_name: formData.author_name,
      author_email: formData.author_email || undefined,
      parent_id: props.parentId || undefined,
      reply_to: props.replyTo || undefined,
    })
    
    message.success(props.isReply ? '回复成功' : '评论成功')
    
    // 清空表单
    formData.content = ''
    if (!props.isReply) {
      formData.author_name = ''
      formData.author_email = ''
    }
    
    emit('success')
  } catch (error) {
    console.error('Failed to submit comment:', error)
    message.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  formData.content = ''
  emit('cancel')
}
</script>

<style scoped>
.comment-form {
  margin-bottom: 24px;
}
</style>
```

- [ ] **步骤 2：创建 CommentItem 组件**

```vue
<template>
  <div class="comment-item" :class="{ 'is-reply': isReply }">
    <div class="comment-header">
      <n-avatar :size="32" round>
        <template #icon>
          {{ getAvatarText(comment.author_name) }}
        </template>
      </n-avatar>
      <div class="comment-meta">
        <span class="author-name">{{ comment.author_name }}</span>
        <span v-if="comment.reply_to" class="reply-to">
          回复 @{{ comment.reply_to }}
        </span>
      </div>
      <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
    </div>

    <div class="comment-content">
      {{ comment.content }}
    </div>

    <div class="comment-actions">
      <n-button text size="small" @click="handleReply">
        回复
      </n-button>
    </div>

    <!-- 回复表单 -->
    <div v-if="showReplyForm" class="reply-form">
      <CommentForm
        :article-slug="comment.article_slug"
        :parent-id="comment.id"
        :reply-to="comment.author_name"
        :is-reply="true"
        @success="handleReplySuccess"
        @cancel="showReplyForm = false"
      />
    </div>

    <!-- 回复列表 -->
    <div v-if="comment.replies && comment.replies.length > 0" class="replies">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :is-reply="true"
        @reply-success="handleReplySuccess"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { formatDate } from '@/utils/date'
import type { Comment } from '@/types'
import CommentForm from './CommentForm.vue'

interface Props {
  comment: Comment
  isReply?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isReply: false,
})

const emit = defineEmits<{
  (e: 'reply-success'): void
}>()

const showReplyForm = ref(false)

const getAvatarText = (name: string) => {
  return name.charAt(0).toUpperCase()
}

const handleReply = () => {
  showReplyForm.value = true
}

const handleReplySuccess = () => {
  showReplyForm.value = false
  emit('reply-success')
}
</script>

<style scoped>
.comment-item {
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}

.is-reply {
  padding-left: 48px;
  background: #f9f9f9;
  margin: 8px 0;
  border-radius: 8px;
  padding: 12px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.comment-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.author-name {
  font-weight: 600;
  color: #333;
}

.reply-to {
  font-size: 12px;
  color: #999;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-content {
  margin-bottom: 12px;
  line-height: 1.6;
  color: #333;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.replies {
  margin-top: 12px;
}

.reply-form {
  margin-top: 12px;
}
</style>
```

- [ ] **步骤 3：创建 CommentList 组件**

```vue
<template>
  <div class="comment-list">
    <div v-if="loading" class="loading">
      <n-spin size="small" />
    </div>

    <div v-else-if="comments.length === 0" class="empty">
      <n-empty description="暂无评论，快来抢沙发吧" />
    </div>

    <div v-else class="comments">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        @reply-success="$emit('refresh')"
      />
    </div>

    <div v-if="total > pageSize" class="pagination">
      <n-pagination
        v-model:page="currentPage"
        :item-count="total"
        :page-size="pageSize"
        @update-page="loadComments"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { commentApi } from '@/api'
import type { Comment } from '@/types'
import CommentItem from './CommentItem.vue'

interface Props {
  articleSlug: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const message = useMessage()

const loading = ref(false)
const comments = ref<Comment[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const loadComments = async (page: number = currentPage.value) => {
  loading.value = true
  try {
    const result = await commentApi.getArticleComments(props.articleSlug, {
      page,
      limit: pageSize.value,
    })
    comments.value = result.comments
    total.value = result.total
    currentPage.value = page
  } catch (error) {
    console.error('Failed to load comments:', error)
    message.error('加载评论失败')
  } finally {
    loading.value = false
  }
}

const refresh = () => {
  loadComments(currentPage.value)
  emit('refresh')
}

onMounted(() => {
  loadComments()
})

defineExpose({ refresh })
</script>

<style scoped>
.comment-list {
  margin-top: 24px;
}

.loading,
.empty {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.comments {
  margin-top: 16px;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
```

- [ ] **步骤 4：创建 CommentSection 组件**

```vue
<template>
  <div class="comment-section">
    <div class="section-header">
      <h3>评论</h3>
      <span class="comment-count" v-if="commentCount > 0">
        {{ commentCount }} 条评论
      </span>
    </div>

    <!-- 发表评论 -->
    <div class="post-comment">
      <CommentForm
        :article-slug="articleSlug"
        @success="handleCommentSuccess"
      />
    </div>

    <!-- 评论列表 -->
    <CommentList
      ref="commentListRef"
      :article-slug="articleSlug"
      @refresh="loadCommentCount"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { commentApi } from '@/api'
import CommentForm from './CommentForm.vue'
import CommentList from './CommentList.vue'

interface Props {
  articleSlug: string
}

const props = defineProps<Props>()

const commentCount = ref(0)
const commentListRef = ref(null)

const loadCommentCount = async () => {
  try {
    commentCount.value = await commentApi.getCommentCount(props.articleSlug)
  } catch (error) {
    console.error('Failed to load comment count:', error)
  }
}

const handleCommentSuccess = () => {
  loadCommentCount()
  commentListRef.value?.refresh()
}

onMounted(() => {
  loadCommentCount()
})
</script>

<style scoped>
.comment-section {
  margin-top: 60px;
  padding-top: 40px;
  border-top: 2px solid #f0f0f0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.section-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.comment-count {
  font-size: 14px;
  color: #999;
}

.post-comment {
  margin-bottom: 32px;
}
</style>
```

- [ ] **步骤 5：Commit**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog
git add frontend/src/views/blog/components/*.vue
git commit -m "feat: add comment components"
```

---

### 任务 5：集成到文章详情页

**文件：**
- 修改：`frontend/src/views/blog/PostDetail.vue`

- [ ] **步骤 1：导入 CommentSection 组件**

```typescript
import CommentSection from './components/CommentSection.vue'
```

- [ ] **步骤 2：在模板中添加评论区**

在 `</article>` 标签后添加：
```vue
      <!-- Comment Section -->
      <CommentSection :article-slug="route.params.slug as string" />
```

- [ ] **步骤 3：Commit**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog
git add frontend/src/views/blog/PostDetail.vue
git commit -m "feat: integrate comment section into article detail page"
```

---

### 任务 6：后台评论数显示

**文件：**
- 修改：`frontend/src/views/admin/articles/ArticleList.vue`

- [ ] **步骤 1：在表格中添加评论数列**

在 `columns` 数组中，`view_count` 列后添加：
```typescript
{
  title: '评论数',
  key: 'comment_count',
  width: 100,
  render(row) {
    return h('span', { style: 'font-size: 13px; color: #666;' }, [
      row.comment_count || 0,
    ])
  },
},
```

- [ ] **步骤 2：在 loadArticles 中获取评论数**

需要在加载文章时同时获取评论数。修改 `loadArticles` 函数，在获取文章列表后，批量获取每篇文章的评论数。

或者在后端 API 中直接返回评论数（推荐）。

- [ ] **步骤 3：Commit**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog
git add frontend/src/views/admin/articles/ArticleList.vue
git commit -m "feat: display comment count in admin article list"
```

---

### 任务 7：测试验证

- [ ] **步骤 1：测试发表评论**
  - 访问文章详情页
  - 填写昵称和评论内容
  - 提交评论
  - 验证评论显示在列表中

- [ ] **步骤 2：测试回复评论**
  - 点击评论的"回复"按钮
  - 填写回复内容
  - 提交回复
  - 验证回复显示在父评论下方

- [ ] **步骤 3：测试评论数统计**
  - 查看评论区标题的评论数
  - 后台文章列表查看评论数列

- [ ] **步骤 4：测试 API**
```bash
# 创建评论
curl -X POST http://localhost:5001/api/v1/comments \
  -H "Content-Type: application/json" \
  -d '{"article_slug":"test-article","content":"测试评论","author_name":"测试用户"}'

# 获取评论列表
curl http://localhost:5001/api/v1/comments/article/test-article

# 获取评论数
curl http://localhost:5001/api/v1/comments/article/test-article/count
```

- [ ] **步骤 5：验证完成**

所有功能测试通过后，标记任务完成。

---

## 自检

- [ ] 数据库迁移脚本包含所有必需字段
- [ ] Comment 模型有自引用关系
- [ ] API 支持创建评论和回复
- [ ] API 返回树形评论结构
- [ ] 前端组件支持嵌套回复
- [ ] 评论区集成到文章详情页
- [ ] 后台显示评论数
- [ ] 所有类型定义完整
- [ ] 错误处理完善

---

计划已完成并保存到 `docs/superpowers/plans/2026-05-12-article-comment-system.md`。两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

选哪种方式？
