# 个人技术博客网站设计文档

## 项目概述

基于 Vue 生态的现代化技术博客网站，参考三少科技博客的设计风格，具备内容管理后台、评论系统和暗黑模式。

---

## 技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 前端框架 | Nuxt.js | 3.x | Vue 生态的 SSR/SSG 框架 |
| 编程语言 | TypeScript | 5.x | 类型安全 |
| 样式框架 | Tailwind CSS | 3.x | 原子化 CSS |
| UI 组件 | @nuxt/ui | 2.x | Nuxt 官方 UI 库 |
| 图标 | @iconify/vue | - | 图标库 |
| CMS | Sanity | 3.x | Headless CMS |
| 评论系统 | Giscus | - | 基于 GitHub Discussions |
| 部署平台 | Vercel | - | 自动 CI/CD |

---

## 页面结构

```
├── 首页 (/)                    # 文章列表 + 个人简介卡片
├── 文章页 (/posts/[slug])      # 文章内容 + Giscus 评论
├── 分类页 (/categories/[name]) # 按分类筛选文章列表
├── 标签页 (/tags/[name])       # 按标签筛选文章列表
├── 关于页 (/about)             # 个人介绍、联系方式
└── 后台管理 (/studio)          # Sanity Studio（可选独立部署）
```

---

## 核心功能

### 1. 文章系统

**文章属性：**
- 标题（必填）
- 别名 slug（必填，URL 友好格式）
- 摘要（选填，默认取正文前 150 字）
- 正文内容（Markdown / Portable Text）
- 封面图（选填）
- 分类（单选，必填）
- 标签（多选，选填）
- 发布时间（必填）
- 更新时间（自动）
- 精选标记（布尔值）
- 阅读时间（自动计算）

**文章列表展示：**
- 卡片式布局
- 封面图 + 标题 + 摘要 + 元信息
- 分页或无限滚动
- 按时间倒序排列

### 2. 评论系统（Giscus）

- 基于 GitHub Discussions
- 每篇文章对应一个 Discussion
- 支持 Markdown、表情、代码块
- 支持回复嵌套
- 无需用户登录（使用 GitHub 账号）

### 3. 暗黑模式

- 系统偏好自动检测
- 手动切换按钮（导航栏右侧）
- localStorage 持久化
- Tailwind darkMode: 'class' 配置

### 4. SEO 优化

- 自动生成 sitemap.xml
- 每页自定义 title、description
- Open Graph 标签
- 结构化数据（JSON-LD）
- canonical URL

---

## 设计风格

### 颜色系统

**浅色模式：**
```
--bg: #f5f5f0          /* 米白背景 */
--bg-card: #ffffff     /* 纯白卡片 */
--bg-nav: rgba(255,255,255,0.85)  /* 导航栏毛玻璃 */
--text: #111111        /* 主文字 */
--text-muted: #777777  /* 次要文字 */
--text-light: #aaaaaa  /* 辅助文字 */
--accent: #1a56db      /* 强调色 */
--accent-light: #eff4ff /* 强调色浅色 */
--border: #e8e8e4      /* 边框 */
--border-hover: #c7c7c0 /* 悬停边框 */
```

**深色模式：**
```
--bg: #0f0f0f          /* 深灰背景 */
--bg-card: #1a1a1a     /* 深灰卡片 */
--bg-nav: rgba(26,26,26,0.85) /* 导航栏毛玻璃 */
--text: #f5f5f0        /* 主文字 */
--text-muted: #a0a0a0  /* 次要文字 */
--text-light: #666666  /* 辅助文字 */
--accent: #3b82f6      /* 强调色（更亮） */
--accent-light: rgba(59,130,246,0.15)
--border: #2a2a2a      /* 边框 */
--border-hover: #3a3a3a /* 悬停边框 */
```

### 布局规范

- 最大内容宽度：1100px
- 页面内边距：24px（移动端 16px）
- 卡片圆角：12px
- 卡片阴影：0 4px 16px rgba(0,0,0,0.08)
- 导航栏高度：60px
- 字体：'PingFang SC', 'Microsoft YaHei', -apple-system, sans-serif

### 组件规范

**导航栏：**
- 粘性定位（sticky top-0）
- 毛玻璃效果（backdrop-blur）
- Logo + 导航链接 + 主题切换按钮

