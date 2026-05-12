<template>
  <n-modal
    v-model:show="showModal"
    preset="card"
    title="扫码支持"
    :style="{ width: '400px' }"
  >
    <div class="donation-modal">
      <div class="qr-container">
        <img :src="currentQr" alt="收款码" class="qr-image" />
      </div>
      <n-space justify="center" style="margin-top: 16px">
        <n-tag
          :type="qrType === 'wechat' ? 'success' : 'warning'"
          size="large"
        >
          {{ qrType === 'wechat' ? '微信' : '支付宝' }}
        </n-tag>
      </n-space>
      <n-text depth="3" style="margin-top: 12px; display: block; text-align: center">
        扫码后完成支付
      </n-text>
    </div>
  </n-modal>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showModal = ref(false)
const currentQr = ref('')
const qrType = ref<'wechat' | 'alipay'>('wechat')

const open = (qr: string, type: 'wechat' | 'alipay') => {
  currentQr.value = qr
  qrType.value = type
  showModal.value = true
}

const close = () => {
  showModal.value = false
}

defineExpose({ open, close })
</script>

<style scoped>
.donation-modal {
  padding: 20px;
}

.qr-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.qr-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}
</style>
