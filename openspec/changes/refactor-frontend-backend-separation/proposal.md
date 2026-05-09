## Why

当前 Nuxt.js 全栈项目存在启动报错问题，架构耦合导致维护和调试困难。通过前后端分离重构，前端采用纯 Vue 3，后端采用 Python Flask，可以提升开发效率、降低部署复杂度、改善代码可维护性。

## What Changes

- **前端架构**: 从 Nuxt.js 全栈框架迁移到 Vue 3 + Vite + Pinia 纯前端架构
- **后端架构**: 从 Nuxt Server API 迁移到 Python Flask + SQLAlchemy
- **API 通信**: 从内部函数调用改为 RESTful API 远程调用
- **认证方式**: 从 Nuxt 中间件认证改为 JWT Token 认证
- **部署方式**: 从单体部署改为前后端完全分离部署
- **新增功能**: Swagger API 文档、监控日志、文件管理、Redis 缓存等

## Capabilities

### New Capabilities

- `backend-api`: Flask 后端 RESTful API 服务，包含文章、分类、标签、评论的 CRUD 接口
- `frontend-vue`: Vue 3 纯前端应用，包含博客展示和管理后台两个子系统
- `jwt-auth`: 基于 JWT 的用户认证系统，支持登录、登出、Token 刷新
- `api-docs`: Swagger/OpenAPI 自动生成的 API 文档系统
- `file-management`: 文件上传、图片压缩、CDN 集成管理
- `monitoring-logging`: 请求日志、慢查询监控、性能指标收集
- `redis-cache`: Redis 缓存层，支持文章列表、热点数据缓存
- `article-search`: 文章全文搜索功能

### Modified Capabilities

- `blog-article`: 从 Nuxt.js SSR 渲染改为 Vue 3 客户端渲染 + API 数据获取
- `admin-dashboard`: 从 Nuxt 内置管理后台改为独立 Vue 3 SPA 应用

## Impact

**受影响代码**:
- 所有 `server/api/` 下的 API 路由需要重写为 Flask routes
- 所有 `app/` 下的 Vue 组件需要适配新的 API 调用方式
- `server/database/` 下的 Drizzle ORM 需要迁移到 SQLAlchemy
- 认证中间件需要重写为 Flask 的 JWT 验证逻辑

**新增依赖**:
- 后端：Flask, SQLAlchemy, Flask-JWT-Extended, Flask-SQLAlchemy, Redis
- 前端：Vue 3, Vite, Pinia, Vue Router, Axios, Naive UI
- 工具：Swagger UI, Gunicorn (生产服务器)

**数据库**:
- 保持 SQLite 数据库不变
- ORM 从 Drizzle 迁移到 SQLAlchemy
- 数据表结构保持不变

**部署**:
- 前端：Vercel/Netlify 静态托管
- 后端：云服务器/Docker 容器
- 数据库：本地文件或云数据库
