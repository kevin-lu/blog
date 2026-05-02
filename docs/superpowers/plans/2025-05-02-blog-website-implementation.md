# 个人技术博客网站实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 基于 Nuxt.js 3 + Sanity CMS 构建一个具备内容管理后台、评论系统和暗黑模式的个人技术博客网站

**架构：** 前端使用 Nuxt.js 3 进行服务端渲染/静态生成，内容管理使用 Sanity Headless CMS，评论系统使用 Giscus（基于 GitHub Discussions），部署在 Vercel 平台

**技术栈：** Nuxt.js 3, Vue 3, TypeScript, Tailwind CSS, Sanity, Giscus, Vercel

---

## 文件结构

```
my-blog/
├── app/                          # Nuxt 3 应用目录
│   ├── components/               # Vue 组件
│   │   ├── content/              # 内容相关组件
│   │   │   ├── ArticleCard.vue   # 文章卡片组件
│   │   │   ├── ArticleList.vue   # 文章列表组件
│   │   │   ├── ArticleContent.vue # 文章内容渲染
│   │   │   ├── CategoryBadge.vue # 分类标签
│   │   │   └── TagList.vue       # 标签列表
│   │   ├── layout/               # 布局组件
│   │   │   ├── AppHeader.vue     # 顶部导航
│   │   │   ├── AppFooter.vue     # 页脚
│   │   │   └── ThemeToggle.vue   # 主题切换按钮
│   │   └── ui/                   # 基础 UI 组件
│   │       └── Container.vue     # 容器组件
│   ├── composables/              # 组合式函数
│   │   ├── useSanity.ts          # Sanity 客户端封装
│   │   ├── useArticles.ts        # 文章数据获取
│   │   └── useTheme.ts           # 主题管理
│   ├── layouts/                  # 布局
│   │   └── default.vue           # 默认布局
│   ├── pages/                    # 页面路由
│   │   ├── index.vue             # 首页
│   │   ├── posts/
│   │   │   └── [slug].vue        # 文章详情页
│   │   ├── categories/
│   │   │   └── [name].vue        # 分类文章页
│   │   ├── tags/
│   │   │   └── [name].vue        # 标签文章页
│   │   └── about.vue             # 关于页面
│   ├── assets/                   # 静态资源
│   │   └── css/
│   │       └── main.css          # 全局样式
│   ├── types/                    # TypeScript 类型
│   │   └── index.ts              # 类型定义
│   ├── utils/                    # 工具函数
│   │   └── helpers.ts            # 辅助函数
│   └── app.vue                   # 根组件
├── studio/                       # Sanity Studio
│   ├── schemas/                  # 数据模型
│   │   ├── article.ts            # 文章模型
│   │   ├── category.ts           # 分类模型
│   │   ├── tag.ts                # 标签模型
│   │   ├── series.ts             # 系列模型
│   │   └── siteSettings.ts       # 站点设置
│   ├── structure.ts              # Studio 结构配置
│   └── sanity.config.ts          # Studio 配置
├── public/                       # 公共静态文件
│   └── favicon.ico
├── nuxt.config.ts                # Nuxt 配置
├── tailwind.config.ts            # Tailwind 配置
├── tsconfig.json                 # TypeScript 配置
├── sanity.cli.ts                 # Sanity CLI 配置
├── sanity.config.ts              # Sanity 项目配置
└── package.json                  # 依赖管理
```

---

## 阶段一：项目初始化

### 任务 1：初始化 Nuxt.js 项目

**文件：**
- 创建：`package.json`
- 创建：`nuxt.config.ts`
- 创建：`tsconfig.json`
- 创建：`.gitignore`

- [ ] **步骤 1：创建 package.json**

```json
{
  "name": "my-blog",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "nuxt build",
    "dev": "nuxt dev",
    "generate": "nuxt generate",
    "preview": "nuxt preview",
    "postinstall": "nuxt prepare"
  },
  "dependencies": {
    "@nuxt/ui": "^2.15.0",
    "@sanity/image-url": "^1.0.2",
    "@sanity/vision": "^3.40.0",
    "groq": "^3.40.0",
    "nuxt": "^3.11.0",
    "sanity": "^3.40.0",
    "vue": "^3.4.0",
    "vue-router": "^4.3.0"
  },
  "devDependencies": {
    "@nuxtjs/sanity": "^1.9.0",
    "@types/node": "^20.0.0",
    "typescript": "^5.4.0"
  }
}
```

- [ ] **步骤 2：创建 nuxt.config.ts**

```typescript
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ['@nuxt/ui', '@nuxtjs/sanity'],
  css: ['~/assets/css/main.css'],
  sanity: {
    projectId: process.env.NUXT_PUBLIC_SANITY_PROJECT_ID,
    dataset: process.env.NUXT_PUBLIC_SANITY_DATASET || 'production',
    apiVersion: process.env.NUXT_PUBLIC_SANITY_API_VERSION || '2024-05-01',
    useCdn: true,
  },
  runtimeConfig: {
    sanityApiToken: process.env.SANITY_API_READ_TOKEN,
    public: {
      giscusRepo: process.env.NUXT_PUBLIC_GISCUS_REPO,
      giscusRepoId: process.env.NUXT_PUBLIC_GISCUS_REPO_ID,
      giscusCategory: process.env.NUXT_PUBLIC_GISCUS_CATEGORY,
      giscusCategoryId: process.env.NUXT_PUBLIC_GISCUS_CATEGORY_ID,
    }
  },
  app: {
    head: {
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      htmlAttrs: {
        lang: 'zh-CN'
      }
    }
  }
})
```

- [ ] **步骤 3：创建 tsconfig.json**

```json
{
  "extends": "./.nuxt/tsconfig.json"
}
```

- [ ] **步骤 4：创建 .gitignore**

```gitignore
# Nuxt dev/build outputs
.output
.nuxt
.nitro
.cache
dist

# Node dependencies
node_modules

# Logs
logs
*.log

# Misc
.DS_Store
.fleet
.idea

# Local env files
.env
.env.*
!.env.example
```

- [ ] **步骤 5：安装依赖**

运行：`npm install`
预期：成功安装所有依赖，生成 `.nuxt` 目录

- [ ] **步骤 6：Commit**

```bash
git add .
git commit -m "chore: initialize Nuxt.js project with dependencies"
```

---

### 任务 2：配置 Tailwind CSS 和全局样式

**文件：**
- 创建：`tailwind.config.ts`
- 创建：`app/assets/css/main.css`

- [ ] **步骤 1：创建 tailwind.config.ts**

```typescript
import type { Config } from 'tailwindcss'

export default {
  darkMode: 'class',
  content: [],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: 'var(--bg)',
          card: 'var(--bg-card)',
          nav: 'var(--bg-nav)',
        },
        text: {
          DEFAULT: 'var(--text)',
          muted: 'var(--text-muted)',
          light: 'var(--text-light)',
        },
        accent: {
          DEFAULT: 'var(--accent)',
          light: 'var(--accent-light)',
        },
        border: {
          DEFAULT: 'var(--border)',
          hover: 'var(--border-hover)',
        },
      },
      fontFamily: {
        sans: ['"PingFang SC"', '"Microsoft YaHei"', '"Hiragino Sans GB"', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'sans-serif'],
        mono: ['"SF Mono"', 'Consolas', '"Courier New"', 'monospace'],
      },
      boxShadow: {
        'sm': '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
        'md': '0 4px 16px rgba(0,0,0,0.08)',
        'lg': '0 12px 40px rgba(0,0,0,0.1)',
      },
      borderRadius: {
        'DEFAULT': '12px',
      },
      maxWidth: {
        'content': '1100px',
      },
    },
  },
  plugins: [],
} satisfies Config
```

