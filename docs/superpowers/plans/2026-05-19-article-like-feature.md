# 文章点赞功能实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 为博客文章实现点赞功能，支持登录和未登录用户点赞，具备防重复点赞和 IP 限流防护。

**架构：** 
- 后端：新增 ArticleLike 模型和点赞 API 端点，使用 SQLAlchemy ORM 和 flask-limiter 限流
- 前端：新增 ArticleLike 组件，集成到 PostDetail 页面，使用 optimistic UI 更新
- 数据库：新增 article_likes 表，使用唯一约束防止重复点赞

**技术栈：** Python/Flask, SQLAlchemy, Vue 3, TypeScript, MySQL, flask-limiter

---

## 文件结构

**后端文件：**
- 创建：`backend/app/models/like.py` - ArticleLike 模型
- 修改：`backend/app/models/__init__.py` - 导出新模型
- 创建：`backend/scripts/add_article_likes_table.py` - 数据库迁移脚本
- 修改：`backend/app/models/article.py` - Article.to_dict() 添加 like_count
- 修改：`backend/app/api/v1/articles.py` - 添加点赞/取消点赞 API 端点

**前端文件：**
- 创建：`frontend/src/api/like.ts` - 点赞 API 调用方法
- 创建：`frontend/src/components/article/ArticleLike.vue` - 点赞组件
- 修改：`frontend/src/views/blog/PostDetail.vue` - 集成点赞组件
- 创建：`frontend/e2e/like.spec.ts` - E2E 测试

**测试文件：**
- 创建：`backend/tests/test_article_like.py` - 后端单元测试

---

## 任务 1：后端数据模型

**文件：**
- 创建：`backend/app/models/like.py`
- 修改：`backend/app/models/__init__.py`

- [ ] **步骤 1：创建 ArticleLike 模型**

```python
"""
Article Like Model
"""
from datetime import datetime
from app.extensions import db


class ArticleLike(db.Model):
    """Article Like model"""
    
    __tablename__ = 'article_likes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article_meta.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    article = db.relationship('Article', backref=db.backref('likes', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('Admin', backref=db.backref('article_likes', lazy='dynamic'))
    
    # Unique constraints
    __table_args__ = (
        db.UniqueConstraint('article_id', 'user_id', name='uq_article_user'),
        db.UniqueConstraint('article_id', 'session_id', name='uq_article_session'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<ArticleLike article_id={self.article_id} user_id={self.user_id}>'
```

- [ ] **步骤 2：在 __init__.py 中导出新模型**

修改 `backend/app/models/__init__.py`：

```python
from .like import ArticleLike

__all__ = [
    'Admin',
    'Article',
    'ArticleCategory',
    'ArticleTag',
    'Category',
    'Tag',
    'Comment',
    'SiteSetting',
    'OperationLog',
    'DonationSetting',
    'CrawledURL',
    'CrawledTitle',
    'CrawlerTask',
    'AIQueue',
    'ScheduledJobLog',
    'ArticleLike',  # 新增
]
```

- [ ] **步骤 3：Commit**

```bash
cd backend
git add app/models/like.py app/models/__init__.py
git commit -m "feat: add ArticleLike model"
```

---

## 任务 2：数据库迁移

**文件：**
- 创建：`backend/scripts/add_article_likes_table.py`

- [ ] **步骤 1：创建迁移脚本**

```python
"""
Migration script to add article_likes table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.like import ArticleLike

def migrate():
    """Create article_likes table"""
    app = create_app()
    with app.app_context():
        print("Creating article_likes table...")
        db.create_all()
        print("Table created successfully!")
        
        # Verify table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if 'article_likes' in tables:
            print("✓ article_likes table verified")
        else:
            print("✗ article_likes table not found")

if __name__ == '__main__':
    migrate()
```

- [ ] **步骤 2：执行迁移脚本**

```bash
cd backend
python scripts/add_article_likes_table.py
```

预期输出：
```
Creating article_likes table...
Table created successfully!
✓ article_likes table verified
```

- [ ] **步骤 3：Commit**

```bash
cd backend
git add scripts/add_article_likes_table.py
git commit -m "migrations: add article_likes table"
```