**文章卡片：**
- 白色背景 + 圆角 + 阴影
- 封面图（可选，16:9 比例）
- 标题（18px，font-bold）
- 摘要（14px，text-muted，2 行截断）
- 元信息（发布时间、分类、阅读时间）

**文章正文：**
- 字体大小 16px，行高 1.75
- 标题层级 h1-h4 样式区分
- 代码块语法高亮
- 图片自适应 + 点击放大
- 引用块左侧边框强调

---

## 数据模型（Sanity Schema）

### Article（文章）

```typescript
{
  name: 'article',
  fields: [
    { name: 'title', type: 'string', validation: Rule => Rule.required() },
    { name: 'slug', type: 'slug', options: { source: 'title' }, validation: Rule => Rule.required() },
    { name: 'excerpt', type: 'text', rows: 3 },
    { name: 'content', type: 'array', of: [{ type: 'block' }, { type: 'image' }, { type: 'code' }] },
    { name: 'coverImage', type: 'image', options: { hotspot: true } },
    { name: 'category', type: 'reference', to: [{ type: 'category' }], validation: Rule => Rule.required() },
    { name: 'tags', type: 'array', of: [{ type: 'reference', to: [{ type: 'tag' }] }] },
    { name: 'publishedAt', type: 'datetime', validation: Rule => Rule.required() },
    { name: 'updatedAt', type: 'datetime' },
    { name: 'featured', type: 'boolean', initialValue: false },
    { name: 'series', type: 'reference', to: [{ type: 'series' }] }
  ]
}
```

### Category（分类）

```typescript
{
  name: 'category',
  fields: [
    { name: 'title', type: 'string', validation: Rule => Rule.required() },
    { name: 'slug', type: 'slug', options: { source: 'title' }, validation: Rule => Rule.required() },
    { name: 'description', type: 'text' }
  ]
}
```

### Tag（标签）

```typescript
{
  name: 'tag',
  fields: [
    { name: 'title', type: 'string', validation: Rule => Rule.required() },
    { name: 'slug', type: 'slug', options: { source: 'title' }, validation: Rule => Rule.required() }
  ]
}
```

### Series（系列）

```typescript
{
  name: 'series',
  fields: [
    { name: 'title', type: 'string', validation: Rule => Rule.required() },
    { name: 'slug', type: 'slug', options: { source: 'title' }, validation: Rule => Rule.required() },
    { name: 'description', type: 'text' }
  ]
}
```

### Site Settings（站点设置）

```typescript
{
  name: 'siteSettings',
  fields: [
    { name: 'title', type: 'string', validation: Rule => Rule.required() },
    { name: 'description', type: 'text' },
    { name: 'author', type: 'string' },
    { name: 'avatar', type: 'image' },
    { name: 'bio', type: 'text' },
    { name: 'socialLinks', type: 'array', of: [{ type: 'object', fields: [{ name: 'platform', type: 'string' }, { name: 'url', type: 'url' }] }] }
  ]
}
```

---

## API 设计（Sanity GROQ 查询）

### 获取文章列表

```groq
*[_type == "article" && publishedAt <= now()] | order(publishedAt desc) [$start...$end] {
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
}
```

### 获取单篇文章

```groq
*[_type == "article" && slug.current == $slug][0] {
  _id,
  title,
  slug,
  excerpt,
  content,
  coverImage,
  "category": category->title,
  "categorySlug": category->slug.current,
  "tags": tags[]->{ title, "slug": slug.current },
  publishedAt,
  updatedAt,
  "readingTime": round(length(pt::text(content)) / 200),
  "series": series->{ title, "slug": slug.current },
  "seriesArticles": *[_type == "article" && series._ref == ^.series._ref] | order(publishedAt asc) { title, "slug": slug.current }
}
```

### 获取分类列表

```groq
*[_type == "category"] | order(title asc) {
  _id,
  title,
  "slug": slug.current,
  description,
  "articleCount": count(*[_type == "article" && references(^._id)])
}
```

### 获取标签列表

```groq
*[_type == "tag"] | order(title asc) {
  _id,
  title,
  "slug": slug.current,
  "articleCount": count(*[_type == "article" && references(^._id)])
}
```

---

## 项目结构

