# 博客管理后台实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 为个人技术博客创建独立的后台管理系统，提供文章管理、分类标签管理、评论管理和站点配置功能

**架构：** 基于 Nuxt.js 框架扩展管理后台，使用 Naive UI 作为组件库，Vercel Postgres 作为数据库，通过 Nuxt Server Routes 提供 API，JWT 进行认证

**技术栈：** Nuxt.js 3.x, Naive UI 2.38.x, TypeScript 5.x, Pinia 2.1.x, Vercel Postgres 15.x, Drizzle ORM 0.29.x, JWT, bcryptjs, Tiptap 2.0.x

---

## 文件结构

### 新增文件列表

**依赖配置：**
- `package.json` - 新增依赖
- `drizzle.config.ts` - Drizzle ORM 配置
- `admin.config.ts` - 后台配置

**数据库层：**
- `server/database/postgres.ts` - Postgres 连接
- `server/database/schema/admins.ts` - 管理员表 schema
- `server/database/schema/siteSettings.ts` - 站点配置表 schema
- `server/database/schema/comments.ts` - 评论表 schema
- `server/database/schema/operationLogs.ts` - 操作日志表 schema
- `server/database/schema/index.ts` - Schema 导出
- `server/database/migrations/001_initial.sql` - 初始迁移

**工具函数：**
- `server/utils/jwt.ts` - JWT 工具
- `server/utils/password.ts` - 密码加密工具

**中间件：**
- `server/middleware/admin-auth.ts` - 管理员认证中间件

**API 路由：**
- `server/routes/api/admin/auth/login.post.ts` - 登录 API
- `server/routes/api/admin/auth/logout.post.ts` - 登出 API
- `server/routes/api/admin/auth/me.get.ts` - 获取当前用户 API
- `server/routes/api/admin/posts/index.get.ts` - 文章列表 API
- `server/routes/api/admin/posts/index.post.ts` - 创建文章 API
- `server/routes/api/admin/posts/[id].get.ts` - 文章详情 API
- `server/routes/api/admin/posts/[id].put.ts` - 更新文章 API
- `server/routes/api/admin/posts/[id].delete.ts` - 删除文章 API
- `server/routes/api/admin/categories/index.get.ts` - 分类列表 API
- `server/routes/api/admin/categories/index.post.ts` - 创建分类 API
- `server/routes/api/admin/categories/[id].get.ts` - 分类详情 API
- `server/routes/api/admin/categories/[id].put.ts` - 更新分类 API
- `server/routes/api/admin/categories/[id].delete.ts` - 删除分类 API
- `server/routes/api/admin/tags/index.get.ts` - 标签列表 API
- `server/routes/api/admin/tags/index.post.ts` - 创建标签 API
- `server/routes/api/admin/tags/[id].get.ts` - 标签详情 API
- `server/routes/api/admin/tags/[id].put.ts` - 更新标签 API
- `server/routes/api/admin/tags/[id].delete.ts` - 删除标签 API
- `server/routes/api/admin/comments/index.get.ts` - 评论列表 API
- `server/routes/api/admin/comments/[id].approve.put.ts` - 审核通过 API
- `server/routes/api/admin/comments/[id].pin.put.ts` - 置顶 API
- `server/routes/api/admin/comments/[id].delete.ts` - 删除评论 API
- `server/routes/api/admin/settings/index.get.ts` - 获取配置 API
- `server/routes/api/admin/settings/[key].put.ts` - 更新配置 API
- `server/routes/api/admin/dashboard/stats.get.ts` - 统计数据 API

**管理后台 - 类型：**
- `admin/types/admin.ts` - TypeScript 类型定义

**管理后台 - 工具：**
- `admin/utils/api.ts` - API 客户端
- `admin/utils/validators.ts` - 验证器

**管理后台 - 状态管理：**
- `admin/stores/auth.ts` - 认证状态
- `admin/stores/app.ts` - 应用状态

**管理后台 - 组合式函数：**
- `admin/composables/useAuth.ts` - 认证逻辑
- `admin/composables/usePosts.ts` - 文章管理
- `admin/composables/useCategories.ts` - 分类管理
- `admin/composables/useTags.ts` - 标签管理
- `admin/composables/useComments.ts` - 评论管理
- `admin/composables/useSettings.ts` - 配置管理

**管理后台 - 布局：**
- `admin/layouts/admin.vue` - 后台布局

**管理后台 - 通用组件：**
- `admin/components/common/AdminHeader.vue` - 顶部导航栏
- `admin/components/common/AdminSidebar.vue` - 侧边栏导航
- `admin/components/common/Pagination.vue` - 分页组件
- `admin/components/common/LoadingMask.vue` - 加载遮罩

**管理后台 - 文章组件：**
- `admin/components/posts/PostList.vue` - 文章列表
- `admin/components/posts/PostForm.vue` - 文章表单
- `admin/components/posts/PostFilters.vue` - 文章筛选
- `admin/components/posts/PostPreview.vue` - 文章预览

**管理后台 - 页面：**
- `admin/pages/login.vue` - 登录页
- `admin/pages/dashboard.vue` - 仪表盘
- `admin/pages/posts/index.vue` - 文章列表页
- `admin/pages/posts/new.vue` - 新建文章页
- `admin/pages/posts/[id].vue` - 编辑文章页
- `admin/pages/categories/index.vue` - 分类管理页
- `admin/pages/tags/index.vue` - 标签管理页
- `admin/pages/comments/index.vue` - 评论管理页
- `admin/pages/settings/index.vue` - 站点配置页

**脚本：**
- `scripts/create-admin.ts` - 创建初始管理员脚本

**配置：**
- `.env.example` - 环境变量示例（更新）