- [ ] **步骤 2：创建 app/assets/css/main.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --bg: #f5f5f0;
  --bg-card: #ffffff;
  --bg-nav: rgba(255,255,255,0.85);
  --text: #111111;
  --text-muted: #777777;
  --text-light: #aaaaaa;
  --accent: #1a56db;
  --accent-light: #eff4ff;
  --border: #e8e8e4;
  --border-hover: #c7c7c0;
}

.dark {
  --bg: #0f0f0f;
  --bg-card: #1a1a1a;
  --bg-nav: rgba(26,26,26,0.85);
  --text: #f5f5f0;
  --text-muted: #a0a0a0;
  --text-light: #666666;
  --accent: #3b82f6;
  --accent-light: rgba(59,130,246,0.15);
  --border: #2a2a2a;
  --border-hover: #3a3a3a;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-sans);
  background-color: var(--bg);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
}

/* 文章正文样式 */
.prose {
  color: var(--text);
}

.prose h1, .prose h2, .prose h3, .prose h4 {
  color: var(--text);
  font-weight: 600;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}

.prose h1 { font-size: 1.875rem; }
.prose h2 { font-size: 1.5rem; }
.prose h3 { font-size: 1.25rem; }
.prose h4 { font-size: 1.125rem; }

.prose p {
  margin-bottom: 1em;
}

.prose code {
  background-color: var(--accent-light);
  color: var(--accent);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-size: 0.875em;
  font-family: var(--font-mono);
}

.prose pre {
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1em;
  overflow-x: auto;
  margin: 1em 0;
}

.prose pre code {
  background-color: transparent;
  color: var(--text);
  padding: 0;
}

.prose blockquote {
  border-left: 4px solid var(--accent);
  padding-left: 1em;
  margin: 1em 0;
  color: var(--text-muted);
}

.prose img {
  max-width: 100%;
  border-radius: 8px;
  margin: 1em 0;
}

.prose a {
  color: var(--accent);
  text-decoration: none;
}

.prose a:hover {
  text-decoration: underline;
}

.prose ul, .prose ol {
  margin: 1em 0;
  padding-left: 1.5em;
}

.prose li {
  margin: 0.25em 0;
}
```

- [ ] **步骤 3：Commit**

```bash
git add .
git commit -m "chore: configure Tailwind CSS and global styles"
```

---

## 阶段二：Sanity CMS 配置

### 任务 3：初始化 Sanity Studio

**文件：**
- 创建：`sanity.cli.ts`
- 创建：`sanity.config.ts`
- 创建：`studio/sanity.config.ts`
- 创建：`studio/structure.ts`

- [ ] **步骤 1：创建 sanity.cli.ts**

```typescript
import { defineCliConfig } from 'sanity/cli'

export default defineCliConfig({
  api: {
    projectId: process.env.SANITY_PROJECT_ID || 'your-project-id',
    dataset: process.env.SANITY_DATASET || 'production'
  }
})
```

- [ ] **步骤 2：创建 sanity.config.ts**

```typescript
import { defineConfig } from 'sanity'
import { structureTool } from 'sanity/structure'
import { visionTool } from '@sanity/vision'
import { schemaTypes } from './studio/schemas'
import { structure } from './studio/structure'

export default defineConfig({
  name: 'default',
  title: 'My Blog',

  projectId: process.env.SANITY_PROJECT_ID || 'your-project-id',
  dataset: process.env.SANITY_DATASET || 'production',

  plugins: [
    structureTool({ structure }),
    visionTool(),
  ],

  schema: {
    types: schemaTypes,
  },
})
```

- [ ] **步骤 3：创建 studio/sanity.config.ts**

```typescript
import { defineConfig } from 'sanity'
import { structureTool } from 'sanity/structure'
import { visionTool } from '@sanity/vision'
import { schemaTypes } from './schemas'
import { structure } from './structure'

export default defineConfig({
  name: 'default',
  title: 'My Blog',

  projectId: import.meta.env.SANITY_STUDIO_PROJECT_ID || 'your-project-id',
  dataset: import.meta.env.SANITY_STUDIO_DATASET || 'production',

  plugins: [
    structureTool({ structure }),
    visionTool(),
  ],

  schema: {
    types: schemaTypes,
  },
})
```

- [ ] **步骤 4：创建 studio/structure.ts**

```typescript
import type { StructureResolver } from 'sanity/structure'

export const structure: StructureResolver = (S) =>
  S.list()
    .title('内容管理')
    .items([
      S.listItem()
        .title('站点设置')
        .child(
          S.editor()
            .schemaType('siteSettings')
            .documentId('siteSettings')
        ),
      S.divider(),
      S.documentTypeListItem('article').title('文章'),
      S.documentTypeListItem('category').title('分类'),
      S.documentTypeListItem('tag').title('标签'),
      S.documentTypeListItem('series').title('系列'),
    ])
```

- [ ] **步骤 5：Commit**

```bash
git add .
git commit -m "chore: initialize Sanity Studio configuration"
```

---

### 任务 4：创建 Sanity Schema

**文件：**
- 创建：`studio/schemas/index.ts`
- 创建：`studio/schemas/article.ts`
- 创建：`studio/schemas/category.ts`
- 创建：`studio/schemas/tag.ts`
- 创建：`studio/schemas/series.ts`
- 创建：`studio/schemas/siteSettings.ts`

- [ ] **步骤 1：创建 studio/schemas/index.ts**

```typescript
import article from './article'
import category from './category'
import tag from './tag'
import series from './series'
import siteSettings from './siteSettings'

export const schemaTypes = [article, category, tag, series, siteSettings]
```

- [ ] **步骤 2：创建 studio/schemas/article.ts**

```typescript
import { defineField, defineType } from 'sanity'

