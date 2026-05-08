# 博客管理后台设计文档

## 项目概述

为个人技术博客创建独立的后台管理系统，提供文章管理、分类标签管理、评论管理和站点配置功能。使用 Vercel Postgres 作为数据库，与博客一起部署到 Vercel。

**创建日期：** 2026-05-08  
**状态：** 待实现

---

## 技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 前端框架 | Nuxt.js | 3.x | 复用现有博客框架 |
| 管理后台 UI | Naive UI | 2.38.x | 轻量、现代、中文友好 |
| 语言 | TypeScript | 5.x | 类型安全 |
| 状态管理 | Pinia | 2.1.x | Vue 3 状态管理 |
| HTTP 客户端 | Axios | 1.6.x | API 请求 |
| 富文本编辑器 | Tiptap | 2.0.x | Markdown 支持 |
| 数据库 | Vercel Postgres | 15.x | 托管 PostgreSQL |
| ORM | Drizzle ORM | 0.29.x | 类型安全 ORM |
| 认证 | JWT + bcrypt | - | Token 认证 |
| 部署 | Vercel | - | 与博客一起部署 |

---

## 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        博客前端 (Nuxt.js)                        │
│                     / (public)                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   管理后台 (/admin)                      │   │
│   │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│   │   │  登录页  │ │ 文章管理 │ │ 分类管理 │ │ 标签管理 │  │   │
│   │   └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│   │   ┌──────────┐ ┌──────────┐ ┌──────────┐                │   │
│   │   │评论管理  │ │站点配置  │ │仪表盘    │                │   │
│   │   └──────────┘ └──────────┘ └──────────┘                │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API 层 (Nuxt Server Routes)                   │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│   │/api/admin│ │/api/admin│ │/api/admin│ │/api/admin│         │
│   │  /auth   │ │  /posts  │ │/categories│ │  /tags   │         │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐                      │
│   │/api/admin│ │/api/admin│ │/api/admin│                      │
│   │/comments │ │/settings │ │/dashboard│                      │
│   └──────────┘ └──────────┘ └──────────┘                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     数据持久层                                   │
│   ┌─────────────────────────┐    ┌─────────────────────────┐   │
│   │    Vercel Postgres       │    │      Sanity CMS         │   │
│   │   (管理数据存储)         │    │    (博客内容存储)        │   │
│   │                         │    │                         │   │
│   │ - admins (管理员)       │    │ - articles (文章)       │   │
│   │ - site_settings (配置)  │    │ - categories (分类)     │   │
│   │ - comments (评论元数据) │    │ - tags (标签)           │   │
│   │ - operation_logs (日志) │    │ - series (系列)         │   │
│   └─────────────────────────┘    └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 目录结构

```
blog/
├── app/                          # 现有博客应用
│   └── ...
├── admin/                        # 【新增】管理后台
│   ├── components/
│   │   ├── common/               # 通用组件
│   │   │   ├── AdminHeader.vue
│   │   │   ├── AdminSidebar.vue
│   │   │   ├── Pagination.vue
│   │   │   └── LoadingMask.vue
│   │   ├── posts/                # 文章管理组件
│   │   │   ├── PostList.vue
│   │   │   ├── PostForm.vue
│   │   │   ├── PostFilters.vue
│   │   │   └── PostPreview.vue
│   │   ├── categories/
│   │   ├── tags/
│   │   ├── comments/
│   │   └── settings/
│   ├── composables/
│   │   ├── useAuth.ts
│   │   ├── usePosts.ts
│   │   ├── useCategories.ts
│   │   ├── useTags.ts
│   │   ├── useComments.ts
│   │   └── useSettings.ts
│   ├── layouts/
│   │   └── admin.vue
│   ├── pages/
│   │   ├── login.vue
│   │   ├── dashboard.vue
│   │   ├── posts/
│   │   │   ├── index.vue
│   │   │   ├── new.vue
│   │   │   └── [id].vue
│   │   ├── categories/
│   │   ├── tags/
│   │   ├── comments/
│   │   └── settings/
│   ├── stores/
│   │   ├── auth.ts
│   │   └── app.ts
│   ├── types/
│   │   └── admin.ts
│   └── utils/
│       ├── api.ts
│       └── validators.ts
├── server/
│   ├── routes/
│   │   └── api/
│   │       └── admin/
│   │           ├── auth/
│   │           │   ├── login.post.ts
│   │           │   ├── logout.post.ts
│   │           │   └── me.get.ts
│   │           ├── posts/
│   │           ├── categories/
│   │           ├── tags/
│   │           ├── comments/
│   │           └── settings/
│   ├── middleware/
│   │   └── admin-auth.ts
│   ├── database/
│   │   ├── postgres.ts           # Postgres 连接
│   │   ├── schema/
│   │   │   ├── admins.ts
│   │   │   ├── siteSettings.ts
│   │   │   ├── comments.ts
│   │   │   └── operationLogs.ts
│   │   └── migrations/
│   │       └── 001_initial.sql
│   └── utils/
│       ├── jwt.ts
│       └── password.ts
├── admin.config.ts
├── drizzle.config.ts
└── package.json
```

