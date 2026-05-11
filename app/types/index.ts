// 文章类型
export interface Article {
  _id: string
  title: string
  slug: { current: string }
  excerpt?: string
  content?: any[] | string
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
  published_at?: string
  createdAt?: string
  created_at?: string
  updatedAt?: string
  updated_at?: string
  featured?: boolean
  series?: {
    _id: string
    title: string
    slug: { current: string }
  }
  readingTime?: number
  order?: number
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
  order?: number
  category: string
  categorySlug: string
  tags?: string[]
  publishedAt: string
  published_at?: string
  createdAt?: string
  created_at?: string
  readingTime?: number
}

// 文章详情（完整版）
export interface ArticleDetail extends Article {
  seriesArticles?: {
    title: string
    slug: { current: string }
  }[]
}