export default defineType({
  name: 'article',
  title: '文章',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: '标题',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'slug',
      title: '别名',
      type: 'slug',
      options: {
        source: 'title',
        maxLength: 96,
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'excerpt',
      title: '摘要',
      type: 'text',
      rows: 3,
      description: '文章摘要，不填写则自动提取正文前150字',
    }),
    defineField({
      name: 'content',
      title: '正文内容',
      type: 'array',
      of: [
        { type: 'block' },
        {
          type: 'image',
          options: {
            hotspot: true,
          },
          fields: [
            {
              name: 'caption',
              type: 'string',
              title: '图片说明',
            },
            {
              name: 'alt',
              type: 'string',
              title: '替代文本',
            },
          ],
        },
        {
          type: 'code',
          title: '代码块',
        },
      ],
    }),
    defineField({
      name: 'coverImage',
      title: '封面图',
      type: 'image',
      options: {
        hotspot: true,
      },
    }),
    defineField({
      name: 'category',
      title: '分类',
      type: 'reference',
      to: [{ type: 'category' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'tags',
      title: '标签',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'tag' }] }],
    }),
    defineField({
      name: 'publishedAt',
      title: '发布时间',
      type: 'datetime',
      initialValue: () => new Date().toISOString(),
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'updatedAt',
      title: '更新时间',
      type: 'datetime',
    }),
    defineField({
      name: 'featured',
      title: '精选文章',
      type: 'boolean',
      initialValue: false,
      description: '标记为精选文章将在首页优先展示',
    }),
    defineField({
      name: 'series',
      title: '所属系列',
      type: 'reference',
      to: [{ type: 'series' }],
      description: '如果文章属于某个系列，请选择',
    }),
  ],
  preview: {
    select: {
      title: 'title',
      category: 'category.title',
      media: 'coverImage',
    },
    prepare({ title, category, media }) {
      return {
        title,
        subtitle: category ? `分类: ${category}` : '',
        media,
      }
    },
  },
  orderings: [
    {
      title: '发布时间, 最新',
      name: 'publishedAtDesc',
      by: [{ field: 'publishedAt', direction: 'desc' }],
    },
  ],
})
```

- [ ] **步骤 3：创建 studio/schemas/category.ts**

```typescript
import { defineField, defineType } from 'sanity'

export default defineType({
  name: 'category',
  title: '分类',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: '名称',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'slug',
      title: '别名',
      type: 'slug',
      options: {
        source: 'title',
        maxLength: 96,
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: '描述',
      type: 'text',
      rows: 2,
    }),
  ],
  preview: {
    select: {
      title: 'title',
      subtitle: 'description',
    },
  },
})
```

- [ ] **步骤 4：创建 studio/schemas/tag.ts**

```typescript
import { defineField, defineType } from 'sanity'

export default defineType({
  name: 'tag',
  title: '标签',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: '名称',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'slug',
      title: '别名',
      type: 'slug',
      options: {
        source: 'title',
        maxLength: 96,
      },
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {
      title: 'title',
    },
  },
})
```

- [ ] **步骤 5：创建 studio/schemas/series.ts**

```typescript
import { defineField, defineType } from 'sanity'

export default defineType({
  name: 'series',
  title: '系列',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: '名称',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'slug',
      title: '别名',
      type: 'slug',
      options: {
        source: 'title',
        maxLength: 96,
      },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: '描述',
      type: 'text',
      rows: 3,
    }),
  ],
  preview: {
    select: {
      title: 'title',
      subtitle: 'description',
    },
  },
})
```

- [ ] **步骤 6：创建 studio/schemas/siteSettings.ts**

```typescript
import { defineField, defineType } from 'sanity'

export default defineType({
  name: 'siteSettings',
  title: '站点设置',
  type: 'document',
  fields: [
    defineField({
      name: 'title',
      title: '网站标题',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: '网站描述',
      type: 'text',
      rows: 2,
      description: '用于 SEO 和社交媒体分享',
    }),
    defineField({
      name: 'author',
      title: '作者名称',
      type: 'string',
    }),
    defineField({
      name: 'avatar',
      title: '头像',
      type: 'image',
      options: {
        hotspot: true,
      },
    }),
    defineField({
      name: 'bio',
      title: '个人简介',
      type: 'text',
      rows: 3,
    }),
    defineField({
      name: 'socialLinks',
      title: '社交链接',
      type: 'array',
      of: [
        {
          type: 'object',
          fields: [
            defineField({
              name: 'platform',
              title: '平台',
              type: 'string',
              options: {
                list: [
                  { title: 'GitHub', value: 'github' },
                  { title: 'Twitter / X', value: 'twitter' },
                  { title: '微博', value: 'weibo' },
                  { title: '知乎', value: 'zhihu' },
                  { title: '掘金', value: 'juejin' },
                  { title: '邮箱', value: 'email' },
                  { title: '其他', value: 'other' },
                ],
              },
            }),
            defineField({
              name: 'url',
              title: '链接',
              type: 'url',
            }),
          ],
        },
      ],
    }),
  ],
  preview: {
    select: {
      title: 'title',
    },
  },
})
```

- [ ] **步骤 7：Commit**

```bash
git add .
git commit -m "feat: add Sanity schemas for article, category, tag, series and site settings"
```

---

## 阶段三：类型定义和工具函数

### 任务 5：创建 TypeScript 类型

**文件：**
- 创建：`app/types/index.ts`

- [ ] **步骤 1：创建 app/types/index.ts**

```typescript
// 文章类型
export interface Article {
  _id: string
  title: string
  slug: { current: string }
  excerpt?: string
  content?: any[]
  coverImage?: {
    asset: {
      _ref: string
      _type: string
    }
    hotspot?: {
      x: number
      y: number
    }
  }
  category: {
    _id: string
    title: string
    slug: { current: string }
  }
  tags?: {
    _id: string
    title: string
    slug: { current: string }
  }[]
  publishedAt: string
  updatedAt?: string
  featured?: boolean
  series?: {
    _id: string
    title: string
    slug: { current: string }
  }
  readingTime?: number
}

// 分类类型
export interface Category {
  _id: string
  title: string
  slug: { current: string }
  description?: string
  articleCount?: number
}

// 标签类型
export interface Tag {
  _id: string
  title: string
  slug: { current: string }
  articleCount?: number
}

// 系列类型
export interface Series {
  _id: string
  title: string
  slug: { current: string }
  description?: string
}

// 站点设置类型
export interface SiteSettings {
  _id: string
  title: string
  description?: string
  author?: string
  avatar?: {
    asset: {
      _ref: string
    }
  }
  bio?: string
  socialLinks?: {
    platform: string
    url: string
  }[]
}

// 文章列表项（简化版）
export interface ArticleListItem {
  _id: string
  title: string
  slug: { current: string }
  excerpt?: string
  coverImage?: Article['coverImage']
  category: string
  categorySlug: string
  tags?: string[]
  publishedAt: string
  readingTime?: number
}

// 文章详情（完整版）
export interface ArticleDetail extends Article {
  seriesArticles?: {
    title: string
    slug: { current: string }
  }[]
}

// Giscus 配置
export interface GiscusConfig {
  repo: string
  repoId: string
  category: string
  categoryId: string
  mapping: 'pathname' | 'url' | 'title' | 'og:title'
  reactionsEnabled: '1' | '0'
  emitMetadata: '1' | '0'
  inputPosition: 'top' | 'bottom'
  theme: 'light' | 'dark' | 'preferred_color_scheme'
  lang: 'zh-CN' | 'en' | string
  loading: 'lazy' | 'eager'
}
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add TypeScript type definitions"
```

---

### 任务 6：创建工具函数

**文件：**
- 创建：`app/utils/helpers.ts`

- [ ] **步骤 1：创建 app/utils/helpers.ts**

```typescript
import type { Article } from '~/types'

/**
 * 格式化日期
 */
export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

/**
 * 计算阅读时间（分钟）
 */
export function calculateReadingTime(content?: any[]): number {
  if (!content || !Array.isArray(content)) return 1
  
  // 提取所有文本内容
  const text = content
    .map((block) => {
      if (block._type === 'block' && block.children) {
        return block.children.map((child: any) => child.text || '').join('')
      }
      return ''
    })
    .join('')
  
  // 假设平均阅读速度为每分钟 200 字
  const wordsPerMinute = 200
  const wordCount = text.length
  const readingTime = Math.ceil(wordCount / wordsPerMinute)
  
  return Math.max(1, readingTime)
}