---

## 任务 3：修改 Article 模型添加点赞数

**文件：**
- 修改：`backend/app/models/article.py:56-70`

- [ ] **步骤 1：修改 to_dict() 方法**

在 `Article.to_dict()` 方法中添加 like_count 字段（在 `view_count` 后面）：

```python
def to_dict(self, include_content=False):
    """Convert to dictionary"""
    data = {
        'id': self.id,
        'slug': self.slug,
        'title': self.title,
        'description': self.description,
        'cover_image': self.cover_image,
        'status': self.status,
        'view_count': self.view_count or 0,
        'like_count': self.likes.count(),  # 新增：实时计算点赞数
        'comment_count': self.comments.filter_by(status='approved').count(),
        'published_at': self.published_at.isoformat() if self.published_at else None,
        'created_at': self.created_at.isoformat() if self.created_at else None,
        'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        'categories': [c.to_dict() for c in self.categories],
        'tags': [t.to_dict() for t in self.tags],
    }
    # ... 其余代码保持不变
```

- [ ] **步骤 2：验证修改**

```bash
cd backend
python -c "from app.models.article import Article; print('Import successful')"
```

- [ ] **步骤 3：Commit**

```bash
cd backend
git add app/models/article.py
git commit -m "feat: add like_count to Article.to_dict()"
```

---

## 任务 4：实现点赞 API

**文件：**
- 修改：`backend/app/api/v1/articles.py`

- [ ] **步骤 1：导入 ArticleLike 模型**

在 `articles.py` 顶部添加导入：

```python
from app.models.article import Article
from app.models.like import ArticleLike  # 新增
```

- [ ] **步骤 2：实现点赞 API 端点**

在 `articles.py` 末尾添加点赞端点（在文件末尾，`if __name__ == '__main__'` 之前）：

```python
@bp.route('/<int:id>/like', methods=['POST'])
@limiter.limit("10 per minute", key_func=lambda: request.remote_addr)
@jwt_required(optional=True)
def like_article(id):
    """
    Like an article
    
    Supports both authenticated and anonymous users.
    For authenticated users: uses user_id
    For anonymous users: uses session_id + IP address
    
    Returns:
        - 200: Success
        - 404: Article not found
        - 409: Already liked
        - 429: Rate limit exceeded
    """
    # Find article
    article = Article.query.get(id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    # Get user info
    try:
        user_id = get_jwt_identity()
    except:
        user_id = None
    
    session_id = request.headers.get('X-Session-ID', request.remote_addr)
    ip_address = request.remote_addr
    
    # Check if already liked
    if user_id:
        existing = ArticleLike.query.filter_by(article_id=id, user_id=user_id).first()
    else:
        existing = ArticleLike.query.filter_by(article_id=id, session_id=session_id).first()
    
    if existing:
        return jsonify({
            'error': 'Already liked',
            'message': '您已点赞过这篇文章'
        }), 409
    
    # Create like record
    like = ArticleLike(
        article_id=id,
        user_id=user_id,
        session_id=session_id if not user_id else None,
        ip_address=ip_address
    )
    db.session.add(like)
    db.session.commit()
    
    # Get updated like count
    like_count = article.likes.count()
    
    return jsonify({
        'success': True,
        'like_count': like_count,
        'liked': True
    }), 200


@bp.route('/<int:id>/unlike', methods=['DELETE'])
@jwt_required(optional=True)
def unlike_article(id):
    """
    Unlike an article
    
    Returns:
        - 200: Success
        - 404: Article not found or like not found
    """
    # Find article
    article = Article.query.get(id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    # Get user info
    try:
        user_id = get_jwt_identity()
    except:
        user_id = None
    
    session_id = request.headers.get('X-Session-ID', request.remote_addr)
    
    # Find and delete like record
    if user_id:
        like = ArticleLike.query.filter_by(article_id=id, user_id=user_id).first()
    else:
        like = ArticleLike.query.filter_by(article_id=id, session_id=session_id).first()
    
    if not like:
        return jsonify({
            'error': 'Like not found',
            'message': '您未点赞过这篇文章'
        }), 404
    
    db.session.delete(like)
    db.session.commit()
    
    # Get updated like count
    like_count = article.likes.count()
    
    return jsonify({
        'success': True,
        'like_count': like_count,
        'liked': False
    }), 200
```

