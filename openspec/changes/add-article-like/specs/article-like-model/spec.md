## ADDED Requirements

### Requirement: 点赞数据模型
系统 SHALL 使用独立的 article_likes 表存储点赞记录，支持防重复点赞。

#### Scenario: 创建点赞记录
- **WHEN** 用户成功点赞文章
- **THEN** 系统在 article_likes 表创建一条记录，包含 article_id、user_id/session_id、ip_address、created_at

#### Scenario: 登录用户唯一性约束
- **WHEN** 同一登录用户尝试对同一篇文章点赞两次
- **THEN** 数据库唯一约束 uq_article_user 阻止重复记录，返回 409 错误

#### Scenario: 未登录用户唯一性约束
- **WHEN** 同一未登录用户（相同 session_id）尝试对同一篇文章点赞两次
- **THEN** 数据库唯一约束 uq_article_session 阻止重复记录，返回 409 错误

#### Scenario: 删除文章时级联删除点赞
- **WHEN** 文章被删除
- **THEN** 该文章的所有点赞记录被级联删除（ON DELETE CASCADE）

### Requirement: 文章点赞数实时计算
系统 SHALL 实时计算文章的点赞数，而非缓存到字段。

#### Scenario: 获取文章详情时返回点赞数
- **WHEN** 客户端请求文章详情 API
- **THEN** 系统返回的文章数据包含 like_count 字段，值为 COUNT(article_likes)

#### Scenario: 点赞后立即更新计数
- **WHEN** 用户成功点赞
- **THEN** 点赞 API 响应中的 like_count 立即 +1

### Requirement: 点赞记录包含必要信息
系统 SHALL 在点赞记录中存储足够的信息用于追踪和防刷。

#### Scenario: 记录登录用户点赞
- **WHEN** 登录用户点赞
- **THEN** 记录包含 user_id（从 JWT token 获取）

#### Scenario: 记录未登录用户点赞
- **WHEN** 未登录用户点赞
- **THEN** 记录包含 session_id（前端生成的 UUID）和 ip_address
