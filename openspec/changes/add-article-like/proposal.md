## Why

博客文章需要点赞功能，让读者快速表达对文章的喜爱，同时为博主提供内容质量反馈。当前项目已有评论、浏览计数等功能，但缺少简单的点赞互动方式。

## What Changes

- **新增**：文章点赞 API（点赞/取消点赞）
- **新增**：点赞数据模型和数据库表
- **新增**：文章详情页点赞按钮和计数显示
- **新增**：IP 限流防护（10 次/分钟）
- **新增**：支持登录和未登录用户点赞

## Capabilities

### New Capabilities

- `article-like-api`: 点赞 API 端点（POST /articles/:id/like, DELETE /articles/:id/unlike）
- `article-like-model`: 点赞数据模型（ArticleLike 表、关联关系）
- `article-like-ui`: 点赞 UI 组件（点赞按钮、计数显示、交互反馈）

### Modified Capabilities

- `article-api`: 文章详情 API 需要返回点赞数（修改 `to_dict()` 方法）

## Impact

**后端影响：**
- 新增 `ArticleLike` 模型（`backend/app/models/like.py`）
- 新增点赞 API（`backend/app/api/v1/articles.py` 添加端点）
- 修改 `Article.to_dict()` 添加 `like_count` 字段
- 数据库迁移：新增 `article_likes` 表

**前端影响：**
- 新增点赞组件（`frontend/src/components/article/ArticleLike.vue`）
- 修改文章详情页（`frontend/src/views/blog/PostDetail.vue` 添加点赞按钮）
- 新增 API 调用方法（`frontend/src/api/like.ts`）

**数据库影响：**
- 新增 `article_likes` 表（包含 article_id, user_id, session_id, ip_address, created_at）
- 唯一约束：同一用户/会话对同一文章只能点赞一次

**依赖影响：**
- 使用现有 `flask-limiter==3.5.0` 实现 IP 限流
- 使用现有 `Flask-JWT-Extended` 处理登录用户验证