---

## 任务分解

### 任务 1：项目初始化和依赖安装

**文件：**
- 修改：`package.json`
- 创建：`drizzle.config.ts`
- 创建：`admin.config.ts`
- 创建：`.env.example`（更新）

- [ ] **步骤 1：安装后端依赖**

```bash
npm install @vercel/postgres drizzle-orm bcryptjs jsonwebtoken
```

- [ ] **步骤 2：安装前端依赖**

```bash
npm install pinia naive-ui @vueuse/core axios @tiptap/vue-3 @tiptap/starter-kit @tiptap/extension-image @tiptap/extension-link
```

- [ ] **步骤 3：安装开发依赖**

```bash
npm install -D @types/bcryptjs @types/jsonwebtoken drizzle-kit
```

- [ ] **步骤 4：创建 Drizzle 配置文件**

```typescript
// drizzle.config.ts
import type { Config } from 'drizzle-kit';

export default {
  schema: './server/database/schema/index.ts',
  out: './server/database/migrations',
  driver: 'pg',
  dbCredentials: {
    connectionString: process.env.POSTGRES_URL || '',
  },
} satisfies Config;
```

- [ ] **步骤 5：创建后台配置文件**

```typescript
// admin.config.ts
export const adminConfig = {
  name: '博客管理后台',
  version: '1.0.0',
  apiPrefix: '/api/admin',
  jwt: {
    expiresIn: '7d',
  },
  pagination: {
    defaultPageSize: 20,
    pageSizes: [10, 20, 50, 100],
  },
};
```

- [ ] **步骤 6：更新 .env.example**

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

- [ ] **步骤 7：Commit**

```bash
git add package.json drizzle.config.ts admin.config.ts .env.example
git commit -m "feat: 初始化管理后台依赖和配置"
```

---

### 任务 2：数据库 Schema 定义

**文件：**
- 创建：`server/database/postgres.ts`
- 创建：`server/database/schema/admins.ts`
- 创建：`server/database/schema/siteSettings.ts`
- 创建：`server/database/schema/comments.ts`
- 创建：`server/database/schema/operationLogs.ts`
- 创建：`server/database/schema/index.ts`
- 创建：`server/database/migrations/001_initial.sql`

- [ ] **步骤 1：创建 Postgres 连接**

```typescript
// server/database/postgres.ts
import { drizzle } from 'drizzle-orm/vercel-postgres';
import { sql } from '@vercel/postgres';
import * as schema from './schema';

export const db = drizzle(sql, { schema });

export type DB = typeof db;
```

- [ ] **步骤 2：定义管理员表 Schema**

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

export type Admin = typeof admins.$inferSelect;
export type NewAdmin = typeof admins.$inferInsert;
```

- [ ] **步骤 3：定义站点配置表 Schema**

```typescript
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

export type SiteSetting = typeof siteSettings.$inferSelect;
export type NewSiteSetting = typeof siteSettings.$inferInsert;
```

- [ ] **步骤 4：定义评论表 Schema**

```typescript
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

export type Comment = typeof comments.$inferSelect;
export type NewComment = typeof comments.$inferInsert;
```

- [ ] **步骤 5：定义操作日志表 Schema**

```typescript
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

export type OperationLog = typeof operationLogs.$inferSelect;
export type NewOperationLog = typeof operationLogs.$inferInsert;
```

- [ ] **步骤 6：创建 Schema 导出文件**

```typescript
// server/database/schema/index.ts
export * from './admins';
export * from './siteSettings';
export * from './comments';
export * from './operationLogs';
```

- [ ] **步骤 7：生成数据库迁移文件**

```bash
npx drizzle-kit generate:pg
```

- [ ] **步骤 8：查看生成的迁移文件并确认**

```bash
cat server/database/migrations/001_initial.sql
```

- [ ] **步骤 9：Commit**

```bash
git add server/database/
git commit -m "feat: 定义数据库 Schema 和迁移"
```

---

### 任务 3：工具函数和中间件

**文件：**
- 创建：`server/utils/jwt.ts`
- 创建：`server/utils/password.ts`
- 创建：`server/middleware/admin-auth.ts`

- [ ] **步骤 1：创建密码加密工具**

```typescript
// server/utils/password.ts
import bcrypt from 'bcryptjs';

const SALT_ROUNDS = 12;

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

export async function verifyPassword(
  password: string,
  hash: string
): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

export function validatePasswordStrength(password: string): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('密码长度至少 8 位');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('密码必须包含大写字母');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('密码必须包含小写字母');
  }

  if (!/[0-9]/.test(password)) {
    errors.push('密码必须包含数字');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
```

- [ ] **步骤 2：创建 JWT 工具**

```typescript
// server/utils/jwt.ts
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-change-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';

export interface JWTPayload {
  adminId: number;
  username: string;
  role: string;
}

export function generateToken(payload: JWTPayload): string {
  return jwt.sign(payload, JWT_SECRET, {
    expiresIn: JWT_EXPIRES_IN,
  });
}

export function verifyToken(token: string): JWTPayload | null {
  try {
    return jwt.verify(token, JWT_SECRET) as JWTPayload;
  } catch (error) {
    return null;
  }
}

export function decodeToken(token: string): JWTPayload | null {
  try {
    return jwt.decode(token) as JWTPayload;
  } catch (error) {
    return null;
  }
}
```

- [ ] **步骤 3：创建管理员认证中间件**

```typescript
// server/middleware/admin-auth.ts
import { defineEventHandler, getHeader, sendError } from 'h3';
import { verifyToken } from '~/server/utils/jwt';

export default defineEventHandler(async (event) => {
  // 跳过登录接口
  if (event.node.req.url?.startsWith('/api/admin/auth/login')) {
    return;
  }

  // 所有 /api/admin/* 请求需要认证
  if (!event.node.req.url?.startsWith('/api/admin')) {
    return;
  }

  const authHeader = getHeader(event, 'Authorization');
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return sendError(event, {
      statusCode: 401,
      statusMessage: 'Unauthorized',
      data: { message: '未提供认证 token' },
    });
  }

  const token = authHeader.substring(7);
  const payload = verifyToken(token);

  if (!payload) {
    return sendError(event, {
      statusCode: 401,
      statusMessage: 'Unauthorized',
      data: { message: 'Token 无效或已过期' },
    });
  }

  // 将用户信息添加到上下文中
  event.context.admin = payload;
});