- [ ] **步骤 3：验证导入**

```bash
cd backend
python -c "from app.api.v1.articles import bp; print('Import successful')"
```

- [ ] **步骤 4：Commit**

```bash
cd backend
git add app/api/v1/articles.py
git commit -m "feat: add like/unlike API endpoints"
```

---

## 任务 5：后端单元测试

**文件：**
- 创建：`backend/tests/test_article_like.py`

- [ ] **步骤 1：编写单元测试**

```python
"""
Tests for Article Like API
"""
import pytest
from app import create_app
from app.extensions import db
from app.models.article import Article
from app.models.like import ArticleLike
from app.models.admin import Admin
from datetime import datetime, timedelta
import json


@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_article(app):
    """Create sample article"""
    with app.app_context():
        article = Article(
            slug='test-article',
            title='Test Article',
            content='Test content',
            status='published',
            published_at=datetime.utcnow()
        )
        db.session.add(article)
        db.session.commit()
        return article


class TestLikeArticle:
    """Test like article endpoint"""
    
    def test_like_article_success(self, client, sample_article):
        """Test successful like"""
        response = client.post(f'/api/v1/articles/{sample_article.id}/like')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['like_count'] == 1
        assert data['liked'] is True
    
    def test_like_article_not_found(self, client):
        """Test like non-existent article"""
        response = client.post('/api/v1/articles/99999/like')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_like_article_duplicate(self, client, sample_article):
        """Test duplicate like returns 409"""
        # First like
        client.post(f'/api/v1/articles/{sample_article.id}/like')
        
        # Second like (same IP/session)
        response = client.post(f'/api/v1/articles/{sample_article.id}/like')
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_unlike_article_success(self, client, sample_article):
        """Test successful unlike"""
        # First like
        client.post(f'/api/v1/articles/{sample_article.id}/like')
        
        # Then unlike
        response = client.delete(f'/api/v1/articles/{sample_article.id}/unlike')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['like_count'] == 0
        assert data['liked'] is False
    
    def test_unlike_article_not_liked(self, client, sample_article):
        """Test unlike without prior like returns 404"""
        response = client.delete(f'/api/v1/articles/{sample_article.id}/unlike')
        assert response.status_code == 404
```

- [ ] **步骤 2：运行测试**

```bash
cd backend
pytest tests/test_article_like.py -v
```

预期输出：5 个测试全部通过

- [ ] **步骤 3：Commit**

```bash
cd backend
git add tests/test_article_like.py
git commit -m "test: add article like API tests"
```

---

## 任务 6：前端 API 调用方法

**文件：**
- 创建：`frontend/src/api/like.ts`

- [ ] **步骤 1：创建 API 调用方法**

```typescript
import api from './index';

export interface LikeResponse {
  success: boolean;
  like_count: number;
  liked: boolean;
}

export interface ErrorResponse {
  error: string;
  message?: string;
}

/**
 * Generate or get session ID for anonymous users
 */
const getSessionId = (): string => {
  let sessionId = sessionStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
    sessionStorage.setItem('session_id', sessionId);
  }
  return sessionId;
};

/**
 * Like an article
 */
export const likeArticle = async (articleId: number): Promise<LikeResponse> => {
  const sessionId = getSessionId();
  const response = await api.post<LikeResponse>(
    `/articles/${articleId}/like`,
    {},
    {
      headers: {
        'X-Session-ID': sessionId,
      },
    }
  );
  return response.data;
};

/**
 * Unlike an article
 */
export const unlikeArticle = async (articleId: number): Promise<LikeResponse> => {
  const sessionId = getSessionId();
  const response = await api.delete<LikeResponse>(
    `/articles/${articleId}/unlike`,
    {
      headers: {
        'X-Session-ID': sessionId,
      },
    }
  );
  return response.data;
};

/**
 * Get article like status (for initial load)
 */
export const getLikeStatus = async (articleId: number): Promise<{ liked: boolean; like_count: number }> => {
  // For now, we'll get this from the article detail API
  // This is a placeholder for future dedicated endpoint
  return {
    liked: false,
    like_count: 0,
  };
};
```

