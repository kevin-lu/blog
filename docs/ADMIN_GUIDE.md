# 博客管理后台使用指南

## 概述

当前后台由两个应用组成：

- `backend/`：Flask API，默认接口前缀 `/api/v1`
- `frontend/`：Vue 3 + Vite 管理端与博客前端

旧的根目录 Nuxt 单体博客项目已经移除，本指南只适用于当前 Flask + Vite 架构。

## 开发启动

### 1. 启动后端

```bash
cd backend
venv/bin/python run.py
```

如果 `5000` 端口被占用，可以改用：

```bash
cd backend
PORT=5001 venv/bin/python -c "from app import create_app; app = create_app('development'); app.run(host='127.0.0.1', port=5001, debug=True, use_reloader=False)"
```

### 2. 启动前端

```bash
cd frontend
npm run dev
```

默认访问地址：

- 前端：`http://localhost:5173`
- 管理后台登录页：`http://localhost:5173/admin/login`
- 后端 API：`http://127.0.0.1:5000/api/v1`

本机如果已按 [dev-startup.md](/Users/luzengbiao/traeProjects/blog/blog/docs/dev-startup.md) 启动过一次，则当前实际后端端口可能是 `5001`。

## 管理员账号

创建管理员：

```bash
cd backend
venv/bin/python scripts/create_admin.py
```

登录接口使用 JWT，前端会把 `access_token` 和 `refresh_token` 保存在本地存储中，并在请求头里附带 `Bearer` token。

## 目录结构

```text
blog/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   ├── models/
│   │   ├── utils/
│   │   └── config.py
│   ├── scripts/
│   ├── instance/
│   └── run.py
├── frontend/
│   ├── src/api/
│   ├── src/views/admin/
│   ├── src/components/
│   └── vite.config.js
└── docs/
```

## 当前可用功能

- 登录、登出、刷新 token、读取当前用户
- 文章列表、详情、新建、编辑、删除
- 分类列表、新建、编辑、删除
- 标签列表、新建、编辑、删除
- 评论列表、通过、拒绝、删除
- 站点配置读取与更新
- 图片/文件上传

## API 对照

- 认证：`POST /api/v1/auth/login`、`POST /api/v1/auth/logout`、`POST /api/v1/auth/refresh`、`GET /api/v1/auth/me`
- 文章：`GET/POST /api/v1/articles`、`GET/PUT/DELETE /api/v1/articles/<slug>`
- 分类：`GET/POST /api/v1/categories`、`PUT/DELETE /api/v1/categories/<id>`
- 标签：`GET/POST /api/v1/tags`、`PUT/DELETE /api/v1/tags/<id>`
- 评论：`GET /api/v1/comments`、`PUT /api/v1/comments/<id>/approve`、`PUT /api/v1/comments/<id>/reject`、`DELETE /api/v1/comments/<id>`
- 配置：`GET/PUT /api/v1/settings`
- 上传：`POST /api/v1/upload`

## 环境与数据说明

- Flask 默认 SQLite 库为 `backend/instance/blog.db`
- 根目录 `blog.db` 目前仍保留旧文章数据，不再被当前 Flask 应用直接使用
- 前端默认通过 `/api/v1` 访问接口，开发环境由 Vite 代理到 Flask 服务

## 补充

- 服务启动和本次清理过程见 [dev-startup.md](/Users/luzengbiao/traeProjects/blog/blog/docs/dev-startup.md)
- `docs/superpowers/` 下的文档是历史规格与计划，不代表当前运行架构