```
my-blog/
├── app/                          # Nuxt 3 应用目录
│   ├── components/               # Vue 组件
│   │   ├── content/              # 内容相关组件
│   │   │   ├── ArticleCard.vue
│   │   │   ├── ArticleList.vue
│   │   │   ├── ArticleContent.vue
│   │   │   ├── CategoryBadge.vue
│   │   │   └── TagList.vue
│   │   ├── layout/               # 布局组件
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppFooter.vue
│   │   │   └── ThemeToggle.vue
│   │   └── ui/                   # 基础 UI 组件
│   │       ├── Button.vue
│   │       └── Card.vue
│   ├── composables/              # 组合式函数
│   │   ├── useSanity.ts          # Sanity 客户端
│   │   ├── useArticles.ts        # 文章数据获取
│   │   └── useTheme.ts           # 主题管理
│   ├── layouts/                  # 布局
│   │   └── default.vue
│   ├── pages/                    # 页面路由
│   │   ├── index.vue             # 首页
│   │   ├── posts/
│   │   │   └── [slug].vue        # 文章详情
│   │   ├── categories/
│   │   │   └── [name].vue        # 分类文章
│   │   ├── tags/
│   │   │   └── [name].vue        # 标签文章
│   │   └── about.vue             # 关于页面
│   ├── assets/                   # 静态资源
│   │   ├── css/
│   │   │   └── main.css
│   │   └── images/
│   ├── types/                    # TypeScript 类型
│   │   └── index.ts
│   ├── utils/                    # 工具函数
│   │   └── helpers.ts
│   └── app.vue
├── studio/                       # Sanity Studio
│   ├── schemas/                  # 数据模型
│   │   ├── article.ts
│   │   ├── category.ts
│   │   ├── tag.ts
│   │   ├── series.ts
│   │   └── siteSettings.ts
│   ├── structure.ts              # Studio 结构配置
│   └── sanity.config.ts
├── public/                       # 公共静态文件
├── nuxt.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── sanity.cli.ts
├── sanity.config.ts
└── package.json
```

---

## 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                        GitHub Repo                          │
│                    (源代码 + GitHub Discussions)             │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│     Vercel      │     │     Sanity      │
│   (前端部署)     │◄────│   (内容管理)     │
│                 │     │                 │
│ • 自动构建       │     │ • CDN 分发       │
│ • 边缘网络       │     │ • 图片优化       │
│ • 自动 HTTPS     │     │ • GROQ API       │
└─────────────────┘     └─────────────────┘
```

### 部署流程

1. 代码推送到 GitHub main 分支
2. Vercel 自动触发构建
3. 构建时从 Sanity 获取内容
4. 生成静态页面（SSG）
5. 部署到 Vercel Edge Network

### 环境变量

**Vercel 环境变量：**
```
NUXT_PUBLIC_SANITY_PROJECT_ID=xxx
NUXT_PUBLIC_SANITY_DATASET=production
NUXT_PUBLIC_SANITY_API_VERSION=2024-05-01
SANITY_API_READ_TOKEN=xxx
NUXT_PUBLIC_GISCUS_REPO=username/repo
NUXT_PUBLIC_GISCUS_REPO_ID=xxx
NUXT_PUBLIC_GISCUS_CATEGORY=Comments
NUXT_PUBLIC_GISCUS_CATEGORY_ID=xxx
```

---

## 性能目标

- Lighthouse Performance Score ≥ 90
- 首屏加载时间 ≤ 1.5s
- Time to Interactive ≤ 3s
- 图片使用 Sanity 自动优化
- 支持 ISR（增量静态再生）

---

## 安全考虑

- Sanity API Token 使用只读权限
- 环境变量不泄露到客户端
- 评论系统使用 Giscus（GitHub 托管）
- 图片使用 Sanity CDN（HTTPS）

---

## 后续扩展（可选）

- [ ] 站内搜索（Algolia / Pagefind）
- [ ] 文章订阅（Newsletter）
- [ ] 阅读进度条
- [ ] 相关文章推荐
- [ ] 文章目录（TOC）
- [ ] RSS 订阅
- [ ] 文章字数统计
- [ ] 访问统计（Umami / Plausible）

---

## 参考资源

- [Nuxt.js 文档](https://nuxt.com/docs)
- [Sanity 文档](https://www.sanity.io/docs)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [Giscus 文档](https://giscus.app/zh-CN)
- [参考网站](https://blog.sanshaokeji.top)

---

**文档版本：** 1.0  
**创建日期：** 2025-05-02  
**状态：** 待实现