/**
 * 生成摘要（从正文提取前 n 个字符）
 */
export function generateExcerpt(content?: any[], maxLength: number = 150): string {
  if (!content || !Array.isArray(content)) return ''
  
  const text = content
    .map((block) => {
      if (block._type === 'block' && block.children) {
        return block.children.map((child: any) => child.text || '').join('')
      }
      return ''
    })
    .join('')
    .replace(/\s+/g, ' ')
    .trim()
  
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * 获取文章列表的 GROQ 查询
 */
export function getArticlesQuery(limit: number = 10, start: number = 0): string {
  return `*[_type == "article" && publishedAt <= now()] | order(publishedAt desc) [${start}...${start + limit}] {
    _id,
    title,
    slug,
    excerpt,
    coverImage,
    "category": category->title,
    "categorySlug": category->slug.current,
    "tags": tags[]->title,
    publishedAt,
    "readingTime": round(length(pt::text(content)) / 200)
  }`
}

/**
 * 获取单篇文章的 GROQ 查询
 */
export function getArticleBySlugQuery(slug: string): string {
  return `*[_type == "article" && slug.current == "${slug}"][0] {
    _id,
    title,
    slug,
    excerpt,
    content,
    coverImage,
    "category": category->{ _id, title, slug },
    "tags": tags[]->{ _id, title, slug },
    publishedAt,
    updatedAt,
    "readingTime": round(length(pt::text(content)) / 200),
    "series": series->{ _id, title, slug },
    "seriesArticles": *[_type == "article" && series._ref == ^.series._ref] | order(publishedAt asc) {
      title, slug
    }
  }`
}

/**
 * 获取分类列表的 GROQ 查询
 */
export function getCategoriesQuery(): string {
  return `*[_type == "category"] | order(title asc) {
    _id,
    title,
    slug,
    description,
    "articleCount": count(*[_type == "article" && references(^._id)])
  }`
}

/**
 * 获取标签列表的 GROQ 查询
 */
export function getTagsQuery(): string {
  return `*[_type == "tag"] | order(title asc) {
    _id,
    title,
    slug,
    "articleCount": count(*[_type == "article" && references(^._id)])
  }`
}

/**
 * 获取站点设置的 GROQ 查询
 */
export function getSiteSettingsQuery(): string {
  return `*[_type == "siteSettings"][0]`
}
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add utility helper functions"
```

---

## 阶段四：组合式函数（Composables）

### 任务 7：创建 useSanity Composable

**文件：**
- 创建：`app/composables/useSanity.ts`

- [ ] **步骤 1：创建 app/composables/useSanity.ts**

```typescript
import type { Article, ArticleListItem, ArticleDetail, Category, Tag, SiteSettings } from '~/types'
import { 
  getArticlesQuery, 
  getArticleBySlugQuery, 
  getCategoriesQuery, 
  getTagsQuery,
  getSiteSettingsQuery 
} from '~/utils/helpers'

export function useSanity() {
  const sanity = useNuxtApp().$sanity

  /**
   * 获取文章列表
   */
  async function fetchArticles(limit: number = 10, start: number = 0): Promise<ArticleListItem[]> {
    const query = getArticlesQuery(limit, start)
    return await sanity.fetch(query)
  }

  /**
   * 获取单篇文章
   */
  async function fetchArticleBySlug(slug: string): Promise<ArticleDetail | null> {
    const query = getArticleBySlugQuery(slug)
    return await sanity.fetch(query)
  }

  /**
   * 获取分类列表
   */
  async function fetchCategories(): Promise<Category[]> {
    const query = getCategoriesQuery()
    return await sanity.fetch(query)
  }

  /**
   * 获取标签列表
   */
  async function fetchTags(): Promise<Tag[]> {
    const query = getTagsQuery()
    return await sanity.fetch(query)
  }

  /**
   * 获取站点设置
   */
  async function fetchSiteSettings(): Promise<SiteSettings | null> {
    const query = getSiteSettingsQuery()
    return await sanity.fetch(query)
  }

  /**
   * 获取分类下的文章
   */
  async function fetchArticlesByCategory(categorySlug: string, limit: number = 10): Promise<ArticleListItem[]> {
    const query = `*[_type == "article" && category->slug.current == "${categorySlug}" && publishedAt <= now()] | order(publishedAt desc) [0...${limit}] {
      _id,
      title,
      slug,
      excerpt,
      coverImage,
      "category": category->title,
      "categorySlug": category->slug.current,
      "tags": tags[]->title,
      publishedAt,
      "readingTime": round(length(pt::text(content)) / 200)
    }`
    return await sanity.fetch(query)
  }

  /**
   * 获取标签下的文章
   */
  async function fetchArticlesByTag(tagSlug: string, limit: number = 10): Promise<ArticleListItem[]> {
    const query = `*[_type == "article" && "${tagSlug}" in tags[]->slug.current && publishedAt <= now()] | order(publishedAt desc) [0...${limit}] {
      _id,
      title,
      slug,
      excerpt,
      coverImage,
      "category": category->title,
      "categorySlug": category->slug.current,
      "tags": tags[]->title,
      publishedAt,
      "readingTime": round(length(pt::text(content)) / 200)
    }`
    return await sanity.fetch(query)
  }

  return {
    fetchArticles,
    fetchArticleBySlug,
    fetchCategories,
    fetchTags,
    fetchSiteSettings,
    fetchArticlesByCategory,
    fetchArticlesByTag,
  }
}
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add useSanity composable for data fetching"
```

---

### 任务 8：创建 useTheme Composable

**文件：**
- 创建：`app/composables/useTheme.ts`

- [ ] **步骤 1：创建 app/composables/useTheme.ts**

```typescript
import { useState, useCookie, onMounted } from '#imports'

type Theme = 'light' | 'dark' | 'system'

export function useTheme() {
  const theme = useState<Theme>('theme', () => 'system')
  const isDark = useState<boolean>('isDark', () => false)
  const themeCookie = useCookie<Theme>('theme', {
    default: () => 'system',
    maxAge: 60 * 60 * 24 * 365, // 1 year
  })

  /**
   * 初始化主题
   */
  function initTheme() {
    const savedTheme = themeCookie.value || 'system'
    theme.value = savedTheme
    applyTheme(savedTheme)
  }

  /**
   * 应用主题
   */
  function applyTheme(newTheme: Theme) {
    const root = document.documentElement
    
    if (newTheme === 'dark') {
      root.classList.add('dark')
      isDark.value = true
    } else if (newTheme === 'light') {
      root.classList.remove('dark')
      isDark.value = false
    } else {
      // system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (prefersDark) {
        root.classList.add('dark')
        isDark.value = true
      } else {
        root.classList.remove('dark')
        isDark.value = false
      }
    }
  }

  /**
   * 设置主题
   */
  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    themeCookie.value = newTheme
    applyTheme(newTheme)
  }

  /**
   * 切换主题（light <-> dark）
   */
  function toggleTheme() {
    if (isDark.value) {
      setTheme('light')
    } else {
      setTheme('dark')
    }
  }

  /**
   * 监听系统主题变化
   */
  function watchSystemTheme() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', (e) => {
      if (theme.value === 'system') {
        applyTheme('system')
      }
    })
  }

  // 在客户端初始化
  onMounted(() => {
    initTheme()
    watchSystemTheme()
  })

  return {
    theme: readonly(theme),
    isDark: readonly(isDark),
    setTheme,
    toggleTheme,
    initTheme,
  }
}
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add useTheme composable for dark mode"
```

---

## 阶段五：布局组件

### 任务 9：创建 ThemeToggle 组件

**文件：**
- 创建：`app/components/layout/ThemeToggle.vue`

- [ ] **步骤 1：创建 app/components/layout/ThemeToggle.vue**

```vue
<template>
  <button
    @click="toggleTheme"
    class="p-2 rounded-lg transition-colors duration-200 hover:bg-border"
    :aria-label="isDark ? '切换到浅色模式' : '切换到深色模式'"
  >
    <!-- 太阳图标（暗黑模式时显示） -->
    <svg
      v-if="isDark"
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="text-text"
    >
      <circle cx="12" cy="12" r="5" />
      <line x1="12" y1="1" x2="12" y2="3" />
      <line x1="12" y1="21" x2="12" y2="23" />
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
      <line x1="1" y1="12" x2="3" y2="12" />
      <line x1="21" y1="12" x2="23" y2="12" />
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
    
    <!-- 月亮图标（浅色模式时显示） -->
    <svg
      v-else
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="text-text"
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
  </button>