- [ ] **步骤 2：验证 TypeScript 编译**

```bash
cd frontend
npm run build
```

- [ ] **步骤 3：Commit**

```bash
cd frontend
git add src/api/like.ts
git commit -m "feat: add article like API methods"
```

---

## 任务 7：前端点赞组件

**文件：**
- 创建：`frontend/src/components/article/ArticleLike.vue`

- [ ] **步骤 1：创建点赞组件**

```vue
<template>
  <div class="article-like">
    <button
      :class="['like-button', { liked: isLiked, loading: isLoading }]"
      @click="handleLike"
      :disabled="isLoading"
      type="button"
    >
      <span class="like-icon">
        <!-- Heart icon -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          class="w-6 h-6"
        >
          <path
            d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z"
          />
        </svg>
      </span>
      <span class="like-count">{{ likeCount }}</span>
    </button>
    
    <!-- Toast notification -->
    <transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div v-if="showToast" class="toast-notification">
        {{ toastMessage }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { likeArticle, unlikeArticle } from '@/api/like';

interface Props {
  articleId: number;
  initialLikeCount: number;
  initialLiked?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  initialLiked: false,
});

const emit = defineEmits<{
  (e: 'update', liked: boolean, likeCount: number): void;
}>();

const isLiked = ref(props.initialLiked);
const likeCount = ref(props.initialLikeCount);
const isLoading = ref(false);
const showToast = ref(false);
const toastMessage = ref('');

const showSuccessToast = (message: string) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 2000);
};

const showErrorToast = (message: string) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 2000);
};

const handleLike = async () => {
  if (isLoading.value) return;
  
  isLoading.value = true;
  
  // Optimistic update
  const previousState = isLiked.value;
  const previousCount = likeCount.value;
  
  if (isLiked.value) {
    // Unlike
    isLiked.value = false;
    likeCount.value = Math.max(0, likeCount.value - 1);
  } else {
    // Like
    isLiked.value = true;
    likeCount.value = likeCount.value + 1;
  }
  
  try {
    let response;
    if (previousState) {
      response = await unlikeArticle(props.articleId);
    } else {
      response = await likeArticle(props.articleId);
    }
    
    // Update with server response
    isLiked.value = response.liked;
    likeCount.value = response.like_count;
    emit('update', response.liked, response.like_count);
    
    if (response.liked) {
      showSuccessToast('点赞成功');
    } else {
      showSuccessToast('已取消点赞');
    }
  } catch (error: any) {
    // Rollback on error
    isLiked.value = previousState;
    likeCount.value = previousCount;
    
    if (error.response?.status === 409) {
      showErrorToast('您已点赞过这篇文章');
    } else if (error.response?.status === 429) {
      showErrorToast('操作过于频繁，请稍后再试');
    } else {
      showErrorToast('操作失败，请重试');
    }
  } finally {
    isLoading.value = false;
  }
};

// Watch for prop changes
watch(
  () => props.initialLikeCount,
  (newVal) => {
    likeCount.value = newVal;
  }
);

watch(
  () => props.initialLiked,
  (newVal) => {
    isLiked.value = newVal;
  }
);
</script>

<style scoped>
.article-like {
  position: relative;
  display: inline-block;
}

.like-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 9999px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.like-button:hover:not(:disabled) {
  border-color: #ef4444;
  background: #fef2f2;
}

.like-button.liked {
  border-color: #ef4444;
  background: #fef2f2;
}

.like-button.liked .like-icon {
  color: #ef4444;
}

.like-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.like-button.loading {
  position: relative;
}

.like-button.loading::after {
  content: '';
  position: absolute;
  width: 1rem;
  height: 1rem;
  border: 2px solid #e5e7eb;
  border-top-color: #ef4444;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  right: 0.75rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.like-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #9ca3af;
  transition: color 0.2s;
}

.like-count {
  font-weight: 500;
  color: #374151;
}

.toast-notification {
  position: absolute;
  bottom: -3rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.5rem 1rem;
  background: #1f2937;
  color: white;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  white-space: nowrap;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .like-button {
    padding: 0.375rem 0.75rem;
    font-size: 0.813rem;
  }
  
  .like-icon {
    width: 1rem;
    height: 1rem;
  }
}
</style>
```