---

## 核心功能

### 1. 认证系统

**功能描述：**
- 管理员账号密码登录
- JWT Token 认证（7 天有效期）
- 登录状态持久化
- 路由守卫保护

**数据流：**
```
登录页面 → POST /api/admin/auth/login → 验证密码 → 生成 JWT → 返回 token
                                              ↓
                                       存储到 localStorage + Pinia
                                              ↓
                                       跳转到仪表盘
                                              ↓
后续请求携带 Authorization: Bearer <token>
```

**API 接口：**

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | /api/admin/auth/login | 登录 | ❌ |
| POST | /api/admin/auth/logout | 登出 | ✅ |
| GET | /api/admin/auth/me | 获取当前用户信息 | ✅ |

### 2. 文章管理

**功能描述：**
- 文章列表展示（分页、搜索、筛选）
- 新建文章
- 编辑文章
- 删除文章
- 批量操作
- 草稿自动保存

**数据流：**
```
文章管理页面 → GET /api/admin/posts → 查询数据库 → 返回文章列表
                    ↓
              展示表格（封面图、标题、分类、时间、状态）
                    ↓
              搜索/筛选 → 重新请求 API
                    ↓
              点击编辑 → GET /api/admin/posts/:id
                    ↓
              文章编辑器 → 保存 → POST/PUT /api/admin/posts
```

**API 接口：**

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /api/admin/posts | 获取文章列表（分页、搜索、筛选） | ✅ |
| GET | /api/admin/posts/:id | 获取单篇文章详情 | ✅ |
| POST | /api/admin/posts | 创建新文章 | ✅ |
| PUT | /api/admin/posts/:id | 更新文章 | ✅ |
| DELETE | /api/admin/posts/:id | 删除文章 | ✅ |
| POST | /api/admin/posts/batch-delete | 批量删除 | ✅ |

**文章数据结构：**
```typescript
interface Post {
  id: number;
  title: string;
  slug: string;
  excerpt?: string;
  content: string;
  coverImage?: string;
  categoryId: number;
  category?: Category;
  tagIds?: number[];
  tags?: Tag[];
  publishedAt: string;
  updatedAt: string;
  featured: boolean;
  order?: number;
  seriesId?: number;
  status: 'draft' | 'published';
}
```

### 3. 分类管理

**功能描述：**
- 分类列表展示
- 新建分类
- 编辑分类
- 删除分类（检查关联文章）
- 分类文章数量统计

**API 接口：**

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /api/admin/categories | 获取分类列表 | ✅ |
| GET | /api/admin/categories/:id | 获取分类详情 | ✅ |
| POST | /api/admin/categories | 创建分类 | ✅ |
| PUT | /api/admin/categories/:id | 更新分类 | ✅ |
| DELETE | /api/admin/categories/:id | 删除分类 | ✅ |

**分类数据结构：**
```typescript
interface Category {
  id: number;
  title: string;
  slug: string;
  description?: string;
  articleCount?: number;
  createdAt: string;
  updatedAt: string;
}
```

