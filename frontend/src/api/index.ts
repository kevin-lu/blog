import { apiClient } from '@/utils/api'
import type {
  Article,
  Category,
  Tag,
  Comment,
  User,
  DashboardStats,
  UploadResponse,
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

interface FlaskArticlesResponse {
  articles: Article[]
  total: number
  page: number
  limit: number
  pages: number
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

export interface AIRewriteTask {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  source_url: string
  rewrite_strategy: 'standard' | 'deep' | 'creative'
  template_type: 'tutorial' | 'concept' | 'comparison' | 'practice'
  auto_publish: boolean
  article_id?: number
  article_slug?: string
  progress?: number
  message?: string
  error?: string
  token_usage?: number
  cost?: number
  created_at: string
  completed_at?: string
  result?: {
    article?: {
      id?: number
      slug?: string
      title?: string
      content?: string
    }
  }
}

export interface AIRewritePayload {
  sourceUrl: string
  rewriteStrategy: 'standard' | 'deep' | 'creative'
  templateType: 'tutorial' | 'concept' | 'comparison' | 'practice'
  autoPublish: boolean
}

const toArticlesResponse = (response: FlaskArticlesResponse): ArticlesResponse => ({
  success: true,
  data: {
    data: response.articles || [],
    total: response.total || 0,
    page: response.page || 1,
    pageSize: response.limit || 10,
    totalPages: response.pages || 0,
  },
})

const toListResponse = <T>(data: T[]) => ({
  success: true,
  data,
})

const normalizeArticlePayload = (data: Partial<Article> & Record<string, any>) => {
  const payload: Record<string, any> = { ...data }

  if ('categoryIds' in payload) {
    payload.category_ids = payload.categoryIds
    delete payload.categoryIds
  }
  if ('tagIds' in payload) {
    payload.tag_ids = payload.tagIds
    delete payload.tagIds
  }

  return payload
}

const settingsArrayToRecord = (settings: any[] | Record<string, any>) => {
  if (!Array.isArray(settings)) return settings || {}

  return settings.reduce<Record<string, any>>((acc, setting) => {
    const value = setting.key_value
    acc[setting.key_name] = value === 'true' ? true : value === 'false' ? false : value
    return acc
  }, {})
}

const settingsRecordToPayload = (data: Record<string, any>) => ({
  settings: Object.entries(data).map(([key_name, key_value]) => ({
    key_name,
    key_value: typeof key_value === 'boolean' ? String(key_value) : key_value ?? '',
  })),
})

// 公开文章 API（不需要认证）
export const articleApi = {
  async getList(params?: { page?: number; limit?: number; category?: string; tag?: string; search?: string }) {
    const response = await apiClient.get<FlaskArticlesResponse>('articles', { params })
    return toArticlesResponse(response)
  },

  async getDetail(slug: string) {
    const response = await apiClient.get<{ article: Article }>(`articles/${slug}`)
    return {
      success: true,
      data: response.article,
    }
  },
}

// 后台管理 API 客户端（需要认证）
export const adminArticleApi = {
  async getList(params?: { page?: number; pageSize?: number; category?: string; tag?: string; search?: string; status?: string }) {
    const apiParams = {
      ...params,
      limit: params?.pageSize,
      status: params?.status ?? '',
    }
    delete (apiParams as any).pageSize

    const response = await apiClient.get<FlaskArticlesResponse>('articles', { params: apiParams })
    return toArticlesResponse(response)
  },

  async getDetail(slug: string) {
    const response = await apiClient.get<{ article: Article }>(`articles/${slug}`)
    return {
      success: true,
      data: response.article,
    }
  },

  async create(data: Partial<Article>) {
    const response = await apiClient.post<{ article: Article }>('articles', normalizeArticlePayload(data as any))
    return {
      success: true,
      data: { article: response.article },
    }
  },

  async update(slug: string, data: Partial<Article>) {
    const response = await apiClient.put<{ article: Article }>(`articles/${slug}`, normalizeArticlePayload(data as any))
    return {
      success: true,
      data: { article: response.article },
    }
  },

  delete(slug: string) {
    return apiClient.delete<{ message: string }>(`articles/${slug}`)
  },
}

export const authApi = {
  async login(username: string, password: string) {
    return apiClient.post<{
      access_token: string
      refresh_token: string
      user: User
    }>('auth/login', {
      username,
      password,
    })
  },

  logout() {
    return apiClient.post<{ message: string }>('auth/logout')
  },

  refresh() {
    return apiClient.post<{ access_token: string }>('auth/refresh')
  },

  getCurrentUser() {
    return apiClient.get<{ user: User }>('auth/me')
  },
}

// 公开分类 API
export const categoryApi = {
  async getList() {
    const response = await apiClient.get<{ categories: Category[] }>('categories')
    return toListResponse(response.categories || [])
  },
}

// 公开标签 API
export const tagApi = {
  async getList() {
    const response = await apiClient.get<{ tags: Tag[] }>('tags')
    return toListResponse(response.tags || [])
  },
}

// 后台分类管理 API
export const adminCategoryApi = {
  async getList() {
    const response = await apiClient.get<{ categories: Category[] }>('categories')
    return toListResponse(response.categories || [])
  },

  async create(data: { name: string; slug: string; description?: string; sort_order?: number }) {
    const response = await apiClient.post<{ category: Category }>('categories', data)
    return {
      success: true,
      data: { category: response.category },
    }
  },

  async update(id: number, data: { name?: string; slug?: string; description?: string; sort_order?: number }) {
    const response = await apiClient.put<{ category: Category }>(`categories/${id}`, data)
    return {
      success: true,
      data: { category: response.category },
    }
  },

  delete(id: number) {
    return apiClient.delete<{ message: string }>(`categories/${id}`)
  },
}

// 后台标签管理 API
export const adminTagApi = {
  async getList() {
    const response = await apiClient.get<{ tags: Tag[] }>('tags')
    return toListResponse(response.tags || [])
  },

  async create(data: { name: string; slug: string; color?: string }) {
    const response = await apiClient.post<{ tag: Tag }>('tags', data)
    return {
      success: true,
      data: { tag: response.tag },
    }
  },

  async update(id: number, data: { name?: string; slug?: string; color?: string }) {
    const response = await apiClient.put<{ tag: Tag }>(`tags/${id}`, data)
    return {
      success: true,
      data: { tag: response.tag },
    }
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
}

export const settingApi = {
  async get() {
    const response = await apiClient.get<{ settings: any[] | Record<string, any> }>('settings')
    return {
      settings: settingsArrayToRecord(response.settings),
    }
  },

  update(data: Record<string, any>) {
    return apiClient.put<{ settings: Record<string, any> }>('settings', settingsRecordToPayload(data))
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
  async getStats() {
    const [articles, categories, tags, comments] = await Promise.all([
      adminArticleApi.getList({ page: 1, pageSize: 5, status: '' }),
      adminCategoryApi.getList(),
      adminTagApi.getList(),
      commentApi.getList({ page: 1, limit: 5 }),
    ])

    const stats: DashboardStats = {
      articleCount: articles.data.total,
      categoryCount: categories.data.length,
      tagCount: tags.data.length,
      commentCount: comments.total,
    }

    return {
      stats,
      recent_articles: articles.data.data,
      recent_comments: comments.comments || [],
    }
  },
}

export const aiRewriteApi = {
  submit(data: AIRewritePayload) {
    return apiClient.post<{ task: AIRewriteTask }>('articles/ai-rewrite', data)
  },

  getTask(taskId: string) {
    return apiClient.get<{ task: AIRewriteTask }>('articles/ai-progress', {
      params: { taskId },
    })
  },

  getTasks() {
    return apiClient.get<{ tasks: AIRewriteTask[] }>('articles/ai-progress')
  },

  clearFinished() {
    return apiClient.post<{ cleared: number }>('articles/ai-tasks/clear')
  },
}

// 文章浏览次数统计 API
export const articleViewApi = {
  async increment(slug: string): Promise<number> {
    const result = await apiClient.post<{ view_count: number }>(`articles/${slug}/view`, {})
    return result.view_count
  },
}