declare module 'h3' {
  interface H3EventContext {
    admin?: {
      adminId: number;
      username: string;
      role: string;
    };
  }
}
```

- [ ] **步骤 4：Commit**

```bash
git add server/utils/ server/middleware/
git commit -m "feat: 创建认证工具函数和中间件"
```

---

### 任务 4：认证 API

**文件：**
- 创建：`server/routes/api/admin/auth/login.post.ts`
- 创建：`server/routes/api/admin/auth/logout.post.ts`
- 创建：`server/routes/api/admin/auth/me.get.ts`
- 创建：`scripts/create-admin.ts`

- [ ] **步骤 1：创建初始管理员脚本**

```typescript
// scripts/create-admin.ts
import { sql } from '@vercel/postgres';
import { hashPassword } from '../server/utils/password';

async function createAdmin() {
  const username = process.argv[2] || 'admin';
  const password = process.argv[3];

  if (!password) {
    console.error('请提供密码：npm run create-admin <username> <password>');
    process.exit(1);
  }

  const passwordHash = await hashPassword(password);

  try {
    await sql`
      INSERT INTO admins (username, password_hash, email, role)
      VALUES (${username}, ${passwordHash}, ${username + '@example.com'}, 'admin')
      ON CONFLICT (username) DO UPDATE SET password_hash = ${passwordHash}
    `;
    console.log(`管理员 ${username} 创建成功`);
  } catch (error) {
    console.error('创建管理员失败:', error);
    process.exit(1);
  }
}

createAdmin();
```

- [ ] **步骤 2：在 package.json 中添加脚本**

```json
{
  "scripts": {
    "create-admin": "tsx scripts/create-admin.ts"
  }
}
```

- [ ] **步骤 3：创建登录 API**

```typescript
// server/routes/api/admin/auth/login.post.ts
import { defineEventHandler, readBody, sendError } from 'h3';
import { db } from '~/server/database/postgres';
import { admins } from '~/server/database/schema';
import { eq } from 'drizzle-orm';
import { verifyPassword } from '~/server/utils/password';
import { generateToken } from '~/server/utils/jwt';
import { z } from 'zod';

const loginSchema = z.object({
  username: z.string().min(1, '用户名不能为空'),
  password: z.string().min(1, '密码不能为空'),
});

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event);
    const { username, password } = loginSchema.parse(body);

    // 查找管理员
    const adminList = await db
      .select()
      .from(admins)
      .where(eq(admins.username, username))
      .limit(1);

    if (adminList.length === 0) {
      return sendError(event, {
        statusCode: 401,
        statusMessage: 'Unauthorized',
        data: { message: '用户名或密码错误' },
      });
    }

    const admin = adminList[0];

    // 验证密码
    const isValid = await verifyPassword(password, admin.passwordHash);

    if (!isValid) {
      return sendError(event, {
        statusCode: 401,
        statusMessage: 'Unauthorized',
        data: { message: '用户名或密码错误' },
      });
    }

    // 生成 token
    const token = generateToken({
      adminId: admin.id,
      username: admin.username,
      role: admin.role || 'admin',
    });

    return {
      success: true,
      data: {
        token,
        admin: {
          id: admin.id,
          username: admin.username,
          email: admin.email,
          avatar: admin.avatar,
          role: admin.role,
        },
      },
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return sendError(event, {
        statusCode: 400,
        statusMessage: 'Bad Request',
        data: { message: error.errors[0].message },
      });
    }
    throw error;
  }
});
```

- [ ] **步骤 4：创建登出 API**

```typescript
// server/routes/api/admin/auth/logout.post.ts
import { defineEventHandler } from 'h3';

export default defineEventHandler(async (event) => {
  // 在客户端清除 token 即可，服务端无需特殊处理
  // 如果需要 token 黑名单机制，可以在这里实现
  
  return {
    success: true,
    message: '登出成功',
  };
});
```

- [ ] **步骤 5：创建获取当前用户信息 API**

```typescript
// server/routes/api/admin/auth/me.get.ts
import { defineEventHandler, getHeader, sendError } from 'h3';
import { db } from '~/server/database/postgres';
import { admins } from '~/server/database/schema';
import { eq } from 'drizzle-orm';
import { verifyToken } from '~/server/utils/jwt';