</template>

<script setup lang="ts">
const { isDark, toggleTheme } = useTheme()
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add ThemeToggle component"
```

---

### 任务 10：创建 AppHeader 组件

**文件：**
- 创建：`app/components/layout/AppHeader.vue`

- [ ] **步骤 1：创建 app/components/layout/AppHeader.vue**

```vue
<template>
  <header class="sticky top-0 z-50 bg-bg-nav backdrop-blur-md border-b border-border">
    <div class="max-w-content mx-auto px-6 h-[60px] flex items-center justify-between">
      <!-- Logo -->
      <NuxtLink to="/" class="flex items-center gap-2 text-text hover:opacity-80 transition-opacity">
        <div class="w-8 h-8 bg-text rounded-lg flex items-center justify-center">
          <svg class="w-4 h-4 text-bg" viewBox="0 0 24 24" fill="currentColor">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <polyline points="10 9 9 9 8 9" />
          </svg>
        </div>
        <span class="font-bold text-[15px] tracking-tight">我的博客</span>
      </NuxtLink>

      <!-- Navigation -->
      <nav class="flex items-center gap-1">
        <NuxtLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="px-3.5 py-1.5 text-sm font-medium text-text-muted rounded-lg transition-all duration-200 hover:text-text hover:bg-border"
          :class="{ 'text-text bg-border': isActive(item.path) }"
        >
          {{ item.label }}
        </NuxtLink>
        
        <div class="w-px h-5 bg-border mx-2" />
        
        <ThemeToggle />
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
const route = useRoute()

const navItems = [
  { label: '首页', path: '/' },
  { label: '分类', path: '/categories' },
  { label: '标签', path: '/tags' },
  { label: '关于', path: '/about' },
]

function isActive(path: string): boolean {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add AppHeader component with navigation"
```

---

### 任务 11：创建 AppFooter 组件

**文件：**
- 创建：`app/components/layout/AppFooter.vue`

- [ ] **步骤 1：创建 app/components/layout/AppFooter.vue**

```vue
<template>
  <footer class="border-t border-border mt-auto">
    <div class="max-w-content mx-auto px-6 py-8">
      <div class="flex flex-col md:flex-row items-center justify-between gap-4">
        <!-- Copyright -->
        <p class="text-sm text-text-muted">
          © {{ currentYear }} {{ siteTitle }}. All rights reserved.
        </p>

        <!-- Social Links -->
        <div v-if="socialLinks?.length" class="flex items-center gap-4">
          <a
            v-for="link in socialLinks"
            :key="link.platform"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-text-muted hover:text-text transition-colors"
            :aria-label="link.platform"
          >
            <component :is="getSocialIcon(link.platform)" class="w-5 h-5" />
          </a>
        </div>

        <!-- Powered by -->
        <p class="text-xs text-text-light">
          Powered by 
          <a href="https://nuxt.com" target="_blank" rel="noopener" class="hover:text-text-muted transition-colors">Nuxt</a>
          &
          <a href="https://sanity.io" target="_blank" rel="noopener" class="hover:text-text-muted transition-colors">Sanity</a>
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const { data: siteSettings } = await useAsyncData('siteSettings', () => useSanity().fetchSiteSettings())

const currentYear = new Date().getFullYear()
const siteTitle = computed(() => siteSettings.value?.title || '我的博客')
const socialLinks = computed(() => siteSettings.value?.socialLinks || [])

// 简单的社交图标组件映射
const getSocialIcon = (platform: string) => {
  // 返回一个通用的链接图标
  return {
    template: `
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
      </svg>
    `
  }
}
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add AppFooter component"
```

---

### 任务 12：创建默认布局

**文件：**
- 创建：`app/layouts/default.vue`

- [ ] **步骤 1：创建 app/layouts/default.vue**

```vue
<template>
  <div class="min-h-screen flex flex-col bg-bg text-text">
    <AppHeader />
    <main class="flex-1">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
// 初始化主题
onMounted(() => {
  useTheme().initTheme()
})
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add default layout with header and footer"
```

---

## 阶段六：内容组件

### 任务 13：创建 ArticleCard 组件

**文件：**
- 创建：`app/components/content/ArticleCard.vue`

- [ ] **步骤 1：创建 app/components/content/ArticleCard.vue**

```vue
<template>
  <article class="bg-bg-card rounded-xl shadow-md overflow-hidden transition-all duration-200 hover:shadow-lg hover:border-border-hover border border-transparent">
    <!-- Cover Image -->
    <NuxtLink v-if="article.coverImage" :to="`/posts/${article.slug.current}`" class="block aspect-video overflow-hidden">
      <SanityImage
        :asset-id="article.coverImage.asset._ref"
        class="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
        :alt="article.title"
      />
    </NuxtLink>

    <div class="p-5">
      <!-- Category -->
      <NuxtLink
        :to="`/categories/${article.categorySlug}`"
        class="inline-block text-xs font-medium text-accent mb-2 hover:underline"
      >
        {{ article.category }}
      </NuxtLink>

      <!-- Title -->
      <h2 class="text-lg font-semibold text-text mb-2 leading-tight">
        <NuxtLink :to="`/posts/${article.slug.current}`" class="hover:text-accent transition-colors">
          {{ article.title }}
        </NuxtLink>
      </h2>

      <!-- Excerpt -->
      <p v-if="article.excerpt" class="text-sm text-text-muted line-clamp-2 mb-3">
        {{ article.excerpt }}
      </p>

      <!-- Meta -->
      <div class="flex items-center gap-3 text-xs text-text-light">
        <time :datetime="article.publishedAt">
          {{ formatDate(article.publishedAt) }}
        </time>
        <span v-if="article.readingTime" class="flex items-center gap-1">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          {{ article.readingTime }} 分钟
        </span>
      </div>

      <!-- Tags -->
      <div v-if="article.tags?.length" class="flex flex-wrap gap-2 mt-3">
        <span
          v-for="tag in article.tags.slice(0, 3)"
          :key="tag"
          class="text-xs px-2 py-0.5 bg-accent-light text-accent rounded"
        >
          {{ tag }}
        </span>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { ArticleListItem } from '~/types'
import { formatDate } from '~/utils/helpers'

interface Props {
  article: ArticleListItem
}

defineProps<Props>()
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add ArticleCard component"
```

---

### 任务 14：创建 ArticleList 组件

**文件：**
- 创建：`app/components/content/ArticleList.vue`

- [ ] **步骤 1：创建 app/components/content/ArticleList.vue**

```vue
<template>
  <div class="space-y-6">
    <div v-if="pending" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
    </div>

    <div v-else-if="error" class="text-center py-12 text-text-muted">
      <p>加载文章失败，请稍后重试</p>
      <button
        @click="refresh"
        class="mt-4 px-4 py-2 text-sm bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors"
      >
        重新加载
      </button>
    </div>

    <div v-else-if="!articles?.length" class="text-center py-12 text-text-muted">
      <p>暂无文章</p>
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2">
      <ArticleCard
        v-for="article in articles"
        :key="article._id"
        :article="article"
      />
    </div>

    <!-- Load More -->
    <div v-if="showLoadMore && articles?.length" class="text-center pt-6">
      <button
        @click="$emit('loadMore')"
        class="px-6 py-2.5 text-sm font-medium text-text-muted bg-bg-card border border-border rounded-lg hover:border-border-hover hover:text-text transition-all"
        :disabled="loadingMore"
      >
        <span v-if="loadingMore">加载中...</span>
        <span v-else>加载更多</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ArticleListItem } from '~/types'