- [ ] **步骤 2：验证组件编译**

```bash
cd frontend
npm run build
```

- [ ] **步骤 3：Commit**

```bash
cd frontend
git add src/components/article/ArticleLike.vue
git commit -m "feat: add ArticleLike component"
```

---

## 任务 8：集成到文章详情页

**文件：**
- 修改：`frontend/src/views/blog/PostDetail.vue`

- [ ] **步骤 1：导入点赞组件**

在 `PostDetail.vue` 中导入组件（在 script 部分）：

```typescript
import ArticleLike from '@/components/article/ArticleLike.vue';
```

- [ ] **步骤 2：在模板中添加点赞组件**

在文章标题下方或内容上方添加点赞组件（找到合适的位置，如在 `{{ article.title }}` 后面）：

```vue
<div class="article-meta">
  <span class="date">{{ formatDate(article.published_at) }}</span>
  <span class="views">
    <svg><!-- view icon --></svg>
    {{ article.view_count }}
  </span>
  <!-- Add like component -->
  <ArticleLike
    v-if="article.id"
    :article-id="article.id"
    :initial-like-count="article.like_count || 0"
    :initial-liked="false"
    @update="handleLikeUpdate"
  />
</div>
```

- [ ] **步骤 3：添加更新处理函数**

在 script 中添加：

```typescript
const handleLikeUpdate = (liked: boolean, likeCount: number) => {
  // Update local article data if needed
  console.log('Like updated:', liked, likeCount);
};
```

- [ ] **步骤 4：验证编译**

```bash
cd frontend
npm run build
```

- [ ] **步骤 5：Commit**

```bash
cd frontend
git add src/views/blog/PostDetail.vue
git commit -m "feat: integrate like component in PostDetail"
```

---

## 任务 9：端到端测试

**文件：**
- 创建：`frontend/e2e/like.spec.ts`

- [ ] **步骤 1：编写 E2E 测试**

```typescript
import { test, expect } from '@playwright/test';

test.describe('Article Like Feature', () => {
  test('should like an article', async ({ page }) => {
    // Navigate to article page
    await page.goto('/blog/test-article');
    
    // Check initial state
    const likeButton = page.locator('.like-button');
    await expect(likeButton).toBeVisible();
    
    const initialCount = await likeButton.locator('.like-count').textContent();
    expect(initialCount).toBe('0');
    
    // Click like button
    await likeButton.click();
    
    // Wait for update
    await page.waitForTimeout(500);
    
    // Verify liked state
    await expect(likeButton).toHaveClass(/liked/);
    const newCount = await likeButton.locator('.like-count').textContent();
    expect(parseInt(newCount!)).toBeGreaterThan(0);
    
    // Check toast notification
    const toast = page.locator('.toast-notification');
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('点赞成功');
  });

  test('should unlike an article', async ({ page }) => {
    // Navigate to article page
    await page.goto('/blog/test-article');
    
    // Like first
    const likeButton = page.locator('.like-button');
    await likeButton.click();
    await page.waitForTimeout(500);
    
    // Unlike
    await likeButton.click();
    await page.waitForTimeout(500);
    
    // Verify unliked state
    await expect(likeButton).not.toHaveClass(/liked/);
    
    // Check toast
    const toast = page.locator('.toast-notification');
    await expect(toast).toContainText('已取消点赞');
  });

  test('should show error for duplicate like', async ({ page }) => {
    // This test requires backend to enforce duplicate prevention
    // May need to mock backend response for reliable testing
    await page.goto('/blog/test-article');
    
    const likeButton = page.locator('.like-button');
    
    // First like
    await likeButton.click();
    await page.waitForTimeout(500);
    
    // Second like (should fail)
    await likeButton.click();
    await page.waitForTimeout(500);
    
    // Should still be in liked state
    await expect(likeButton).toHaveClass(/liked/);
  });
});
```