export default defineEventHandler(async (event) => {
  const authHeader = getHeader(event, 'Authorization');
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return sendError(event, {
      statusCode: 401,
      statusMessage: 'Unauthorized',
      data: { message: '未认证' },
    });
  }

  const token = authHeader.substring(7);
  const payload = verifyToken(token);

  if (!payload) {
    return sendError(event, {
      statusCode: 401,
      statusMessage: 'Unauthorized',
      data: { message: 'Token 无效' },
    });
  }

  const adminList = await db
    .select({
      id: admins.id,
      username: admins.username,
      email: admins.email,
      avatar: admins.avatar,
      role: admins.role,
      createdAt: admins.createdAt,
    })
    .from(admins)
    .where(eq(admins.id, payload.adminId))
    .limit(1);

  if (adminList.length === 0) {
    return sendError(event, {
      statusCode: 404,
      statusMessage: 'Not Found',
      data: { message: '管理员不存在' },
    });
  }

  return {
    success: true,
    data: adminList[0],
  };
});
```

- [ ] **步骤 6：安装 zod 依赖**

```bash
npm install zod
```

- [ ] **步骤 7：Commit**

```bash
git add server/routes/api/admin/auth/ scripts/create-admin.ts package.json
git commit -m "feat: 实现认证 API"
```

---

### 任务 5：管理后台类型和工具

**文件：**
- 创建：`admin/types/admin.ts`
- 创建：`admin/utils/api.ts`
- 创建：`admin/utils/validators.ts`

- [ ] **步骤 1：创建 TypeScript 类型定义**

```typescript
// admin/types/admin.ts
export interface Admin {
  id: number;
  username: string;
  email?: string;
  avatar?: string;
  role: string;
  createdAt: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  data: {
    token: string;
    admin: Admin;
  };
}

export interface Post {
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

export interface Category {
  id: number;
  title: string;
  slug: string;
  description?: string;
  articleCount?: number;
  createdAt: string;
  updatedAt: string;
}

export interface Tag {
  id: number;
  title: string;
  slug: string;
  articleCount?: number;
  createdAt: string;
  updatedAt: string;
}

export interface Comment {
  id: number;
  articleSlug: string;
  articleTitle?: string;
  githubId?: string;
  status: 'pending' | 'approved' | 'rejected';
  isPinned: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface SiteSetting {
  id: number;
  keyName: string;
  keyValue?: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

export interface DashboardStats {
  totalPosts: number;
  totalCategories: number;
  totalTags: number;
  totalComments: number;
  pendingComments: number;
}

export interface PaginationParams {
  page?: number;
  pageSize?: number;
  search?: string;
  categoryId?: number;
  status?: string;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}
```

- [ ] **步骤 2：创建 API 客户端**

```typescript
// admin/utils/api.ts
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = '/api/admin';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器：添加 token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('admin_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器：处理错误
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token 过期，跳转到登录页
          localStorage.removeItem('admin_token');
          window.location.href = '/admin/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete(url);
    return response.data;
  }
}

export const apiClient = new ApiClient();
```

- [ ] **步骤 3：创建验证器**

```typescript
// admin/utils/validators.ts
export function validateSlug(slug: string): { valid: boolean; error?: string } {
  if (!slug) {
    return { valid: false, error: '别名不能为空' };
  }

  if (slug.length > 100) {
    return { valid: false, error: '别名长度不能超过 100 个字符' };
  }

  const slugRegex = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
  if (!slugRegex.test(slug)) {
    return {
      valid: false,
      error: '别名只能包含小写字母、数字和连字符',
    };
  }

  return { valid: true };
}

export function validateEmail(email: string): { valid: boolean; error?: string } {
  if (!email) {
    return { valid: true }; // 邮箱可选
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, error: '邮箱格式不正确' };
  }

  return { valid: true };
}

export function validateRequired(
  value: any,
  fieldName: string
): { valid: boolean; error?: string } {
  if (!value || (typeof value === 'string' && !value.trim())) {
    return { valid: false, error: `${fieldName}不能为空` };
  }
  return { valid: true };
}

export function validateLength(
  value: string,
  fieldName: string,
  maxLength: number
): { valid: boolean; error?: string } {
  if (value.length > maxLength) {
    return {
      valid: false,
      error: `${fieldName}长度不能超过${maxLength}个字符`,
    };
  }
  return { valid: true };
}
```

- [ ] **步骤 4：Commit**

```bash
git add admin/types/ admin/utils/
git commit -m "feat: 创建管理后台类型定义和工具函数"
```

---

### 任务 6：状态管理和组合式函数

**文件：**
- 创建：`admin/stores/auth.ts`
- 创建：`admin/stores/app.ts`
- 创建：`admin/composables/useAuth.ts`
- 创建：`admin/composables/usePosts.ts`
- 创建：`admin/composables/useCategories.ts`
- 创建：`admin/composables/useTags.ts`
- 创建：`admin/composables/useComments.ts`
- 创建：`admin/composables/useSettings.ts`

- [ ] **步骤 1：创建认证状态管理**

```typescript
// admin/stores/auth.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Admin } from '../types/admin';

export const useAuthStore = defineStore('auth', () => {
  const admin = ref<Admin | null>(null);
  const token = ref<string | null>(localStorage.getItem('admin_token'));

  const isAuthenticated = computed(() => !!token.value);

  function setAuth(newToken: string, newAdmin: Admin) {
    token.value = newToken;
    admin.value = newAdmin;
    localStorage.setItem('admin_token', newToken);
  }

  function clearAuth() {
    token.value = null;
    admin.value = null;
    localStorage.removeItem('admin_token');
  }

  return {
    admin,
    token,
    isAuthenticated,
    setAuth,
    clearAuth,
  };
});
```

- [ ] **步骤 2：创建应用状态管理**

```typescript
// admin/stores/app.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false);
  const loading = ref(false);

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  }

  function setLoading(value: boolean) {
    loading.value = value;
  }

  return {
    sidebarCollapsed,
    loading,
    toggleSidebar,
    setLoading,
  };
});
```

- [ ] **步骤 3：创建认证组合式函数**

```typescript
// admin/composables/useAuth.ts
import { useAuthStore } from '../stores/auth';
import { apiClient } from '../utils/api';
import type { LoginRequest, LoginResponse, ApiResponse, Admin } from '../types/admin';

