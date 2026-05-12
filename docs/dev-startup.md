# 开发服务启动记录

## 当前保留的服务

- `backend`: Flask API 后端，地址 `http://127.0.0.1:5001`
- `frontend`: Vue 3 + Vite 前端，地址 `http://localhost:5173`

旧的根目录 Nuxt 单体服务曾在排查时启动到 `http://localhost:3002/`，确认属于旧纯 Nuxt 博客项目后已经停止并删除，不再作为当前启动项。

## 本次启动过程

1. 检查项目结构，确认当前保留 `backend/` 和 `frontend/` 两个应用。
2. 读取 `backend/README.md` 和 `frontend/package.json`，确认后端使用 Flask、前端使用 Vite。
3. 检查端口占用，发现 `5000` 被本机已有进程占用，所以 Flask backend 改用 `5001`。
4. 启动 backend 时遇到 `flask_limiter` 导入错误，修复为从 `app.extensions` 导入 `limiter`。
5. 启动并探活 Flask backend。
6. 启动并探活 Vite frontend。
7. 删除旧根目录 Nuxt 单体项目源码、Nuxt/Sanity/Drizzle 配置、旧构建产物和根目录依赖。
8. 将 frontend 的 API 代理从旧 `3002` 切换到 Flask backend 的 `/api/v1`。

## 启动命令

### Backend

```bash
cd backend
venv/bin/python -c "from app import create_app; app = create_app('development'); app.run(host='127.0.0.1', port=5001, debug=True, use_reloader=False)"
```

### Frontend

```bash
cd frontend
npm run dev
```

## 探活命令

```bash
curl -I http://127.0.0.1:5001/api/v1/articles
curl -I http://localhost:5173/
```

## 备注

- 旧 Nuxt 服务的 `3002` 端口已不再使用。
- 根目录 `blog.db` 保留，因为里面有旧文章数据；当前 Flask 默认库是 `backend/instance/blog.db`。
- 前端默认 API 地址为 `/api/v1`，Vite 代理目标为 `http://127.0.0.1:5001`。