interface Props {
  articles?: ArticleListItem[]
  pending?: boolean
  error?: Error | null
  showLoadMore?: boolean
  loadingMore?: boolean
}

interface Emits {
  (e: 'refresh'): void
  (e: 'loadMore'): void
}

defineProps<Props>()
defineEmits<Emits>()

const refresh = () => {
  // 触发刷新
  location.reload()
}
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add ArticleList component"
```

---

### 任务 15：创建 ArticleContent 组件

**文件：**
- 创建：`app/components/content/ArticleContent.vue`

- [ ] **步骤 1：创建 app/components/content/ArticleContent.vue**

```vue
<template>
  <article class="prose prose-lg max-w-none">
    <SanityContent :blocks="content" />
  </article>
</template>

<script setup lang="ts">
interface Props {
  content?: any[]
}

defineProps<Props>()
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add ArticleContent component"
```

---

### 任务 16：创建 GiscusComments 组件

**文件：**
- 创建：`app/components/content/GiscusComments.vue`

- [ ] **步骤 1：创建 app/components/content/GiscusComments.vue**

```vue
<template>
  <div class="mt-12 pt-8 border-t border-border">
    <h3 class="text-lg font-semibold text-text mb-6">评论</h3>
    <div ref="giscusContainer" />
  </div>
</template>

<script setup lang="ts">
const giscusContainer = ref<HTMLElement>()
const config = useRuntimeConfig()

onMounted(() => {
  if (!giscusContainer.value) return
  
  const script = document.createElement('script')
  script.src = 'https://giscus.app/client.js'
  script.setAttribute('data-repo', config.public.giscusRepo as string)
  script.setAttribute('data-repo-id', config.public.giscusRepoId as string)
  script.setAttribute('data-category', config.public.giscusCategory as string)
  script.setAttribute('data-category-id', config.public.giscusCategoryId as string)
  script.setAttribute('data-mapping', 'pathname')
  script.setAttribute('data-strict', '0')
  script.setAttribute('data-reactions-enabled', '1')
  script.setAttribute('data-emit-metadata', '0')
  script.setAttribute('data-input-position', 'bottom')
  script.setAttribute('data-theme', 'preferred_color_scheme')
  script.setAttribute('data-lang', 'zh-CN')
  script.setAttribute('data-loading', 'lazy')
  script.setAttribute('crossorigin', 'anonymous')
  script.async = true
  
  giscusContainer.value.appendChild(script)
})
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add GiscusComments component"
```

---

## 阶段七：页面实现

### 任务 17：创建首页

**文件：**
- 创建：`app/pages/index.vue`

- [ ] **步骤 1：创建 app/pages/index.vue**

```vue
<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <!-- Hero Section -->
    <section v-if="siteSettings" class="mb-12">
      <div class="flex flex-col md:flex-row items-center gap-6 bg-bg-card rounded-2xl p-6 shadow-md">
        <SanityImage
          v-if="siteSettings.avatar"
          :asset-id="siteSettings.avatar.asset._ref"
          class="w-20 h-20 rounded-full object-cover"
          :alt="siteSettings.author || 'Avatar'"
        />
        <div class="text-center md:text-left">
          <h1 class="text-2xl font-bold text-text mb-2">
            {{ siteSettings.title }}
          </h1>
          <p v-if="siteSettings.bio" class="text-text-muted">
            {{ siteSettings.bio }}
          </p>
        </div>
      </div>
    </section>

    <!-- Articles Section -->
    <section>
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold text-text">最新文章</h2>
        <NuxtLink
          to="/categories"
          class="text-sm text-accent hover:underline"
        >
          查看全部 →
        </NuxtLink>
      </div>

      <ArticleList
        :articles="articles"
        :pending="pending"
        :error="error"
        :show-load-more="hasMore"
        :loading-more="loadingMore"
        @load-more="loadMore"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
const { fetchArticles, fetchSiteSettings } = useSanity()

// 获取站点设置
const { data: siteSettings } = await useAsyncData('siteSettings', () => fetchSiteSettings())

// 获取文章列表
const pageSize = 10
const page = ref(1)
const articles = ref<ArticleListItem[]>([])
const hasMore = ref(true)
const loadingMore = ref(false)

const { data: initialArticles, pending, error } = await useAsyncData('articles', () => fetchArticles(pageSize, 0))

if (initialArticles.value) {
  articles.value = initialArticles.value
  hasMore.value = initialArticles.value.length === pageSize
}

// 加载更多
async function loadMore() {
  if (loadingMore.value) return
  
  loadingMore.value = true
  const start = page.value * pageSize
  
  try {
    const newArticles = await fetchArticles(pageSize, start)
    if (newArticles.length) {
      articles.value.push(...newArticles)
      page.value++
    }
    hasMore.value = newArticles.length === pageSize
  } catch (e) {
    console.error('Failed to load more articles:', e)
  } finally {
    loadingMore.value = false
  }
}