export function useAuth() {
  const authStore = useAuthStore();

  async function login(credentials: LoginRequest) {
    const response = await apiClient.post<LoginResponse>('/auth/login', credentials);
    if (response.success) {
      authStore.setAuth(response.data.token, response.data.admin);
    }
    return response;
  }

  async function logout() {
    await apiClient.post('/auth/logout');
    authStore.clearAuth();
  }

  async function getCurrentAdmin() {
    try {
      const response = await apiClient.get<ApiResponse<Admin>>('/auth/me');
      if (response.success) {
        authStore.admin = response.data;
      }
      return response.data;
    } catch (error) {
      return null;
    }
  }

  return {
    login,
    logout,
    getCurrentAdmin,
  };
}
```

- [ ] **步骤 4：创建文章管理组合式函数**

```typescript
// admin/composables/usePosts.ts
import { apiClient } from '../utils/api';
import type { Post, PaginatedResponse, PaginationParams, ApiResponse } from '../types/admin';

export function usePosts() {
  async function getPosts(params?: PaginationParams) {
    return apiClient.get<PaginatedResponse<Post>>('/posts', params);
  }

  async function getPost(id: number) {
    const response = await apiClient.get<ApiResponse<Post>>(`/posts/${id}`);
    return response.data;
  }

  async function createPost(data: Partial<Post>) {
    return apiClient.post<ApiResponse<Post>>('/posts', data);
  }

  async function updatePost(id: number, data: Partial<Post>) {
    return apiClient.put<ApiResponse<Post>>(`/posts/${id}`, data);
  }

  async function deletePost(id: number) {
    return apiClient.delete<ApiResponse<void>>(`/posts/${id}`);
  }

  async function batchDelete(ids: number[]) {
    return apiClient.post<ApiResponse<void>>('/posts/batch-delete', { ids });
  }

  return {
    getPosts,
    getPost,
    createPost,
    updatePost,
    deletePost,
    batchDelete,
  };
}
```

- [ ] **步骤 5：创建分类管理组合式函数**

```typescript
// admin/composables/useCategories.ts
import { apiClient } from '../utils/api';
import type { Category, PaginatedResponse, ApiResponse } from '../types/admin';

export function useCategories() {
  async function getCategories(params?: { page?: number; pageSize?: number }) {
    return apiClient.get<PaginatedResponse<Category>>('/categories', params);
  }

  async function getCategory(id: number) {
    const response = await apiClient.get<ApiResponse<Category>>(`/categories/${id}`);
    return response.data;
  }

  async function createCategory(data: Partial<Category>) {
    return apiClient.post<ApiResponse<Category>>('/categories', data);
  }

  async function updateCategory(id: number, data: Partial<Category>) {
    return apiClient.put<ApiResponse<Category>>(`/categories/${id}`, data);
  }

  async function deleteCategory(id: number) {
    return apiClient.delete<ApiResponse<void>>(`/categories/${id}`);
  }

  return {
    getCategories,
    getCategory,
    createCategory,
    updateCategory,
    deleteCategory,
  };
}
```

- [ ] **步骤 6：创建标签管理组合式函数**

```typescript
// admin/composables/useTags.ts
import { apiClient } from '../utils/api';
import type { Tag, PaginatedResponse, ApiResponse } from '../types/admin';

export function useTags() {
  async function getTags(params?: { page?: number; pageSize?: number }) {
    return apiClient.get<PaginatedResponse<Tag>>('/tags', params);
  }

  async function getTag(id: number) {
    const response = await apiClient.get<ApiResponse<Tag>>(`/tags/${id}`);
    return response.data;
  }

  async function createTag(data: Partial<Tag>) {
    return apiClient.post<ApiResponse<Tag>>('/tags', data);
  }

  async function updateTag(id: number, data: Partial<Tag>) {
    return apiClient.put<ApiResponse<Tag>>(`/tags/${id}`, data);
  }

  async function deleteTag(id: number) {
    return apiClient.delete<ApiResponse<void>>(`/tags/${id}`);
  }

  return {
    getTags,
    getTag,
    createTag,
    updateTag,
    deleteTag,
  };
}
```

- [ ] **步骤 7：创建评论管理组合式函数**

```typescript
// admin/composables/useComments.ts
import { apiClient } from '../utils/api';
import type { Comment, PaginatedResponse, ApiResponse } from '../types/admin';

export function useComments() {
  async function getComments(params?: { page?: number; pageSize?: number; status?: string }) {
    return apiClient.get<PaginatedResponse<Comment>>('/comments', params);
  }

  async function approveComment(id: number) {
    return apiClient.put<ApiResponse<void>>(`/comments/${id}/approve`);
  }

  async function pinComment(id: number) {
    return apiClient.put<ApiResponse<void>>(`/comments/${id}/pin`);
  }

  async function deleteComment(id: number) {
    return apiClient.delete<ApiResponse<void>>(`/comments/${id}`);
  }

  return {
    getComments,
    approveComment,
    pinComment,
    deleteComment,
  };
}
```

- [ ] **步骤 8：创建站点配置组合式函数**

```typescript
// admin/composables/useSettings.ts
import { apiClient } from '../utils/api';
import type { SiteSetting, ApiResponse } from '../types/admin';