### 4. 标签管理

**功能描述：**
- 标签列表展示
- 新建标签
- 编辑标签
- 删除标签（检查关联文章）
- 标签文章数量统计

**API 接口：**

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /api/admin/tags | 获取标签列表 | ✅ |
| GET | /api/admin/tags/:id | 获取标签详情 | ✅ |
| POST | /api/admin/tags | 创建标签 | ✅ |
| PUT | /api/admin/tags/:id | 更新标签 | ✅ |
| DELETE | /api/admin/tags/:id | 删除标签 | ✅ |

**标签数据结构：**
```typescript
interface Tag {
  id: number;
  title: string;
  slug: string;
  articleCount?: number;
  createdAt: string;
  updatedAt: string;
}
```

### 5. 评论管理

**功能描述：**
- 评论列表展示（按文章分组）
- 评论审核（通过/拒绝）
- 评论置顶
- 评论删除
- 评论元数据管理（Giscus 评论的本地元数据）

**API 接口：**

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /api/admin/comments | 获取评论列表（分页、筛选） | ✅ |
| PUT | /api/admin/comments/:id/approve | 审核通过 | ✅ |
| PUT | /api/admin/comments/:id/reject | 审核拒绝 | ✅ |
| PUT | /api/admin/comments/:id/pin | 置顶/取消置顶 | ✅ |
| DELETE | /api/admin/comments/:id | 删除评论 | ✅ |

**评论数据结构：**
```typescript
interface Comment {
  id: number;
  articleSlug: string;
  articleTitle?: string;
  githubId?: string;
  status: 'pending' | 'approved' | 'rejected';
  isPinned: boolean;
  createdAt: string;
  updatedAt: string;
}
```

### 6. 站点配置

**功能描述：**
- 站点基本信息配置（标题、描述、作者）
- 社交链接管理
- 配置项读取和更新
- 与 Sanity 站点设置同步

**API 接口：**

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /api/admin/settings | 获取所有配置项 | ✅ |
| GET | /api/admin/settings/:key | 获取单个配置项 | ✅ |
| PUT | /api/admin/settings/:key | 更新配置项 | ✅ |
| POST | /api/admin/settings/sync-sanity | 同步到 Sanity | ✅ |

**配置项数据结构：**
```typescript
interface SiteSetting {
  id: number;
  keyName: string;
  keyValue?: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}
```

**预定义配置项：**
- `site.title` - 站点标题
- `site.description` - 站点描述
- `site.author` - 作者名
- `site.avatar` - 头像 URL
- `site.bio` - 个人简介
- `social.github` - GitHub 链接
- `social.twitter` - Twitter 链接
- `social.weibo` - 微博链接

### 7. 仪表盘

**功能描述：**
- 数据统计（文章总数、分类数、标签数、评论数）
- 最近文章列表
- 快速操作入口
- 系统状态信息

**API 接口：**

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | /api/admin/dashboard/stats | 获取统计数据 | ✅ |
| GET | /api/admin/dashboard/recent-posts | 获取最近文章 | ✅ |

---

## 数据库设计

### 表结构

#### admins (管理员表)

```sql
CREATE TABLE admins (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email VARCHAR(100),
  avatar VARCHAR(255),
  role VARCHAR(20) DEFAULT 'admin',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admins_username ON admins(username);
```

#### site_settings (站点配置表)

```sql
CREATE TABLE site_settings (
  id SERIAL PRIMARY KEY,
  key_name VARCHAR(100) UNIQUE NOT NULL,
  key_value TEXT,
  description VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_site_settings_key ON site_settings(key_name);
```

#### comments (评论元数据表)

```sql
CREATE TABLE comments (
  id SERIAL PRIMARY KEY,
  article_slug VARCHAR(100) NOT NULL,
  github_id VARCHAR(50),
  status VARCHAR(20) DEFAULT 'pending',
  is_pinned BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_comments_article_slug ON comments(article_slug);
CREATE INDEX idx_comments_status ON comments(status);
```

#### operation_logs (操作日志表)

