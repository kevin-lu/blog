## ADDED Requirements

### Requirement: 文章管理 API

系统应提供完整的博客文章 CRUD 接口，支持创建、读取、更新、删除文章，支持按分类、标签筛选。

#### Scenario: 获取文章列表
- **WHEN** 用户请求 `GET /api/v1/articles?page=1&limit=10`
- **THEN** 系统返回分页的文章列表，包含文章标题、摘要、发布时间、作者信息

#### Scenario: 获取文章详情
- **WHEN** 用户请求 `GET /api/v1/articles/{slug}`
- **THEN** 系统返回完整的文章内容，包括正文、分类、标签、评论列表

#### Scenario: 创建新文章
- **WHEN** 管理员发送 `POST /api/v1/articles` 携带文章数据
- **THEN** 系统创建文章并返回创建成功响应

#### Scenario: 更新文章
- **WHEN** 管理员发送 `PUT /api/v1/articles/{slug}` 携带更新数据
- **THEN** 系统更新文章并返回更新后的文章数据

#### Scenario: 删除文章
- **WHEN** 管理员发送 `DELETE /api/v1/articles/{slug}`
- **THEN** 系统删除文章并返回删除成功响应

#### Scenario: 按分类筛选文章
- **WHEN** 用户请求 `GET /api/v1/articles?category=tech`
- **THEN** 系统返回该分类下的所有文章

#### Scenario: 按标签筛选文章
- **WHEN** 用户请求 `GET /api/v1/articles?tag=python`
- **THEN** 系统返回包含该标签的所有文章

### Requirement: 分类管理 API

系统应提供分类的 CRUD 接口，支持分类的创建、编辑、删除，支持查看分类下的文章列表。

#### Scenario: 获取分类列表
- **WHEN** 用户请求 `GET /api/v1/categories`
- **THEN** 系统返回所有分类及其文章数量

#### Scenario: 创建分类
- **WHEN** 管理员发送 `POST /api/v1/categories` 携带分类名称
- **THEN** 系统创建分类并返回创建成功响应

#### Scenario: 删除分类
- **WHEN** 管理员发送 `DELETE /api/v1/categories/{id}`
- **THEN** 系统删除分类，该分类下的文章归类为"未分类"

### Requirement: 标签管理 API

系统应提供标签的 CRUD 接口，支持标签的创建、编辑、删除，支持查看标签下的文章列表。

#### Scenario: 获取标签列表
- **WHEN** 用户请求 `GET /api/v1/tags`
- **THEN** 系统返回所有标签及其使用次数

#### Scenario: 创建标签
- **WHEN** 管理员发送 `POST /api/v1/tags` 携带标签名称
- **THEN** 系统创建标签并返回创建成功响应

#### Scenario: 删除标签
- **WHEN** 管理员发送 `DELETE /api/v1/tags/{id}`
- **THEN** 系统删除标签，相关文章的标签关联被移除

### Requirement: 评论管理 API

系统应提供评论管理接口，支持获取评论列表、审核评论、删除评论。

#### Scenario: 获取评论列表
- **WHEN** 用户请求 `GET /api/v1/comments?article={slug}`
- **THEN** 系统返回该文章的评论列表

#### Scenario: 删除评论
- **WHEN** 管理员发送 `DELETE /api/v1/comments/{id}`
- **THEN** 系统删除评论并返回删除成功响应

### Requirement: 站点设置 API

系统应提供站点设置接口，支持获取和更新站点配置信息。

#### Scenario: 获取站点设置
- **WHEN** 用户请求 `GET /api/v1/settings`
- **THEN** 系统返回站点配置信息，包括站点名称、描述、SEO 设置等

#### Scenario: 更新站点设置
- **WHEN** 管理员发送 `PUT /api/v1/settings` 携带配置数据
- **THEN** 系统更新配置并返回更新成功响应