export function useSettings() {
  async function getSettings() {
    return apiClient.get<ApiResponse<SiteSetting[]>>('/settings');
  }

  async function getSetting(key: string) {
    const response = await apiClient.get<ApiResponse<SiteSetting>>(`/settings/${key}`);
    return response.data;
  }

  async function updateSetting(key: string, value: string) {
    return apiClient.put<ApiResponse<SiteSetting>>(`/settings/${key}`, { value });
  }

  async function syncWithSanity() {
    return apiClient.post<ApiResponse<void>>('/settings/sync-sanity');
  }

  return {
    getSettings,
    getSetting,
    updateSetting,
    syncWithSanity,
  };
}
```

- [ ] **步骤 9：Commit**

```bash
git add admin/stores/ admin/composables/
git commit -m "feat: 创建状态管理和组合式函数"
```

---

### 任务 7：管理后台布局和通用组件

**文件：**
- 创建：`admin/layouts/admin.vue`
- 创建：`admin/components/common/AdminHeader.vue`
- 创建：`admin/components/common/AdminSidebar.vue`
- 创建：`admin/components/common/Pagination.vue`
- 创建：`admin/components/common/LoadingMask.vue`

- [ ] **步骤 1：创建后台布局**

```vue
<!-- admin/layouts/admin.vue -->
<template>
  <div class="admin-layout">
    <AdminSidebar />
    <div class="admin-content">
      <AdminHeader />
      <main class="admin-main">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import AdminHeader from '../components/common/AdminHeader.vue';
import AdminSidebar from '../components/common/AdminSidebar.vue';

const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/admin/login');
  }
});
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.admin-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 240px;
}

.admin-main {
  flex: 1;
  padding: 24px;
  background-color: #f5f5f5;
}

@media (max-width: 768px) {
  .admin-content {
    margin-left: 0;
  }
}
</style>
```

- [ ] **步骤 2：创建顶部导航栏组件**

```vue
<!-- admin/components/common/AdminHeader.vue -->
<template>
  <header class="admin-header">
    <div class="breadcrumb">
      <slot name="breadcrumb">首页</slot>
    </div>
    <div class="user-menu">
      <n-avatar :src="admin?.avatar" :size="32" />
      <span class="username">{{ admin?.username }}</span>
      <n-dropdown :options="menuOptions" @select="handleMenuSelect">
        <n-button quaternary circle>
          <template #icon>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8m0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4"/>
            </svg>
          </template>
        </n-button>
      </n-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { NAvatar, NButton, NDropdown } from 'naive-ui';
import { useAuthStore } from '../../stores/auth';
import { useAuth } from '../../composables/useAuth';

const router = useRouter();
const authStore = useAuthStore();
const { logout } = useAuth();

const admin = computed(() => authStore.admin);

const menuOptions = [
  {
    label: '退出登录',
    key: 'logout',
    icon: () => '🚪',
  },
];

const handleMenuSelect = async (key: string) => {
  if (key === 'logout') {
    await logout();
    router.push('/admin/login');
  }
};
</script>

<style scoped>
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: white;
  border-bottom: 1px solid #e8e8e4;
}

.breadcrumb {
  font-size: 14px;
  color: #666;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username {
  font-size: 14px;
  color: #333;
}
</style>
```

- [ ] **步骤 3：创建侧边栏导航组件**

```vue
<!-- admin/components/common/AdminSidebar.vue -->
<template>
  <aside class="admin-sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
    <div class="logo">
      <h1 v-if="!appStore.sidebarCollapsed">博客管理后台</h1>
      <span v-else>📊</span>
    </div>
    <nav class="nav-menu">
      <n-menu
        v-model:value="activeKey"
        :collapsed="appStore.sidebarCollapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :options="menuOptions"
        @update:value="handleMenuSelect"
      />
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { ref, h } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { NMenu, NIcon } from 'naive-ui';
import { useAppStore } from '../../stores/app';

const router = useRouter();
const route = useRoute();
const appStore = useAppStore();

const activeKey = ref(route.path);

const renderIcon = (icon: string) => {
  return () => h(NIcon, null, { default: () => icon });
};

const menuOptions = [
  {
    label: '仪表盘',
    key: '/admin/dashboard',
    icon: renderIcon('📊'),
  },
  {
    label: '文章管理',
    key: '/admin/posts',
    icon: renderIcon('📝'),
    children: [
      { label: '所有文章', key: '/admin/posts' },
      { label: '新建文章', key: '/admin/posts/new' },
    ],
  },
  {
    label: '分类管理',
    key: '/admin/categories',
    icon: renderIcon('📁'),
  },
  {
    label: '标签管理',
    key: '/admin/tags',
    icon: renderIcon('🏷️'),
  },
  {
    label: '评论管理',
    key: '/admin/comments',
    icon: renderIcon('💬'),
  },
  {
    label: '站点配置',
    key: '/admin/settings',
    icon: renderIcon('⚙️'),
  },
];

const handleMenuSelect = (key: string) => {
  router.push(key);
};
</script>

<style scoped>
.admin-sidebar {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 240px;
  background-color: #1a1a1a;
  color: white;
  transition: width 0.3s;
  z-index: 1000;
}

.admin-sidebar.collapsed {
  width: 64px;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #2a2a2a;
}

.logo h1 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.nav-menu {
  padding: 16px 0;
}

:deep(.n-menu) {
  --n-item-text-color: #fff;
  --n-item-text-color-hover: #fff;
  --n-item-color-hover: rgba(255, 255, 255, 0.1);
}
</style>
```

- [ ] **步骤 4：创建分页组件**

```vue
<!-- admin/components/common/Pagination.vue -->
<template>
  <div class="pagination">
    <n-pagination
      v-model:page="currentPage"
      v-model:page-size="pageSize"
      :item-count="total"
      :page-sizes="pageSizes"
      show-size-picker
      @update:page="handlePageChange"
      @update:page-size="handlePageSizeChange"
    >
      <template #prefix="{ itemCount }">
        共 {{ itemCount }} 条
      </template>
    </n-pagination>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { NPagination } from 'naive-ui';

