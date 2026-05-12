import { apiClient } from '@/utils/api'
import type { DonationSetting, DonationSettingUpdate } from '@/types'

export const donationApi = {
  /**
   * Get donation settings (public)
   */
  async getSettings(): Promise<DonationSetting | null> {
    const result = await apiClient.get<{ settings: DonationSetting }>('/donations')
    return result.settings
  },

  /**
   * Update donation settings
   */
  async updateSettings(data: DonationSettingUpdate): Promise<DonationSetting> {
    const result = await apiClient.put<{ settings: DonationSetting }>('/donations', data)
    return result.settings
  },

  /**
   * Upload QR code image
   */
  async uploadQRCode(type: 'wechat' | 'alipay', file: File): Promise<{ url: string }> {
    const formData = new FormData()
    formData.append('type', type)
    formData.append('file', file)
    
    const result = await apiClient.post<{ url: string }>('/donations/upload-qr', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return result
  },
}