```sql
CREATE TABLE operation_logs (
  id SERIAL PRIMARY KEY,
  admin_id INTEGER NOT NULL REFERENCES admins(id),
  action VARCHAR(50) NOT NULL,
  resource VARCHAR(50),
  resource_id INTEGER,
  details JSONB,
  ip_address VARCHAR(45),
  user_agent VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_operation_logs_admin_id ON operation_logs(admin_id);
CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at);
CREATE INDEX idx_operation_logs_details ON operation_logs USING GIN (details);
```

### Drizzle ORM Schema

```typescript
// server/database/schema/admins.ts
import { pgTable, serial, varchar, timestamp } from 'drizzle-orm/pg-core';

export const admins = pgTable('admins', {
  id: serial('id').primaryKey(),
  username: varchar('username', { length: 50 }).unique().notNull(),
  passwordHash: varchar('password_hash', { length: 255 }).notNull(),
  email: varchar('email', { length: 100 }),
  avatar: varchar('avatar', { length: 255 }),
  role: varchar('role', { length: 20 }).default('admin'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
});

// server/database/schema/siteSettings.ts
import { pgTable, serial, varchar, text, timestamp } from 'drizzle-orm/pg-core';

export const siteSettings = pgTable('site_settings', {
  id: serial('id').primaryKey(),
  keyName: varchar('key_name', { length: 100 }).unique().notNull(),
  keyValue: text('key_value'),
  description: varchar('description', { length: 255 }),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
});

// server/database/schema/comments.ts
import { pgTable, serial, varchar, boolean, timestamp } from 'drizzle-orm/pg-core';

export const comments = pgTable('comments', {
  id: serial('id').primaryKey(),
  articleSlug: varchar('article_slug', { length: 100 }).notNull(),
  githubId: varchar('github_id', { length: 50 }),
  status: varchar('status', { length: 20 }).default('pending'),
  isPinned: boolean('is_pinned').default(false),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
});

// server/database/schema/operationLogs.ts
import { pgTable, serial, varchar, integer, jsonb, timestamp } from 'drizzle-orm/pg-core';
import { admins } from './admins';

export const operationLogs = pgTable('operation_logs', {
  id: serial('id').primaryKey(),
  adminId: integer('admin_id').notNull().references(() => admins.id),
  action: varchar('action', { length: 50 }).notNull(),
  resource: varchar('resource', { length: 50 }),
  resourceId: integer('resource_id'),
  details: jsonb('details'),
  ipAddress: varchar('ip_address', { length: 45 }),
  userAgent: varchar('user_agent', { length: 255 }),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
});
```

---

## UI 设计

### 登录页面

**布局：**
- 居中卡片（宽 400px）
- 背景渐变（博客主题色）
- Logo + 标题
- 用户名输入框
- 密码输入框
- 登录按钮
- 错误提示（红色文字）

**交互：**
- 表单验证（必填项检查）
- 登录中 loading 状态
- 登录成功跳转仪表盘
- 登录失败显示错误信息

### 管理后台布局

**侧边栏导航：**
```
┌─────────────────────┐
│   📊 仪表盘         │
├─────────────────────┤
│   📝 文章管理       │
│     - 所有文章      │
│     - 新建文章      │
├─────────────────────┤
│   📁 分类管理       │
├─────────────────────┤
│   🏷️ 标签管理       │
├─────────────────────┤
│   💬 评论管理       │
├─────────────────────┤
│   ⚙️ 站点配置       │
└─────────────────────┘
```

**顶部导航栏：**
```
┌────────────────────────────────────────────────────────────┐
│  面包屑导航                    用户头像 ▼  退出登录         │
└────────────────────────────────────────────────────────────┘
```

### 文章列表页面

**表格列：**
- 封面图（缩略图 60x40）
- 标题（可点击编辑）
- 分类（标签形式）
- 发布时间
- 状态（草稿/已发布）
- 操作（编辑、删除）

**筛选区：**
- 搜索框（标题、slug）
- 分类下拉选择
- 状态下拉选择（全部/草稿/已发布）
- 搜索按钮、重置按钮

