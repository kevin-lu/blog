# 文章点赞功能实现总结

## 功能概述

为博客文章添加了点赞功能，支持：
- ✅ 未登录用户点赞（基于 session + IP）
- ✅ 登录用户点赞（基于 user_id）
- ✅ 实时计算点赞数
- ✅ IP 限流：10 次/分钟
- ✅ 防止重复点赞
- ✅ 无操作日志

## 实现内容

### 后端 (Backend)

1. **数据模型** - [`backend/app/models/like.py`](backend/app/models/like.py)
   - `ArticleLike` 模型
   - 唯一约束：`article_id + user_id` 和 `article_id + session_id`

2. **数据库迁移** - [`backend/scripts/add_article_likes_table.py`](backend/scripts/add_article_likes_table.py)
   - 创建 `article_likes` 表

3. **API 端点** - [`backend/app/api/v1/articles.py`](backend/app/api/v1/articles.py#L676-L785)
   - `POST /api/v1/articles/:id/like` - 点赞
   - `DELETE /api/v1/articles/:id/unlike` - 取消点赞
   - 限流：10 次/分钟 per IP

4. **单元测试** - [`backend/tests/test_article_like.py`](backend/tests/test_article_like.py)
   - 点赞成功测试
   - 重复点赞测试
   - 取消点赞测试

### 前端 (Frontend)

1. **API 方法** - [`frontend/src/api/like.ts`](frontend/src/api/like.ts)
   - `likeArticle()` - 点赞 API
   - `unlikeArticle()` - 取消点赞 API
   - Session ID 管理

2. **点赞组件** - [`frontend/src/components/article/ArticleLike.vue`](frontend/src/components/article/ArticleLike.vue)
   - 心形图标
   - 点赞数显示
   - 加载状态
   - Toast 提示
   - 响应式设计

3. **集成** - [`frontend/src/views/blog/PostDetail.vue`](frontend/src/views/blog/PostDetail.vue)
   - 在文章详情页显示点赞组件
   - 实时更新点赞数

4. **类型定义** - [`frontend/src/types/index.ts`](frontend/src/types/index.ts#L27)
   - 添加 `like_count` 字段

## API 使用示例

### 点赞
```javascript
import { likeArticle } from '@/api/like';

try {
  const response = await likeArticle(articleId);
  console.log(`点赞成功，当前点赞数：${response.like_count}`);
} catch (error) {
  if (error.response?.status === 409) {
    console.log('已点赞过');
  } else if (error.response?.status === 429) {
    console.log('操作过于频繁');
  }
}
```

### 取消点赞
```javascript
import { unlikeArticle } from '@/api/like';

const response = await unlikeArticle(articleId);
console.log(`取消点赞，当前点赞数：${response.like_count}`);
```

## 数据库表结构

```sql
CREATE TABLE article_likes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  article_id INTEGER NOT NULL,
  user_id INTEGER,
  session_id VARCHAR(100),
  ip_address VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (article_id) REFERENCES article_meta(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES admins(id),
  UNIQUE(article_id, user_id),
  UNIQUE(article_id, session_id)
);
```

## 限流策略

- **限制**：10 次点赞/分钟 per IP
- **实现**：flask-limiter
- **错误码**：429 Too Many Requests

## 注意事项

1. 首次使用需运行数据库迁移脚本：
   ```bash
   cd backend
   python scripts/add_article_likes_table.py
   ```

2. 前端需要确保 API 基础 URL 配置正确

3. 点赞数实时计算，适合小数据量场景

## 后续优化建议

- [ ] 大数据量时考虑缓存点赞数
- [ ] 添加用户点赞历史页面
- [ ] 支持查看点赞者列表
- [ ] 添加反作弊机制
