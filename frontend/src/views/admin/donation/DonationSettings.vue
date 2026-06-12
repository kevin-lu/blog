<template>
  <div class="donation-settings-page">
    <div class="page-header">
      <h1>打赏设置</h1>
      <n-button type="primary" @click="handleSave">保存设置</n-button>
    </div>

    <n-card title="基本设置" style="margin-top: 16px">
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100"
      >
        <n-form-item label="标题" path="title">
          <n-input
            v-model:value="formData.title"
            placeholder="支持博主"
            maxlength="50"
            show-count
          />
        </n-form-item>

        <n-form-item label="描述文案" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="代码编织梦想，分享传递价值..."
            :rows="4"
            show-count
            maxlength="200"
          />
        </n-form-item>

        <n-form-item label="启用状态" path="enabled">
          <n-switch v-model:value="formData.enabled" />
        </n-form-item>
      </n-form>
    </n-card>

    <n-card title="收款码设置" style="margin-top: 16px">
      <n-grid :cols="2" :x-gap="16">
        <!-- 微信收款码 -->
        <n-grid-item>
          <div class="qr-upload-section">
            <h3>微信收款码</h3>
            <div class="qr-preview">
              <img
                v-if="formData.wechat_qr"
                :src="formData.wechat_qr"
                alt="微信收款码"
                class="qr-preview-image"
              />
              <div v-else class="qr-placeholder">
                <n-icon :component="ImageOutline" size="48" />
                <n-text depth="3">未上传</n-text>
              </div>
            </div>
            <n-upload
              :custom-request="handleWechatUpload"
              :show-file-list="false"
              accept="image/*"
            >
              <n-button style="width: 100%; margin-top: 12px">
                上传微信收款码
              </n-button>
            </n-upload>
          </div>
        </n-grid-item>

        <!-- 支付宝收款码 -->
        <n-grid-item>
          <div class="qr-upload-section">
            <h3>支付宝收款码</h3>
            <div class="qr-preview">
              <img
                v-if="formData.alipay_qr"
                :src="formData.alipay_qr"
                alt="支付宝收款码"
                class="qr-preview-image"
              />
              <div v-else class="qr-placeholder">
                <n-icon :component="ImageOutline" size="48" />
                <n-text depth="3">未上传</n-text>
              </div>
            </div>
            <n-upload
              :custom-request="handleAlipayUpload"
              :show-file-list="false"
              accept="image/*"
            >
              <n-button style="width: 100%; margin-top: 12px">
                上传支付宝收款码
              </n-button>
            </n-upload>
          </div>
        </n-grid-item>
      </n-grid>
    </n-card>

    <n-card title="预览" style="margin-top: 16px">
      <div class="preview-section">
        <DonationCard
          :settings-override="{
            title: formData.title,
            description: formData.description,
            wechat_qr: formData.wechat_qr,
            alipay_qr: formData.alipay_qr,
            enabled: formData.enabled,
          }"
        />
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useMessage } from 'naive-ui'
import { ImageOutline } from '@vicons/ionicons5'
import { donationApi } from '@/api'
import type { DonationSetting, DonationSettingUpdate } from '@/types'
import DonationCard from '@/components/donation/DonationCard.vue'
import { resolveServerAssetUrl } from '@/utils/assets'

const message = useMessage()

const formData = reactive<DonationSettingUpdate>({
  title: '支持博主',
  description: '代码编织梦想，分享传递价值\n每一分支持，都是前行的光',
  enabled: true,
  wechat_qr: undefined,
  alipay_qr: undefined,
})

const formRules = {
  title: {
    required: true,
    message: '请输入标题',
    trigger: 'blur',
  },
}

const handleSave = async () => {
  try {
    await donationApi.updateSettings({
      title: formData.title,
      description: formData.description,
      enabled: formData.enabled,
    })
    message.success('保存成功')
  } catch (error) {
    message.error('保存失败')
  }
}

const handleWechatUpload = async ({ file }: { file: any }) => {
  try {
    console.log('[Upload] Wechat upload triggered, file:', file)
    console.log('[Upload] File object keys:', Object.keys(file))
    
    // Naive UI passes a wrapper object, the real File is in file.file
    const rawFile = file.file || file
    console.log('[Upload] Raw file:', rawFile)
    console.log('[Upload] Raw file type:', rawFile?.constructor?.name)
    
    const result = await donationApi.uploadQRCode('wechat', rawFile as File)
    formData.wechat_qr = resolveServerAssetUrl(result.url)
    message.success('上传成功')
  } catch (error: any) {
    console.error('[Upload] Error:', error)
    console.error('[Upload] Error response:', error.response)
    message.error(`上传失败：${error.response?.data?.error || error.message}`)
  }
}

const handleAlipayUpload = async ({ file }: { file: any }) => {
  try {
    console.log('[Upload] Alipay upload triggered, file:', file)
    
    // Naive UI passes a wrapper object, the real File is in file.file
    const rawFile = file.file || file
    console.log('[Upload] Raw file:', rawFile)
    
    const result = await donationApi.uploadQRCode('alipay', rawFile as File)
    formData.alipay_qr = resolveServerAssetUrl(result.url)
    message.success('上传成功')
  } catch (error: any) {
    console.error('[Upload] Error:', error)
    console.error('[Upload] Error response:', error.response)
    message.error(`上传失败：${error.response?.data?.error || error.message}`)
  }
}

onMounted(async () => {
  try {
    const settings = await donationApi.getSettings()
    if (settings) {
      formData.title = settings.title
      formData.description = settings.description || ''
      formData.enabled = settings.enabled
      formData.wechat_qr = resolveServerAssetUrl(settings.wechat_qr) || undefined
      formData.alipay_qr = resolveServerAssetUrl(settings.alipay_qr) || undefined
    }
  } catch (error) {
    console.error('Failed to load donation settings:', error)
  }
})
</script>

<style scoped>
.donation-settings-page {
  padding: 24px 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  margin: 0;
  font-size: 24px;
}

.qr-upload-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
}

.qr-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  background: #f5f5f5;
  border-radius: 8px;
  border: 2px dashed #d9d9d9;
}

.qr-preview-image {
  max-width: 100%;
  max-height: 180px;
  border-radius: 8px;
}

.qr-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #999;
}

.preview-section {
  display: flex;
  justify-content: center;
}
</style>