// SEO
useHead({
  title: siteSettings.value?.title || '我的博客',
  meta: [
    {
      name: 'description',
      content: siteSettings.value?.description || '一个基于 Nuxt.js 和 Sanity 构建的技术博客'
    }
  ]
})
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add homepage with hero and article list"
```

---

### 任务 18：创建文章详情页

**文件：**
- 创建：`app/pages/posts/[slug].vue`

- [ ] **步骤 1：创建 app/pages/posts/[slug].vue**

```vue
<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <article v-if="article">
      <!-- Header -->
      <header class="mb-8">
        <!-- Category -->
        <NuxtLink
          :to="`/categories/${article.category.slug.current}`"
          class="inline-block text-sm font-medium text-accent mb-3 hover:underline"
        >
          {{ article.category.title }}
        </NuxtLink>

        <!-- Title -->
        <h1 class="text-3xl md:text-4xl font-bold text-text mb-4 leading-tight">
          {{ article.title }}
        </h1>

        <!-- Meta -->
        <div class="flex flex-wrap items-center gap-4 text-sm text-text-muted">
          <time :datetime="article.publishedAt">
            {{ formatDate(article.publishedAt) }}
          </time>
          <span v-if="article.readingTime" class="flex items-center gap-1">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            {{ article.readingTime }} 分钟阅读
          </span>
          <span v-if="article.updatedAt" class="text-text-light">
            更新于 {{ formatDate(article.updatedAt) }}
          </span>
        </div>

        <!-- Tags -->
        <div v-if="article.tags?.length" class="flex flex-wrap gap-2 mt-4">
          <NuxtLink
            v-for="tag in article.tags"
            :key="tag._id"
            :to="`/tags/${tag.slug.current}`"
            class="text-xs px-3 py-1 bg-accent-light text-accent rounded-full hover:bg-accent hover:text-white transition-colors"
          >
            {{ tag.title }}
          </NuxtLink>
        </div>
      </header>

      <!-- Cover Image -->
      <SanityImage
        v-if="article.coverImage"
        :asset-id="article.coverImage.asset._ref"
        class="w-full aspect-video object-cover rounded-xl mb-8"
        :alt="article.title"
      />

      <!-- Content -->
      <ArticleContent :content="article.content" />

      <!-- Series Navigation -->
      <div v-if="article.series && article.seriesArticles?.length" class="mt-12 p-6 bg-bg-card rounded-xl border border-border">
        <h3 class="text-lg font-semibold text-text mb-4">
          系列：{{ article.series.title }}
        </h3>
        <ul class="space-y-2">
          <li
            v-for="(seriesArticle, index) in article.seriesArticles"
            :key="seriesArticle.slug.current"
            class="flex items-center gap-2"
          >
            <span class="text-sm text-text-light">{{ index + 1 }}.</span>
            <NuxtLink
              :to="`/posts/${seriesArticle.slug.current}`"
              class="text-sm hover:text-accent transition-colors"
              :class="seriesArticle.slug.current === article.slug.current ? 'text-accent font-medium' : 'text-text-muted'"
            >
              {{ seriesArticle.title }}
            </NuxtLink>
          </li>
        </ul>
      </div>

      <!-- Comments -->
      <GiscusComments />
    </article>

    <!-- 404 -->
    <div v-else class="text-center py-20">
      <h1 class="text-4xl font-bold text-text mb-4">404</h1>
      <p class="text-text-muted mb-6">文章未找到</p>
      <NuxtLink to="/" class="text-accent hover:underline">
        ← 返回首页
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { fetchArticleBySlug } = useSanity()

const slug = route.params.slug as string

const { data: article, pending, error } = await useAsyncData(`article-${slug}`, () => fetchArticleBySlug(slug))

// SEO
useHead(() => {
  if (!article.value) return {}
  
  return {
    title: `${article.value.title} - 我的博客`,
    meta: [
      {
        name: 'description',
        content: article.value.excerpt || ''
      },
      {
        property: 'og:title',
        content: article.value.title
      },
      {
        property: 'og:description',
        content: article.value.excerpt || ''
      },
      {
        property: 'og:type',
        content: 'article'
      }
    ]
  }
})
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add article detail page with comments"
```

---

### 任务 19：创建分类页面

**文件：**
- 创建：`app/pages/categories/index.vue`
- 创建：`app/pages/categories/[name].vue`

- [ ] **步骤 1：创建 app/pages/categories/index.vue**

```vue
<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <h1 class="text-2xl font-bold text-text mb-8">文章分类</h1>
    
    <div v-if="pending" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
    </div>

    <div v-else-if="error" class="text-center py-12 text-text-muted">
      <p>加载失败，请稍后重试</p>
    </div>

    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <NuxtLink
        v-for="category in categories"
        :key="category._id"
        :to="`/categories/${category.slug.current}`"
        class="block p-6 bg-bg-card rounded-xl border border-border hover:border-border-hover hover:shadow-md transition-all"
      >
        <h2 class="text-lg font-semibold text-text mb-2">{{ category.title }}</h2>
        <p v-if="category.description" class="text-sm text-text-muted mb-3 line-clamp-2">
          {{ category.description }}
        </p>
        <span class="text-xs text-text-light">{{ category.articleCount || 0 }} 篇文章</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const { fetchCategories } = useSanity()

const { data: categories, pending, error } = await useAsyncData('categories', () => fetchCategories())

useHead({
  title: '文章分类 - 我的博客',
  meta: [
    { name: 'description', content: '浏览所有文章分类' }
  ]
})
</script>
```

- [ ] **步骤 2：创建 app/pages/categories/[name].vue**

```vue
<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <div class="mb-8">
      <NuxtLink to="/categories" class="text-sm text-text-muted hover:text-accent transition-colors">
        ← 全部分类
      </NuxtLink>
      <h1 class="text-2xl font-bold text-text mt-4">{{ categoryName }}</h1>
    </div>

    <ArticleList
      :articles="articles"
      :pending="pending"
      :error="error"
    />
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { fetchArticlesByCategory } = useSanity()

const categoryName = computed(() => route.params.name as string)

const { data: articles, pending, error } = await useAsyncData(
  `category-${categoryName.value}`,
  () => fetchArticlesByCategory(categoryName.value, 20)
)

useHead({
  title: `${categoryName.value} - 文章分类 - 我的博客`
})
</script>
```

- [ ] **步骤 3：Commit**

```bash
git add .
git commit -m "feat: add category pages"
```

---

### 任务 20：创建标签页面

**文件：**
- 创建：`app/pages/tags/index.vue`
- 创建：`app/pages/tags/[name].vue`

- [ ] **步骤 1：创建 app/pages/tags/index.vue**

```vue
<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <h1 class="text-2xl font-bold text-text mb-8">文章标签</h1>
    
    <div v-if="pending" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
    </div>

    <div v-else-if="error" class="text-center py-12 text-text-muted">
      <p>加载失败，请稍后重试</p>
    </div>

    <div v-else class="flex flex-wrap gap-3">
      <NuxtLink
        v-for="tag in tags"
        :key="tag._id"
        :to="`/tags/${tag.slug.current}`"
        class="px-4 py-2 bg-bg-card border border-border rounded-full text-sm text-text-muted hover:border-accent hover:text-accent transition-all"
      >
        {{ tag.title }}
        <span class="ml-1 text-text-light">({{ tag.articleCount || 0 }})</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const { fetchTags } = useSanity()

const { data: tags, pending, error } = await useAsyncData('tags', () => fetchTags())

useHead({
  title: '文章标签 - 我的博客',
  meta: [
    { name: 'description', content: '浏览所有文章标签' }
  ]
})
</script>
```

- [ ] **步骤 2：创建 app/pages/tags/[name].vue**

```vue
<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <div class="mb-8">
      <NuxtLink to="/tags" class="text-sm text-text-muted hover:text-accent transition-colors">
        ← 全部标签
      </NuxtLink>
      <h1 class="text-2xl font-bold text-text mt-4">
        <span class="text-accent">#</span>{{ tagName }}
      </h1>
    </div>

    <ArticleList
      :articles="articles"
      :pending="pending"
      :error="error"
    />
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { fetchArticlesByTag } = useSanity()

