## 1. 后端数据模型

- [ ] 1.1 创建 ArticleLike 模型（backend/app/models/like.py）
- [ ] 1.2 在 backend/app/models/__init__.py 中导出新模型
- [ ] 1.3 创建数据库迁移脚本（backend/scripts/add_article_likes_table.py）
- [ ] 1.4 执行迁移脚本创建 article_likes 表

## 2. 后端 API 实现

- [ ] 2.1 修改 Article.to_dict() 添加 like_count 字段
- [ ] 2.2 实现点赞 API 端点 POST /api/v1/articles/:id/like
- [ ] 2.3 实现取消点赞 API 端点 DELETE /api/v1/articles/:id/unlike
- [ ] 2.4 添加 IP 限流装饰器（10 次/分钟）
- [ ] 2.5 添加异常处理（重复点赞返回 409，文章不存在返回 404）

## 3. 后端测试

- [ ] 3.1 编写点赞 API 单元测试
- [ ] 3.2 编写取消点赞 API 单元测试
- [ ] 3.3 编写重复点赞测试（验证 409 响应）
- [ ] 3.4 编写限流测试（验证 429 响应）
- [ ] 3.5 运行所有测试确保通过

## 4. 前端组件开发

- [ ] 4.1 创建点赞 API 调用方法（frontend/src/api/like.ts）
- [ ] 4.2 创建 ArticleLike.vue 组件
- [ ] 4.3 实现 optimistic UI 更新逻辑
- [ ] 4.4 实现加载状态和错误处理
- [ ] 4.5 添加样式（未点赞/已点赞状态，响应式布局）

## 5. 前端集成

- [ ] 5.1 在 PostDetail.vue 中集成点赞组件
- [ ] 5.2 验证文章详情页显示点赞数和按钮
- [ ] 5.3 测试点赞/取消点赞交互流程
- [ ] 5.4 测试未登录用户点赞功能

## 6. 端到端测试

- [ ] 6.1 编写点赞功能 E2E 测试（frontend/e2e/like.spec.ts）
- [ ] 6.2 运行 E2E 测试验证完整流程
- [ ] 6.3 修复发现的 bug

## 7. 文档和收尾

- [ ] 7.1 更新 API 文档（添加点赞端点说明）
- [ ] 7.2 编写功能使用说明
- [ ] 7.3 代码审查和清理
- [ ] 7.4 验证所有测试通过
- [ ] 7.5 准备发布