interface Props {
  total: number;
  page: number;
  pageSize: number;
  pageSizes?: number[];
}

const props = withDefaults(defineProps<Props>(), {
  pageSizes: () => [10, 20, 50, 100],
});

const emit = defineEmits<{
  'update:page': [value: number];
  'update:pageSize': [value: number];
}>();

const currentPage = ref(props.page);
const pageSize = ref(props.pageSize);

watch(
  () => props.page,
  (newVal) => {
    currentPage.value = newVal;
  }
);

watch(
  () => props.pageSize,
  (newVal) => {
    pageSize.value = newVal;
  }
);

const handlePageChange = (page: number) => {
  emit('update:page', page);
};

const handlePageSizeChange = (size: number) => {
  emit('update:pageSize', size);
  emit('update:page', 1);
};
</script>

<style scoped>
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}
</style>
```

- [ ] **步骤 5：创建加载遮罩组件**

```vue
<!-- admin/components/common/LoadingMask.vue -->
<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="loading-mask">
        <n-spin :show="true" :size="64" description="加载中...">
          <div class="loading-content" />
        </n-spin>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { NSpin } from 'naive-ui';

defineProps<{
  visible: boolean;
}>();
</script>

<style scoped>
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  width: 200px;
  height: 200px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
```

- [ ] **步骤 6：Commit**

```bash
git add admin/layouts/ admin/components/common/
git commit -m "feat: 创建后台布局和通用组件"
```

---

### 任务 8：登录页面

**文件：**
- 创建：`admin/pages/login.vue`

- [ ] **步骤 1：创建登录页面**

```vue
<!-- admin/pages/login.vue -->
<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h1>博客管理后台</h1>
        <p>请登录您的管理员账号</p>
      </div>
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        @submit.prevent="handleLogin"
      >
        <n-form-item path="username" label="用户名">
          <n-input
            v-model:value="formData.username"
            placeholder="请输入用户名"
            size="large"
          />
        </n-form-item>
        <n-form-item path="password" label="密码">
          <n-input
            v-model:value="formData.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password-on="click"
          />
        </n-form-item>
        <n-form-item>
          <n-button
            type="primary"
            html-type="submit"
            size="large"
            block
            :loading="loading"
          >
            登录
          </n-button>
        </n-form-item>
      </n-form>
      <n-alert
        v-if="error"
        type="error"
        :title="error"
        style="margin-top: 16px"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import {
  NForm,
  NFormItem,
  NInput,
  NButton,
  NAlert,
} from 'naive-ui';
import type { FormRules, FormInst } from 'naive-ui';
import { useAuth } from '../composables/useAuth';

const router = useRouter();
const { login } = useAuth();

const formRef = ref<FormInst | null>(null);
const loading = ref(false);
const error = ref('');

const formData = reactive({
  username: '',
  password: '',
});

const formRules: FormRules = {
  username: {
    required: true,
    message: '请输入用户名',
    trigger: 'blur',
  },
  password: {
    required: true,
    message: '请输入密码',
    trigger: 'blur',
  },
};

const handleLogin = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (errors) => {
    if (errors) return;

    loading.value = true;
    error.value = '';

    try {
      await login({
        username: formData.username,
        password: formData.password,
      });
      router.push('/admin/dashboard');
    } catch (err: any) {
      error.value = err.response?.data?.data?.message || '登录失败，请检查账号密码';
    } finally {
      loading.value = false;
    }
  });
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: #666;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add admin/pages/login.vue
git commit -m "feat: 创建登录页面"
```

---

### 任务 9：仪表盘页面

**文件：**
- 创建：`admin/pages/dashboard.vue`
- 创建：`server/routes/api/admin/dashboard/stats.get.ts`
- 创建：`server/routes/api/admin/dashboard/recent-posts.get.ts`

- [ ] **步骤 1：创建仪表盘统计 API**

```typescript
// server/routes/api/admin/dashboard/stats.get.ts
import { defineEventHandler } from 'h3';
import { db } from '~/server/database/postgres';
import { admins, siteSettings, comments, operationLogs } from '~/server/database/schema';
import { count, sql } from 'drizzle-orm';

export default defineEventHandler(async (event) => {
  // 获取统计数据
  const [
    adminCount,
    settingsCount,
    commentCount,
    pendingCommentCount,
  ] = await Promise.all([
    db.select({ count: count() }).from(admins),
    db.select({ count: count() }).from(siteSettings),
    db.select({ count: count() }).from(comments),
    db
      .select({ count: count() })
      .from(comments)
      .where(sql`${comments.status} = 'pending'`),
  ]);

  return {
    success: true,
    data: {
      totalAdmins: adminCount[0].count,
      totalSettings: settingsCount[0].count,
      totalComments: commentCount[0].count,
      pendingComments: pendingCommentCount[0].count,
    },
  };
});
```

- [ ] **步骤 2：创建仪表盘页面**

```vue
<!-- admin/pages/dashboard.vue -->
<template>
  <div class="dashboard">
    <h1 class="page-title">仪表盘</h1>
    
    <div class="stats-grid">
      <n-card class="stat-card">
        <div class="stat-icon" style="background-color: #18a058">
          📝
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalPosts || 0 }}</div>
          <div class="stat-label">文章总数</div>
        </div>
      </n-card>

      <n-card class="stat-card">
        <div class="stat-icon" style="background-color: #2080f0">
          📁
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalCategories || 0 }}</div>
          <div class="stat-label">分类数</div>
        </div>
      </n-card>

      <n-card class="stat-card">
        <div class="stat-icon" style="background-color: #f0a020">
          🏷️
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalTags || 0 }}</div>
          <div class="stat-label">标签数</div>
        </div>
      </n-card>

      <n-card class="stat-card">
        <div class="stat-icon" style="background-color: #d03050">
          💬
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pendingComments || 0 }}</div>
          <div class="stat-label">待审核评论</div>
        </div>
      </n-card>
    </div>

    <div class="quick-actions">
      <h2 class="section-title">快速操作</h2>
      <div class="action-buttons">
        <n-button type="primary" @click="router.push('/admin/posts/new')">
          新建文章
        </n-button>
        <n-button @click="router.push('/admin/comments')">
          评论审核
        </n-button>
        <n-button @click="router.push('/admin/settings')">
          站点配置
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { NCard, NButton } from 'naive-ui';
import { apiClient } from '../utils/api';

