<template>
  <n-card
    v-if="settings && settings.enabled"
    class="donation-card"
    title="❤️ 支持博主"
    content-style="padding: 16px;"
  >
    <div class="donation-content">
      <!-- 诗意文案 -->
      <div class="donation-text">
        <p v-if="settings.description">
          {{ settings.description }}
        </p>
        <p v-else>
          代码编织梦想，分享传递价值<br />
          每一分支持，都是前行的光
        </p>
      </div>

      <!-- 收款码展示 -->
      <div class="qr-codes">
        <div
          v-if="settings.wechat_qr"
          class="qr-item"
          @click="showQr(settings.wechat_qr, 'wechat')"
        >
          <img :src="settings.wechat_qr" alt="微信收款码" class="qr-image" />
          <n-tag type="success" size="small" style="margin-top: 8px">
            微信
          </n-tag>
        </div>
        <div
          v-if="settings.alipay_qr"
          class="qr-item"
          @click="showQr(settings.alipay_qr, 'alipay')"
        >
          <img :src="settings.alipay_qr" alt="支付宝收款码" class="qr-image" />
          <n-tag type="warning" size="small" style="margin-top: 8px">
            支付宝
          </n-tag>
        </div>
      </div>

      <!-- 感谢语 -->
      <div class="donation-footer">
        <n-text depth="3" style="font-size: 12px">
          💝 感谢您的支持
        </n-text>
      </div>
    </div>

    <!-- 二维码查看模态框 -->
    <DonationModal ref="modalRef" />
  </n-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { donationApi } from '@/api'
import type { DonationSetting } from '@/types'
import DonationModal from './DonationModal.vue'
import { resolveServerAssetUrl } from '@/utils/assets'

const settings = ref<DonationSetting | null>(null)
const modalRef = ref<InstanceType<typeof DonationModal>>()

const showQr = (qr: string, type: 'wechat' | 'alipay') => {
  modalRef.value?.open(resolveServerAssetUrl(qr), type)
}

onMounted(async () => {
  try {
    const data = await donationApi.getSettings()
    settings.value = data ? {
      ...data,
      wechat_qr: resolveServerAssetUrl(data.wechat_qr),
      alipay_qr: resolveServerAssetUrl(data.alipay_qr),
    } : data
  } catch (error) {
    console.error('Failed to load donation settings:', error)
  }
})
</script>

<style scoped>
.donation-card {
  margin-top: 16px;
  border: 1px solid #ffd1dc;
}

.donation-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.donation-text {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  white-space: pre-line;
}

.qr-codes {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.qr-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.qr-item:hover {
  transform: scale(1.05);
}

.qr-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid #f0f0f0;
}

.donation-footer {
  text-align: center;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}
</style>
