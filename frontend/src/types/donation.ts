export interface DonationSetting {
  id: number
  title: string
  description: string | null
  wechat_qr: string | null
  alipay_qr: string | null
  enabled: boolean
  created_at: string
  updated_at: string
}

export interface DonationSettingUpdate {
  title?: string
  description?: string
  enabled?: boolean
  wechat_qr?: string
  alipay_qr?: string
}
