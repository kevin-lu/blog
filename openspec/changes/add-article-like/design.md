## Context

博客项目已有评论、浏览计数等互动功能，但缺少简单的点赞功能。根据 grill 阶段的需求审查，需要实现：
- 支持登录和未登录用户点赞
- 实时计算点赞数（非缓存）
- IP 限流防护（10 次/分钟）
- 防重复点赞（数据库唯一约束）

**技术栈约束：**
- 后端：Python/Flask + SQLAlchemy ORM
- 前端：Vue 3 + TypeScript
- 数据库：MySQL
- 限流：flask-limiter（现有依赖）

**参考文档：**
- CONTEXT.md：领域术语定义
- docs/adr/0001-article-like-model.md：数据模型决策
- docs/adr/0002-like-rate-limit.md：限流策略决策

## Goals / Non-Goals

**Goals:**
- 实现文章点赞/取消点赞功能
- 支持登录和未登录用户
- 防止重复点赞和刷赞攻击
- 前端提供流畅的交互体验
- 实时计算点赞数（简单可靠）

**Non-Goals:**
- 点赞用户列表展示（后续迭代）
- 点赞通知功能（后续迭代）
- 点赞排行榜（后续迭代）
- 管理后台点赞统计（后续迭代）
- 缓存点赞数（数据量小，暂不需要）

## Decisions

### 1. 数据模型设计

**决策**：使用独立的 `article_likes` 表，而非在文章表添加字段。

**理由**：
- 支持防重复点赞（唯一约束）
- 便于扩展（点赞用户列表、时间分析）
- 符合现有项目 ORM 模式

**表结构**：
```sql
CREATE TABLE article_likes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    article_id INT NOT NULL,
    user_id INT NULL,
    session_id VARCHAR(100) NULL,
    ip_address VARCHAR(50) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES article_meta(id) ON DELETE CASCADE,
    UNIQUE KEY uq_article_user (article_id, user_id),
    UNIQUE KEY uq_article_session (article_id, session_id)
);
```

**替代方案**：
- 方案 A：在文章表添加 `like_count` 字段
  - 优点：查询性能好
  - 缺点：增加数据一致性复杂度，不支持防重复
  - 不选理由：当前数据量小，实时计算可接受

### 2. 点赞计数策略

**决策**：实时计算 `COUNT(article_likes)`，不缓存到字段。

**理由**：
- 数据量小，性能影响可忽略
- 避免缓存同步问题
- 简化实现

**实现方式**：
- 修改 `Article.to_dict()` 添加计算逻辑
- 或在文章详情 API 中单独查询

**替代方案**：
- 方案 A：Redis 缓存 + 异步更新
  - 不选理由：过度设计，增加复杂度

### 3. 用户标识策略

**决策**：同时支持登录和未登录用户。

- **登录用户**：使用 `user_id`（JWT token 获取）
- **未登录用户**：使用 `session_id`（前端生成 UUID）+ `ip_address`

**理由**：
- 降低点赞门槛
- 保留扩展能力

### 4. 限流策略

**决策**：IP 限流，10 次/分钟。

**实现**：
```python
@bp.route('/articles/<int:id>/like', methods=['POST'])
@limiter.limit("10 per minute", key_func=lambda: request.remote_addr)
def like_article(id):
    ...
```

**替代方案**：
- 方案 A：用户级限流
  - 不选理由：未登录用户无法限流

### 5. API 设计

**决策**：RESTful 风格。

- `POST /api/v1/articles/<id>/like` - 点赞
- `DELETE /api/v1/articles/<id>/unlike` - 取消点赞
- `GET /api/v1/articles/<id>` - 文章详情（返回点赞数）

**响应格式**：
```json
// 点赞成功
{
  "success": true,
  "like_count": 42,
  "liked": true
}

// 已点赞过（409 Conflict）
{
  "error": "Already liked",
  "message": "您已点赞过这篇文章"
}
```

## Risks / Trade-offs

### [风险] 高并发场景下，实时计算可能成为瓶颈

**缓解**：
- 当前数据量小，可接受
- 未来可添加 Redis 缓存
- 数据库索引优化（article_id 索引）

### [风险] 同一 IP 的多个用户共享限流额度

**缓解**：
- 10 次/分钟足够正常使用
- 误判概率低，可接受

### [风险] 未登录用户清除浏览器数据后可再次点赞

**缓解**：
- 结合 IP 限制增加难度
- 无法完全防止，但提高成本
- 业务可接受（非金融场景）

### [权衡] 实时计算 vs 缓存计数

**选择**：实时计算

**理由**：
- 简化实现和数据一致性
- 性能影响可接受
- 可在需要时再优化

## Migration Plan

### 部署步骤

1. **后端模型**：创建 `backend/app/models/like.py`
2. **API 端点**：修改 `backend/app/api/v1/articles.py` 添加点赞端点
3. **数据库迁移**：执行 SQL 迁移脚本创建 `article_likes` 表
4. **前端组件**：创建 `ArticleLike.vue` 组件
5. **集成测试**：验证点赞/取消点赞功能

### 回滚策略

1. 回滚前端代码（移除点赞按钮）
2. 回滚后端代码（移除点赞 API）
3. 删除 `article_likes` 表（可选，保留数据）

## Open Questions

无。需求和技术方案已明确。