const router = useRouter();
const stats = ref({
  totalPosts: 0,
  totalCategories: 0,
  totalTags: 0,
  totalComments: 0,
  pendingComments: 0,
});

onMounted(async () => {
  try {
    const response = await apiClient.get('/dashboard/stats');
    if (response.success) {
      stats.value = response.data;
    }
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
});
</script>

<style scoped>
.dashboard {
  padding: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.quick-actions {
  margin-top: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 12px;
}
</style>
```

- [ ] **步骤 3：Commit**

```bash
git add admin/pages/dashboard.vue server/routes/api/admin/dashboard/
git commit -m "feat: 创建仪表盘页面和 API"
```

---

### 任务 10：文章管理 API

**文件：**
- 创建：`server/routes/api/admin/posts/index.get.ts`
- 创建：`server/routes/api/admin/posts/index.post.ts`
- 创建：`server/routes/api/admin/posts/[id].get.ts`
- 创建：`server/routes/api/admin/posts/[id].put.ts`
- 创建：`server/routes/api/admin/posts/[id].delete.ts`

- [ ] **步骤 1：创建获取文章列表 API**

```typescript
// server/routes/api/admin/posts/index.get.ts
import { defineEventHandler, getQuery } from 'h3';
import { sql } from '@vercel/postgres';

export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const page = Number(query.page) || 1;
  const pageSize = Number(query.pageSize) || 20;
  const offset = (page - 1) * pageSize;

  // 构建查询条件
  const conditions: string[] = [];
  const params: any[] = [];

  if (query.search) {
    conditions.push(`(title ILIKE $${params.length + 1} OR slug ILIKE $${params.length + 1})`);
    params.push(`%${query.search}%`);
  }

  if (query.categoryId) {
    conditions.push(`category_id = $${params.length + 1}`);
    params.push(Number(query.categoryId));
  }

  const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

  // 获取文章列表
  const postsResult = await sql`
    SELECT * FROM posts
    ${whereClause ? sql.raw(whereClause) : sql``}
    ORDER BY published_at DESC
    LIMIT ${pageSize} OFFSET ${offset}
  `;

  // 获取总数
  const countResult = await sql`
    SELECT COUNT(*) FROM posts
    ${whereClause ? sql.raw(whereClause) : sql``}
  `;

  const total = Number(countResult.rows[0]?.count || 0);

  return {
    success: true,
    data: postsResult.rows,
    total,
    page,
    pageSize,
    totalPages: Math.ceil(total / pageSize),
  };
});
```

- [ ] **步骤 2：创建获取文章详情 API**

```typescript
// server/routes/api/admin/posts/[id].get.ts
import { defineEventHandler, getRouterParam } from 'h3';
import { sql } from '@vercel/postgres';

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id');

  const result = await sql`
    SELECT * FROM posts WHERE id = ${Number(id)}
  `;

  if (result.rows.length === 0) {
    throw createError({
      statusCode: 404,
      statusMessage: 'Not Found',
      data: { message: '文章不存在' },
    });
  }

  return {
    success: true,
    data: result.rows[0],
  };
});
```

- [ ] **步骤 3：创建文章 API（续）**

继续创建创建、更新、删除文章的 API...

（由于篇幅限制，这里省略详细代码，实际实现时参考设计文档中的 API 规范）

- [ ] **步骤 4：Commit**

```bash
git add server/routes/api/admin/posts/
git commit -m "feat: 创建文章管理 API"
```

---

### 任务 11：文章管理页面

**文件：**
- 创建：`admin/pages/posts/index.vue`
- 创建：`admin/pages/posts/new.vue`
- 创建：`admin/pages/posts/[id].vue`
- 创建：`admin/components/posts/PostList.vue`
- 创建：`admin/components/posts/PostForm.vue`
- 创建：`admin/components/posts/PostFilters.vue`
- 创建：`admin/components/posts/PostPreview.vue`

- [ ] **步骤 1：创建文章列表页面**
- [ ] **步骤 2：创建文章表单组件**
- [ ] **步骤 3：创建文章编辑页面**
- [ ] **步骤 4：集成 Tiptap 富文本编辑器**
- [ ] **步骤 5：Commit**

---

### 任务 12：分类和标签管理

**文件：**
- 创建：`server/routes/api/admin/categories/` 下所有 API
- 创建：`server/routes/api/admin/tags/` 下所有 API
- 创建：`admin/pages/categories/index.vue`
- 创建：`admin/pages/tags/index.vue`

- [ ] **步骤 1：创建分类管理 API**
- [ ] **步骤 2：创建分类管理页面**
- [ ] **步骤 3：创建标签管理 API**
- [ ] **步骤 4：创建标签管理页面**
- [ ] **步骤 5：Commit**

---

### 任务 13：评论和配置管理

**文件：**
- 创建：`server/routes/api/admin/comments/` 下所有 API
- 创建：`server/routes/api/admin/settings/` 下所有 API
- 创建：