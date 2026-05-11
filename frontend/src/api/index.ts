import { apiClient } from '@/utils/api'
import type {
  Article,
  Category,
  Tag,
  Comment,
  SiteSetting,
  User,
  DashboardStats,
  UploadResponse,
  ApiResponse,
} from '@/types'

interface ArticlesResponse {
  success: boolean
  data: {
    data: Article[]
    total: number
    page: number
    pageSize: number
    totalPages: number
  }
}

interface CommentWithUser extends Comment {
  author_name?: string
  author_email?: string
  article_title?: string
  content?: string
}

interface CommentsResponse {
  comments: CommentWithUser[]
  total: number
  page: number
  limit: number
  pages: number
}

// 公开文章 API（不需要认证）
export const articleApi = {
  getList(params?: { page?: number; limit?: number; category?: string; tag?: string; search?: string }) {
    return apiClient.get<ArticlesResponse>('articles', { params })
  },

  getDetail(slug: string) {
    return apiClient.get<{ success: boolean; data: Article }>(`articles/${slug}`)
  },
}

// 后台管理 API 客户端（需要认证）
export const adminArticleApi = {
  getList(params?: { page?: number; pageSize?: number; category?: string; tag?: string; search?: string; status?: string }) {
    return apiClient.get<ArticlesResponse>('admin/articles', { params })
  },

  getDetail(slug: string) {
    return apiClient.get<{ success: boolean; data: Article }>(`admin/articles/${slug}`)
  },

  create(data: Partial<Article>) {
    return apiClient.post<{ success: boolean; data: { article: Article } }>('admin/articles', data)
  },

  update(slug: string, data: Partial<Article>) {
    return apiClient.put<{ success: boolean; data: { article: Article } }>(`admin/articles/${slug}`, data)
  },

  delete(slug: string) {
    return apiClient.delete<{ success: boolean; message: string }>(`admin/articles/${slug}`)
  },
}

export const authApi = {
  async login(username: string, password: string) {
    const response = await apiClient.post<{ 
      success: boolean; 
      data: { 
        token: string; 
        admin: { id: number; username: string; email: string; avatar: string | null; role: string } 
      }
    }>('admin/auth/login', {
      username,
      password,
    })

    return {
      access_token: response.data.token,
      refresh_token: '',
      user: response.data.admin,
    }
  },

  logout() {
    return apiClient.post<{ message: string }>('admin/auth/logout')
  },

  refresh() {
    return apiClient.post<{ access_token: string }>('admin/auth/refresh')
  },

  getCurrentUser() {
    return apiClient.get<{ user: User }>('admin/auth/me')
  },
}

// 公开分类 API
export const categoryApi = {
  getList() {
    return apiClient.get<{ success: boolean; data: Category[] }>('categories')
  },
}

// 公开标签 API
export const tagApi = {
  getList() {
    return apiClient.get<{ success: boolean; data: Tag[] }>('tags')
  },
}

// 后台分类管理 API
export const adminCategoryApi = {
  getList() {
    return apiClient.get<{ success: boolean; data: Category[] }>('categories')
  },

  create(data: { name: string; slug: string; description?: string; sort_order?: number }) {
    return apiClient.post<{ success: boolean; data: { category: Category } }>('categories', data)
  },

  update(id: number, data: { name?: string; slug?: string; description?: string; sort_order?: number }) {
    return apiClient.put<{ success: boolean; data: { category: Category } }>(`categories/${id}`, data)
  },

  delete(id: number) {
    return apiClient.delete<{ success: boolean; message: string }>(`categories/${id}`)
  },
}

// 后台标签管理 API
export const adminTagApi = {
  getList() {
    return apiClient.get<{ success: boolean; data: Tag[] }>('tags')
  },

  create(data: { name: string; slug: string; color?: string }) {
    return apiClient.post<{ success: boolean; data: { tag: Tag } }>('tags', data)
  },

  update(id: number, data: { name?: string; slug?: string; color?: string }) {
    return apiClient.put<{ success: boolean; data: { tag: Tag } }>(`tags/${id}`, data)
  },

  delete(id: number) {
    return apiClient.delete<{ success: boolean; message: string }>(`tags/${id}`)
  },
}

export const commentApi = {
  getList(params?: { article_slug?: string; status?: string; page?: number; limit?: number }) {
    return apiClient.get<CommentsResponse>('comments', {
      params,
    })
  },

  delete(id: number) {
    return apiClient.delete<{ message: string }>(`comments/${id}`)
  },

  approve(id: number) {
    return apiClient.put<{ comment: Comment }>(`comments/${id}/approve`)
  },

  reject(id: number) {
    return apiClient.put<{ comment: Comment }>(`comments/${id}/reject`)
  },

  reply(id: number, data: { content: string; parent_id?: number }) {
    return apiClient.post<{ comment: Comment }>(`comments/${id}/reply`, data)
  },
}

export const settingApi = {
  get() {
    return apiClient.get<{ settings: Record<string, any> }>('settings')
  },

  update(data: Record<string, any>) {
    return apiClient.put<{ settings: Record<string, any> }>('settings', data)
  },
}

export const uploadApi = {
  upload(file: File, type: 'image' | 'document' = 'image') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('type', type)

    return apiClient.post<UploadResponse>('upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

export const dashboardApi = {
  getStats() {
    return apiClient.get<{
      stats: DashboardStats
      recent_articles: Article[]
      recent_comments: CommentWithUser[]
    }>('admin/dashboard/stats')
  },
}
