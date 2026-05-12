import request from '@/utils/request'
import type { DonationSetting, DonationSettingUpdate } from '@/types'

export const donationApi = {
  /**
   * Get donation settings (public)
   */
  getSettings(): Promise<DonationSetting | null> {
    return request.get('/donations').then(res => res.data.settings)
  },

  /**
   * Update donation settings
   */
  updateSettings(data: DonationSettingUpdate): Promise<DonationSetting> {
    return request.put('/donations', data).then(res => res.data.settings)
  },

  /**
   * Upload QR code image
   */
  uploadQRCode(type: 'wechat' | 'alipay', file: File): Promise<{ url: string }> {
    const formData = new FormData()
    formData.append('type', type)
    formData.append('file', file)
    
    return request.post('/donations/upload-qr', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}