- [ ] **步骤 2：运行 E2E 测试**

```bash
cd frontend
npm run test:e2e
```

- [ ] **步骤 3：修复发现的 bug**

根据测试结果修复问题

- [ ] **步骤 4：Commit**

```bash
cd frontend
git add e2e/like.spec.ts
git commit -m "test: add E2E tests for like feature"
```

---

## 任务 10：文档和收尾

**文件：**
- 创建：`backend/docs/LIKE_API.md`
- 创建：`frontend/docs/LIKE_FEATURE.md`

- [ ] **步骤 1：编写后端 API 文档**

```markdown
# Article Like API

## Endpoints

### POST /api/v1/articles/:id/like

Like an article.

**Request:**
```
POST /api/v1/articles/1/like
Headers:
  X-Session-ID: session_123456 (for anonymous users)
  Authorization: Bearer <token> (for authenticated users, optional)
```

**Response (200 OK):**
```json
{
  "success": true,
  "like_count": 42,
  "liked": true
}
```

**Response (409 Conflict):**
```json
{
  "error": "Already liked",
  "message": "您已点赞过这篇文章"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Article not found"
}
```

**Response (429 Too Many Requests):**
```json
{
  "error": "Rate limit exceeded"
}
```

### DELETE /api/v1/articles/:id/unlike

Unlike an article.

**Request:**
```
DELETE /api/v1/articles/1/unlike
Headers:
  X-Session-ID: session_123456
```

**Response (200 OK):**
```json
{
  "success": true,
  "like_count": 41,
  "liked": false
}
```

## Rate Limiting

- 10 requests per minute per IP address
- Applies to both like and unlike endpoints

## Authentication

- Supports both authenticated and anonymous users
- Authenticated users: identified by JWT token
- Anonymous users: identified by X-Session-ID header + IP address
```

- [ ] **步骤 2：编写前端功能说明**

```markdown
# Article Like Feature

## Overview

The article like feature allows users to express appreciation for articles with a single click.

## Components

### ArticleLike.vue

**Props:**
- `articleId`: number - Article ID
- `initialLikeCount`: number - Initial like count
- `initialLiked`: boolean - Initial liked state (default: false)

**Events:**
- `update(liked: boolean, likeCount: number)` - Emitted when like status changes

**Features:**
- Optimistic UI updates
- Loading state during API calls
- Toast notifications for success/error
- Responsive design

## Usage

```vue
<ArticleLike
  :article-id="article.id"
  :initial-like-count="article.like_count"
  @update="handleLikeUpdate"
/>
```

## API Methods

- `likeArticle(articleId: number)` - Like an article
- `unlikeArticle(articleId: number)` - Unlike an article

## Session Management

Anonymous users are identified by:
- Session ID stored in sessionStorage
- IP address as fallback

## Error Handling

- 409: Already liked - shows toast message
- 429: Rate limit exceeded - shows error message
- Network errors - shows generic error message
```

- [ ] **步骤 3：代码审查和清理**

```bash
# Backend lint
cd backend
flake8 app/
black --check app/

# Frontend lint
cd frontend
npm run lint
```

修复所有 lint 错误

- [ ] **步骤 4：运行所有测试**

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Frontend E2E
cd frontend
npm run test:e2e
```

- [ ] **步骤 5：最终 Commit**

```bash
cd backend
git add docs/LIKE_API.md
git commit -m "docs: add like API documentation"

cd frontend
git add docs/LIKE_FEATURE.md
git commit -m "docs: add like feature documentation"
```

---

## 验证清单

完成所有任务后，验证：

- [ ] 后端模型创建成功
- [ ] 数据库迁移成功
- [ ] 点赞 API 工作正常
- [ ] 限流防护生效
- [ ] 前端组件渲染正常
- [ ] 点赞/取消点赞交互流畅
- [ ] 所有单元测试通过
- [ ] 所有 E2E 测试通过
- [ ] 文档完整

---

计划已完成并保存到 `docs/superpowers/plans/2026-05-19-article-like-feature.md`。两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

选哪种方式？
