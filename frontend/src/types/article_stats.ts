/**
 * Article Statistics Types
 */

export interface ArticleStats {
  total_pv: number
  total_uv: number
  first_visit?: string
  last_visit?: string
  trend: Array<{
    date: string
    pv: number
    uv: number
  }>
}

export interface ArticleVisit {
  id: number
  article_id: number
  article_slug: string
  ip_address: string
  user_agent?: string
  visited_at: string
}

export interface VisitsListResponse {
  visits: ArticleVisit[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface StatsQueryParams {
  period?: 'daily' | 'weekly' | 'monthly'
  days?: number
}

export interface VisitsQueryParams {
  page?: number
  limit?: number
  start_date?: string
  end_date?: string
  ip_address?: string
}
