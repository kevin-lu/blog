export const mockArticles = [
  {
    _id: 'article-1',
    title: 'Vue 3 组合式 API 完全指南',
    slug: { current: 'vue3-composition-api-guide' },
    excerpt: '深入理解 Vue 3 的组合式 API，掌握响应式系统的核心原理',
    content: [
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '什么是组合式 API' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: '组合式 API 是 Vue 3 引入的一种新的组织组件逻辑的方式。它允许我们将相关功能的代码组织在一起，而不是按照选项类型分离。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: 'setup 函数' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'setup 是组合式 API 的入口点，它在组件创建之前执行，并且返回一个对象，该对象的属性和方法可以在模板中使用。' }]
      },
      {
        _type: 'block',
        style: 'h3',
        children: [{ text: 'ref 和 reactive' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'ref 用于创建基本类型的响应式数据，而 reactive 用于创建对象类型的响应式数据。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '计算属性和监听器' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: '使用 computed 函数可以创建计算属性，使用 watch 函数可以监听响应式数据的变化。' }]
      }
    ],
    publishedAt: '2024-01-15T10:00:00Z',
    category: { _id: 'cat-1', title: '前端开发', slug: { current: 'frontend' } },
    tags: [
      { _id: 'tag-1', title: 'Vue', slug: { current: 'vue' } },
      { _id: 'tag-2', title: 'JavaScript', slug: { current: 'javascript' } }
    ],
    featured: true,
    readingTime: 15,
    order: 1
  },
  {
    _id: 'article-2',
    title: 'TypeScript 进阶技巧',
    slug: { current: 'typescript-advanced-tips' },
    excerpt: '提升 TypeScript 技能水平的高级技巧和最佳实践',
    content: [
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '类型推断' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'TypeScript 具有强大的类型推断能力，能够根据变量的初始值自动推断出变量的类型。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '泛型' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: '泛型允许我们创建可复用的组件，能够支持多种类型而不是单一类型。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '类型守卫' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: '类型守卫是在运行时检查变量类型的函数，它可以帮助我们在代码块中缩窄类型。' }]
      }
    ],
    publishedAt: '2024-01-20T14:30:00Z',
    category: { _id: 'cat-1', title: '前端开发', slug: { current: 'frontend' } },
    tags: [
      { _id: 'tag-2', title: 'JavaScript', slug: { current: 'javascript' } },
      { _id: 'tag-3', title: 'TypeScript', slug: { current: 'typescript' } }
    ],
    featured: false,
    readingTime: 12,
    order: 2
  },
  {
    _id: 'article-3',
    title: 'Nuxt 3 完全入门教程',
    slug: { current: 'nuxt3-getting-started' },
    excerpt: '从零开始学习 Nuxt 3，构建现代化的 SSR 应用',
    content: [
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: 'Nuxt 3 简介' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'Nuxt 3 是一个基于 Vue 3 的全栈框架，支持服务端渲染、静态站点生成和客户端渲染。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '目录结构' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'Nuxt 3 有清晰的目录结构，包括 pages、components、composables、layouts 等目录。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '自动导入' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'Nuxt 3 会自动导入 composables、components 和 utils 目录中的内容，无需手动 import。' }]
      }
    ],
    publishedAt: '2024-02-01T09:00:00Z',
    category: { _id: 'cat-1', title: '前端开发', slug: { current: 'frontend' } },
    tags: [
      { _id: 'tag-1', title: 'Vue', slug: { current: 'vue' } },
      { _id: 'tag-4', title: 'Nuxt', slug: { current: 'nuxt' } }
    ],
    featured: true,
    readingTime: 20,
    order: 3
  },
  {
    _id: 'article-4',
    title: 'Node.js 性能优化实战',
    slug: { current: 'nodejs-performance-optimization' },
    excerpt: '深入了解 Node.js 性能优化的核心技巧和实战经验',
    content: [
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '性能优化的重要性' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: '在生产环境中，性能优化可以显著提升用户体验和降低服务器成本。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '事件循环' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: '理解 Node.js 的事件循环机制是性能优化的基础。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '缓存策略' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: '使用 Redis 等缓存系统可以显著减少数据库查询，提升响应速度。' }]
      }
    ],
    publishedAt: '2024-02-10T16:00:00Z',
    category: { _id: 'cat-2', title: '后端开发', slug: { current: 'backend' } },
    tags: [
      { _id: 'tag-5', title: 'Node.js', slug: { current: 'nodejs' } },
      { _id: 'tag-6', title: '性能优化', slug: { current: 'performance' } }
    ],
    featured: false,
    readingTime: 18,
    order: 4
  },
  {
    _id: 'article-5',
    title: 'Docker 容器化部署指南',
    slug: { current: 'docker-deployment-guide' },
    excerpt: '使用 Docker 轻松实现应用的容器化部署',
    content: [
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: 'Docker 基础' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'Docker 是一个开源的容器化平台，可以将应用及其依赖打包成轻量级的容器。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: 'Dockerfile 编写' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'Dockerfile 是构建 Docker 镜像的脚本，定义了镜像的结构和配置。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: 'Docker Compose' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'Docker Compose 可以定义和运行多容器应用，简化部署流程。' }]
      }
    ],
    publishedAt: '2024-02-15T11:00:00Z',
    category: { _id: 'cat-3', title: 'DevOps', slug: { current: 'devops' } },
    tags: [
      { _id: 'tag-7', title: 'Docker', slug: { current: 'docker' } },
      { _id: 'tag-8', title: 'Kubernetes', slug: { current: 'kubernetes' } }
    ],
    featured: false,
    readingTime: 25,
    order: 5
  },
  {
    _id: 'article-6',
    title: 'React Hooks 最佳实践',
    slug: { current: 'react-hooks-best-practices' },
    excerpt: '掌握 React Hooks 的使用技巧，编写更优雅的组件代码',
    content: [
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: 'useState 基础' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'useState 是最基础的 Hook，用于在函数组件中添加状态。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: 'useEffect 详解' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'useEffect 用于处理副作用，可以替代 componentDidMount、componentDidUpdate 等生命周期方法。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '自定义 Hook' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: '自定义 Hook 可以提取组件逻辑到可复用的函数中。' }]
      }
    ],
    publishedAt: '2024-02-20T13:30:00Z',
    category: { _id: 'cat-1', title: '前端开发', slug: { current: 'frontend' } },
    tags: [
      { _id: 'tag-9', title: 'React', slug: { current: 'react' } },
      { _id: 'tag-2', title: 'JavaScript', slug: { current: 'javascript' } }
    ],
    featured: true,
    readingTime: 16,
    order: 6
  },
  {
    _id: 'article-7',
    title: 'Python 数据分析入门',
    slug: { current: 'python-data-analysis-intro' },
    excerpt: '使用 Python 和 Pandas 开始你的数据分析之旅',
    content: [
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: 'Pandas 基础' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'Pandas 是 Python 最流行的数据分析库，提供了 DataFrame 等强大的数据结构。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '数据清洗' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: '数据清洗是数据分析的第一步，包括处理缺失值、重复值等。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '数据可视化' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: '使用 Matplotlib 和 Seaborn 可以将数据可视化，帮助理解数据特征。' }]
      }
    ],
    publishedAt: '2024-02-25T10:00:00Z',
    category: { _id: 'cat-4', title: '数据科学', slug: { current: 'data-science' } },
    tags: [
      { _id: 'tag-10', title: 'Python', slug: { current: 'python' } },
      { _id: 'tag-11', title: '数据分析', slug: { current: 'data-analysis' } }
    ],
    featured: false,
    readingTime: 22,
    order: 7
  },
  {
    _id: 'article-8',
    title: 'Git 高级技巧',
    slug: { current: 'git-advanced-tips' },
    excerpt: '提升 Git 使用效率的高级命令和技巧',
    content: [
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '交互式变基' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'git rebase -i 可以交互式地修改提交历史，合并、拆分、重排提交。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: 'Git Hooks' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'Git Hooks 可以在特定事件发生时自动执行脚本，如提交前检查代码格式。' }]
      },
      {
        _type: 'block',
        style: 'h2',
        children: [{ text: '子模块' }]
      },
      {
        _type: 'block',
        style: 'normal',
        children: [{ text: 'Git 子模块允许在一个仓库中嵌入另一个仓库。' }]
      }
    ],
    publishedAt: '2024-03-01T15:00:00Z',
    category: { _id: 'cat-5', title: '开发工具', slug: { current: 'dev-tools' } },
    tags: [
      { _id: 'tag-12', title: 'Git', slug: { current: 'git' } },
      { _id: 'tag-13', title: '版本控制', slug: { current: 'version-control' } }
    ],
    featured: false,
    readingTime: 14,
    order: 8
  }
]

