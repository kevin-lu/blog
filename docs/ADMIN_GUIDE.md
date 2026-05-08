# 博客管理后台使用指南

## 📋 项目概述

这是一个基于 Nuxt.js 3.x + Naive UI 2.x + Vercel Postgres 的独立博客管理后台系统。

## 🚀 快速开始

### 1. 环境配置

复制环境变量模板并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加 Vercel Postgres 连接字符串和 JWT 密钥：

```env
POSTGRES_URL="postgres://..."
JWT_SECRET="your-secret-key-change-in-production"
JWT_EXPIRES_IN="7d"
```

### 2. 安装依赖

```bash
npm install
```

### 3. 数据库迁移

```bash
# 生成迁移文件（已完成）
npm run db:generate

# 推送 schema 到数据库
npm run db:push
```

### 4. 创建管理员账号

```bash
npm run create-admin <用户名> <密码> [邮箱]
```

示例：
```bash
npm run create-admin admin 123456 admin@example.com
```

### 5. 启动开发服务器

```bash
npm run dev
```

访问 `http://localhost:3002/admin/login` 登录管理后台。

## 📁 项目结构

```
blog/
├── app/                          # Nuxt 应用目录
│   ├── components/admin/         # 管理后台组件
│   ├── composables/              # 组合式函数
│   ├── layouts/                  # 布局文件
│   ├── pages/admin/              # 管理后台页面
│   ├── stores/                   # Pinia 状态管理
│   └── utils/                    # 工具函数
├── server/                       # 服务端目录
│   ├── api/admin/                # 管理后台 API
│   │   ├── auth/                 # 认证相关
│   │   ├── articles/             # 文章管理
│   │   ├── categories/           # 分类管理
│   │   ├── tags/                 # 标签管理
│   │   ├── comments/             # 评论管理
│   │   └── settings/             # 站点配置
│   ├── database/                 # 数据库相关
│   │   ├── schema/               # 数据库 Schema
│   │   └── migrations/           # 数据库迁移
│   ├── middleware/               # 中间件
│   └── utils/                    # 服务端工具
├── types/                        # TypeScript 类型定义
├── scripts/                      # 脚本文件
├── docs/                         # 文档目录
│   └── superpowers/
│       ├── specs/                # 规格说明
│       └── plans/                # 实现计划
└── admin.config.ts               # 管理后台配置
```

## 🗄️ 数据库表结构

### 核心表

- **admins** - 管理员信息
- **article_meta** - 文章元数据
- **categories** - 文章分类
- **tags** - 文章标签
- **article_categories** - 文章分类关联
- **article_tags** - 文章标签关联
- **comments** - 评论管理
- **site_settings** - 站点配置
- **operation_logs** - 操作日志

## 🔐 认证机制

- 使用 JWT 进行身份验证
- Token 有效期 7 天（可配置）
- 密码使用 bcryptjs 加密（12 轮）
- 中间件自动验证 `/api/admin/*` 请求

## 📝 功能清单

### ✅ 已完成功能

1. **用户认证**
   - 登录/登出
   - JWT Token 管理
   - 自动跳转

2. **仪表盘**
   - 统计卡片（文章数、分类数、评论数、浏览量）
   - 快捷操作入口
   - 最近文章列表

3. **文章管理**
   - 文章列表（分页、筛选、搜索）
   - 新建文章
   - 编辑文章
   - 删除文章
   - 文章状态管理（草稿/已发布）

4. **分类和标签管理**
   - 分类列表
   - 新建分类
   - 删除分类
   - 标签列表
   - 新建标签
   - 删除标签

5. **评论管理**
   - 评论列表（分页、筛选）
   - 审核评论（通过/拒绝）
   - 删除评论
   - 评论置顶

6. **站点配置**
   - 站点标题/描述/关键词
   - 作者信息
   - GitHub 集成
   - 每页文章数
   - 评论开关

## 🔧 API 接口

### 认证接口

- `POST /api/admin/auth/login` - 登录
- `GET /api/admin/auth/me` - 获取当前用户
- `POST /api/admin/auth/logout` - 登出

### 文章接口

- `GET /api/admin/articles` - 获取文章列表
- `GET /api/admin/articles/:slug` - 获取单篇文章
- `POST /api/admin/articles` - 创建文章
- `PUT /api/admin/articles/:slug` - 更新文章
- `DELETE /api/admin/articles/:slug` - 删除文章

### 分类接口

- `GET /api/admin/categories` - 获取分类列表
- `POST /api/admin/categories` - 创建分类

### 标签接口

- `GET /api/admin/tags` - 获取标签列表
- `POST /api/admin/tags` - 创建标签

### 评论接口

- `GET /api/admin/comments` - 获取评论列表
- `PUT /api/admin/comments/:id` - 更新评论状态
- `DELETE /api/admin/comments/:id` - 删除评论

### 配置接口

- `GET /api/admin/settings` - 获取站点配置
- `PUT /api/admin/settings` - 更新站点配置

## 🎨 技术栈

- **前端框架**: Nuxt.js 3.x
- **UI 组件库**: Naive UI 2.x
- **状态管理**: Pinia 2.x
- **HTTP 客户端**: Axios
- **数据库**: Vercel Postgres
- **ORM**: Drizzle ORM
- **认证**: JWT + bcryptjs
- **表单验证**: Zod

## 📦 NPM 脚本

```bash
# 开发
npm run dev              # 启动开发服务器

# 构建
npm run build            # 构建生产版本
npm run generate         # 静态生成
npm run preview          # 预览生产构建

# 数据库
npm run db:generate      # 生成迁移文件
npm run db:push          # 推送 schema 到数据库

# 工具
npm run create-admin     # 创建管理员账号
```

## 🔒 安全建议

1. **生产环境配置**
   - 修改 `JWT_SECRET` 为强随机密钥
   - 启用 HTTPS
   - 配置 CORS 白名单

2. **密码策略**
   - 至少 8 位
   - 包含大小写字母和数字
   - 定期更换

3. **数据库**
   - 使用只读/写入分离
   - 定期备份
   - 限制访问 IP

## 🚧 后续优化建议

1. **功能增强**
   - 富文本编辑器集成（Tiptap）
   - 图片上传功能
   - 批量操作
   - 数据导出/导入

2. **性能优化**
   - 列表虚拟滚动
   - 图片懒加载
   - API 响应缓存

3. **监控和日志**
   - 操作日志记录
   - 错误监控
   - 性能监控

## 📄 License

MIT
