export interface User {
  id: number
  username: string
  email: string
  avatar?: string
  role: string
  created_at: string
}

export interface Article {
  id: number
  slug: string
  title: string
  description?: string
  content?: string
  cover_image?: string
  status: 'draft' | 'published' | 'archived'
  published_at?: string
  publishedAt?: string
  created_at: string
  createdAt?: string
  updated_at: string
  updatedAt?: string
  categories?: Category[]
  tags?: Tag[]
  view_count?: number  // 浏览次数
  comment_count?: number
}

export interface Category {
  id: number
  name: string
  slug: string
  description?: string
  sort_order: number
  created_at: string
  article_count?: number
}

export interface Tag {
  id: number
  name: string
  slug: string
  color?: string
  created_at: string
  article_count?: number
}

export interface Comment {
  id: number
  article_slug: string
  github_id?: string
  status: 'pending' | 'approved' | 'rejected'
  is_pinned: boolean
  created_at: string
  content?: string
  author_name?: string
  author_email?: string
  parent_id?: number
  article_title?: string
}

export interface SiteSetting {
  id: number
  key_name: string
  key_value?: string
  description?: string
  created_at: string
}

export interface DashboardStats {
  articleCount: number
  categoryCount: number
  tagCount: number
  commentCount: number
}

export interface UploadResponse {
  url: string
  thumbnail_url?: string
  filename?: string
  size?: number
}

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}