export const mockCategories = [
  { _id: 'cat-1', title: '前端开发', slug: { current: 'frontend' }, description: '前端技术相关文章', articleCount: 4 },
  { _id: 'cat-2', title: '后端开发', slug: { current: 'backend' }, description: '后端技术相关文章', articleCount: 1 },
  { _id: 'cat-3', title: 'DevOps', slug: { current: 'devops' }, description: '运维和部署相关文章', articleCount: 1 },
  { _id: 'cat-4', title: '数据科学', slug: { current: 'data-science' }, description: '数据分析和机器学习相关文章', articleCount: 1 },
  { _id: 'cat-5', title: '开发工具', slug: { current: 'dev-tools' }, description: '开发工具和效率提升相关文章', articleCount: 1 }
]

export const mockTags = [
  { _id: 'tag-1', title: 'Vue', slug: { current: 'vue' } },
  { _id: 'tag-2', title: 'JavaScript', slug: { current: 'javascript' } },
  { _id: 'tag-3', title: 'TypeScript', slug: { current: 'typescript' } },
  { _id: 'tag-4', title: 'Nuxt', slug: { current: 'nuxt' } },
  { _id: 'tag-5', title: 'Node.js', slug: { current: 'nodejs' } },
  { _id: 'tag-6', title: '性能优化', slug: { current: 'performance' } },
  { _id: 'tag-7', title: 'Docker', slug: { current: 'docker' } },
  { _id: 'tag-8', title: 'Kubernetes', slug: { current: 'kubernetes' } },
  { _id: 'tag-9', title: 'React', slug: { current: 'react' } },
  { _id: 'tag-10', title: 'Python', slug: { current: 'python' } },
  { _id: 'tag-11', title: '数据分析', slug: { current: 'data-analysis' } },
  { _id: 'tag-12', title: 'Git', slug: { current: 'git' } },
  { _id: 'tag-13', title: '版本控制', slug: { current: 'version-control' } }
]

export const mockSiteSettings = {
  title: '我的技术博客',
  bio: '分享技术、探索创新、启迪思想',
  description: '一个专注于前端开发和 DevOps 的技术博客',
  logo: null,
  social: {
    github: 'https://github.com',
    twitter: 'https://twitter.com',
    email: 'hello@example.com'
  }
}
