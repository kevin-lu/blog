import { apiClient } from '@/utils/api'

export interface SiteSettings {
  // Basic Settings
  site_name: string
  site_description: string
  site_logo: string
  site_url: string
  site_keywords: string
  og_image: string

  // Social Links
  github_url: string
  twitter_url: string
  weibo_url: string
  email: string

  // About Page Settings
  about_welcome_title: string
  about_welcome_content: string
  about_author_title: string
  about_author_content: string
  about_tech_stack_title: string
  about_tech_stack_items: string[]
  about_contact_title: string
  about_contact_email: string
  about_contact_github: string
  about_contact_github_label: string

  // Comment Settings
  comment_require_review: boolean
  comment_enabled: boolean
}

export interface SettingsResponse {
  settings: SiteSettings
}

export const settingApi = {
  /**
   * Get all site settings
   */
  get(): Promise<SettingsResponse> {
    return apiClient.get('/settings')
  },

  /**
   * Update site settings
   */
  update(data: Partial<SiteSettings>): Promise<SettingsResponse> {
    return apiClient.put('/settings', data)
  },

  /**
   * Reset settings to defaults
   */
  reset(): Promise<SettingsResponse> {
    return apiClient.post('/settings/reset')
  },
}