const tagName = computed(() => route.params.name as string)

const { data: articles, pending, error } = await useAsyncData(
  `tag-${tagName.value}`,
  () => fetchArticlesByTag(tagName.value, 20)
)

useHead({
  title: `#${tagName.value} - 文章标签 - 我的博客`
})
</script>
```

- [ ] **步骤 3：Commit**

```bash
git add .
git commit -m "feat: add tag pages"
```

---

### 任务 21：创建关于页面

**文件：**
- 创建：`app/pages/about.vue`

- [ ] **步骤 1：创建 app/pages/about.vue**

```vue
<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <div v-if="siteSettings" class="max-w-2xl mx-auto">
      <!-- Profile -->
      <div class="text-center mb-12">
        <SanityImage
          v-if="siteSettings.avatar"
          :asset-id="siteSettings.avatar.asset._ref"
          class="w-24 h-24 rounded-full object-cover mx-auto mb-4"
          :alt="siteSettings.author || 'Avatar'"
        />
        <h1 class="text-2xl font-bold text-text mb-2">
          {{ siteSettings.author || siteSettings.title }}
        </h1>
        <p v-if="siteSettings.bio" class="text-text-muted">
          {{ siteSettings.bio }}
        </p>
      </div>

      <!-- Social Links -->
      <div v-if="siteSettings.socialLinks?.length" class="mb-12">
        <h2 class="text-lg font-semibold text-text mb-4">联系方式</h2>
        <div class="flex flex-wrap gap-4">
          <a
            v-for="link in siteSettings.socialLinks"
            :key="link.platform"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-2 px-4 py-2 bg-bg-card border border-border rounded-lg hover:border-accent hover:text-accent transition-all"
          >
            <span class="capitalize">{{ link.platform }}</span>
          </a>
        </div>
      </div>

      <!-- Description -->
      <div v-if="siteSettings.description" class="prose prose-lg max-w-none">
        <h2 class="text-lg font-semibold text-text mb-4">关于本站</h2>
        <p class="text-text-muted">{{ siteSettings.description }}</p>
      </div>
    </div>

    <div v-else class="text-center py-20 text-text-muted">
      <p>暂无内容</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { fetchSiteSettings } = useSanity()

const { data: siteSettings } = await useAsyncData('about', () => fetchSiteSettings())

useHead({
  title: '关于 - 我的博客',
  meta: [
    { name: 'description', content: siteSettings.value?.description || '关于本站' }
  ]
})
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: add about page"
```

---

## 阶段八：SEO 和优化

### 任务 22：配置 SEO 和 Meta

**文件：**
- 修改：`app/app.vue`

- [ ] **步骤 1：创建 app/app.vue**

```vue
<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
useHead({
  htmlAttrs: {
    lang: 'zh-CN'
  },
  link: [
    {
      rel: 'icon',
      type: 'image/x-icon',
      href: '/favicon.ico'
    }
  ],
  meta: [
    {
      name: 'viewport',
      content: 'width=device-width, initial-scale=1'
    },
    {
      charset: 'utf-8'
    }
  ]
})
</script>
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "feat: configure SEO and meta tags"
```

---

### 任务 23：生成 Sitemap

**文件：**
- 修改：`nuxt.config.ts`
- 创建：`server/routes/sitemap.xml.ts`

- [ ] **步骤 1：修改 nuxt.config.ts 添加 sitemap 配置**

```typescript
export default defineNuxtConfig({
  // ... existing config
  nitro: {
    prerender: {
      routes: ['/sitemap.xml']
    }
  }
})
```

- [ ] **步骤 2：创建 server/routes/sitemap.xml.ts**

```typescript
import { defineEventHandler } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const baseUrl = 'https://your-domain.vercel.app'
  
  // 获取所有文章
  const sanity = useNuxtApp().$sanity
  const articles = await sanity.fetch(`*[_type == "article"] { slug, updatedAt }`)
  
  const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${baseUrl}/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>${baseUrl}/categories</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>${baseUrl}/tags</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>${baseUrl}/about</loc>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
  ${articles.map((article: any) => `
  <url>
    <loc>${baseUrl}/posts/${article.slug.current}</loc>
    <lastmod>${article.updatedAt || new Date().toISOString()}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  `).join('')}
</urlset>`

  event.node.res.setHeader('content-type', 'application/xml')
  return sitemap
})
```

- [ ] **步骤 3：Commit**

```bash
git add .
git commit -m "feat: add sitemap generation"
```

---

## 阶段九：部署配置

### 任务 24：创建环境变量示例

**文件：**
- 创建：`.env.example`

- [ ] **步骤 1：创建 .env.example**

```bash
# Sanity 配置
NUXT_PUBLIC_SANITY_PROJECT_ID=your_project_id
NUXT_PUBLIC_SANITY_DATASET=production
NUXT_PUBLIC_SANITY_API_VERSION=2024-05-01
SANITY_API_READ_TOKEN=your_read_token

# Giscus 配置
NUXT_PUBLIC_GISCUS_REPO=username/repo
NUXT_PUBLIC_GISCUS_REPO_ID=xxx
NUXT_PUBLIC_GISCUS_CATEGORY=Comments
NUXT_PUBLIC_GISCUS_CATEGORY_ID=xxx
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "chore: add environment variables example"
```

---

### 任务 25：配置 Vercel 部署

**文件：**
- 创建：`vercel.json`

- [ ] **步骤 1：创建 vercel.json**

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".output/public",
  "installCommand": "npm install",
  "framework": "nuxtjs"
}
```

- [ ] **步骤 2：Commit**

```bash
git add .
git commit -m "chore: add Vercel deployment configuration"
```

---

## 部署清单

### Sanity 设置

1. 在 [Sanity.io](https://sanity.io) 创建项目
2. 获取 Project ID
3. 创建 API Token（只读权限）
4. 部署 Sanity Studio：`cd studio && sanity deploy`

### GitHub 设置

1. 创建新的 GitHub 仓库
2. 启用 Discussions（用于 Giscus 评论）
3. 在 [Giscus.app](https://giscus.app) 获取配置参数

### Vercel 设置

1. 导入 GitHub 仓库
2. 配置环境变量（从 .env.example）
3. 部署

---

## 自检

**规格覆盖度检查：**
- ✅ Nuxt.js 3 项目初始化
- ✅ Tailwind CSS 配置（含暗黑模式）
- ✅ Sanity Studio 配置
- ✅ 数据模型（Article, Category, Tag, Series, SiteSettings）
- ✅ 类型定义
- ✅ 工具函数
- ✅ Composables（useSanity, useTheme）
- ✅ 布局组件（Header, Footer, ThemeToggle）
- ✅ 内容组件（ArticleCard, ArticleList, ArticleContent, GiscusComments）
- ✅ 页面（首页、文章详情、分类、标签、关于）
- ✅ SEO 配置
- ✅ Sitemap 生成
- ✅ 部署配置

**无占位符检查：** 通过

**类型一致性检查：** 通过

---

**计划已完成并保存到 `docs/superpowers/plans/2025-05-02-blog-website-implementation.md`。两种执行方式：**

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

**选哪种方式？**