**批量操作：**
- 全选复选框
- 批量删除按钮
- 批量发布按钮

**分页：**
- 每页 20 条
- 页码显示
- 上一页/下一页

### 文章编辑页面

**布局：**
```
┌─────────────────────────────────────────────────────────────┐
│  返回  |  文章标题输入框                      [保存] [预览]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────┐  ┌─────────────────────────────┐ │
│  │                      │  │                             │ │
│  │   富文本编辑器       │  │      实时预览               │ │
│  │   (Markdown 支持)     │  │                             │ │
│  │                      │  │                             │ │
│  └──────────────────────┘  └─────────────────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  别名：[slug 输入]        分类：[下拉选择]                  │
│  标签：[多选下拉]         发布时间：[日期选择器]            │
│  排序号：[数字输入]       精选文章：[开关]                  │
│  封面图：[上传组件]                                        │
└─────────────────────────────────────────────────────────────┘
```

**编辑器功能：**
- Markdown 语法支持
- 富文本工具栏（加粗、斜体、链接、图片、代码块等）
- 图片拖拽上传
- 代码块语法高亮
- 自动保存草稿（每 30 秒）
- 快捷键（Ctrl+S 保存）

---

## 安全措施

### 1. 密码安全
- 使用 bcrypt 加密（cost factor: 12）
- 密码长度至少 8 位
- 密码强度检查

### 2. Token 安全
- JWT Token 有效期 7 天
- Token 刷新机制
- 登出时加入黑名单

### 3. API 安全
- 所有 `/api/admin/*` 路由需要认证（登录接口除外）
- CORS 限制（仅允许同域名）
- 速率限制（登录接口 5 次/分钟）

### 4. 数据库安全
- 使用 Drizzle ORM 参数化查询（防止 SQL 注入）
- 数据库连接字符串存储在环境变量

### 5. 操作审计
- 记录所有管理操作到 operation_logs
- 记录操作者、时间、IP 地址、操作详情

---

## 环境变量

创建 `.env` 文件：

```bash
# Vercel Postgres
POSTGRES_URL="postgres://..."

# JWT 配置
JWT_SECRET="your-secret-key-change-in-production"
JWT_EXPIRES_IN="7d"

# Sanity (现有)
NUXT_PUBLIC_SANITY_PROJECT_ID=xxx
NUXT_PUBLIC_SANITY_DATASET=production
NUXT_PUBLIC_SANITY_API_VERSION=2024-05-01
SANITY_API_READ_TOKEN=xxx

# Giscus (现有)
NUXT_PUBLIC_GISCUS_REPO=username/repo
NUXT_PUBLIC_GISCUS_REPO_ID=xxx
NUXT_PUBLIC_GISCUS_CATEGORY=Comments
NUXT_PUBLIC_GISCUS_CATEGORY_ID=xxx
```

---

## 部署配置

### Vercel 配置

创建 `vercel.json`：

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nuxtjs",
  "outputDirectory": ".output"
}
```

### 数据库迁移

使用 Drizzle Kit 进行数据库迁移：

```bash
# 生成本地迁移文件
npx drizzle-kit generate:pg

# 推送到 Vercel Postgres
npx drizzle-kit push:pg
```

---

## 性能目标

- 首屏加载时间 ≤ 2s
- API 响应时间 ≤ 200ms
- 列表页面分页加载
- 图片懒加载
- 组件按需加载

---

## 测试策略

### 单元测试
- 工具函数测试（密码加密、JWT 生成）
- 组件单元测试

### 集成测试
- API 接口测试
- 认证流程测试

### E2E 测试
- 登录流程
- 文章 CRUD 流程

---

## 后续扩展（可选）

- [ ] 多管理员角色和权限
- [ ] 操作日志查看界面
- [ ] 数据导入导出
- [ ] 文章版本历史
- [ ] 定时发布
- [ ] 文章统计（阅读量、点赞数）
- [ ] 站内消息通知
- [ ] 移动端适配优化

---

**文档版本：** 1.0  
**创建日期：** 2026-05-08  
**状态：** 待实现
