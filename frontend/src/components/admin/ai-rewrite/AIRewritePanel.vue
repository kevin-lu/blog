<template>
  <n-card title="AI 改写" class="rewrite-panel">
    <n-form :model="formData" label-placement="top">
      <n-form-item label="参考文章链接" required>
        <n-input
          v-model:value="formData.sourceUrl"
          placeholder="请输入微信公众号文章链接，例如：https://mp.weixin.qq.com/s/xxx"
          clearable
        />
      </n-form-item>

      <n-form-item label="改写策略">
        <n-radio-group v-model:value="formData.rewriteStrategy">
          <n-space>
            <n-radio value="standard">标准改写</n-radio>
            <n-radio value="deep">深度改写</n-radio>
            <n-radio value="creative">创意改写</n-radio>
          </n-space>
        </n-radio-group>
      </n-form-item>

      <n-form-item label="文章模板">
        <n-radio-group v-model:value="formData.templateType">
          <n-space>
            <n-radio value="tutorial">教程类</n-radio>
            <n-radio value="concept">概念类</n-radio>
            <n-radio value="comparison">对比类</n-radio>
            <n-radio value="practice">实战类</n-radio>
          </n-space>
        </n-radio-group>
      </n-form-item>

      <n-form-item label="发布设置">
        <n-radio-group v-model:value="formData.autoPublish">
          <n-space>
            <n-radio :value="false">保存为草稿</n-radio>
            <n-radio :value="true">立即发布</n-radio>
          </n-space>
        </n-radio-group>
      </n-form-item>

      <n-alert type="info" :show-icon="false" class="panel-tip">
        需要在 `backend/.env` 中配置 `MINIMAX_API_KEY`。改写任务会在后端异步执行，刷新页面后历史任务仍可查看。
      </n-alert>

      <n-space>
        <n-button type="primary" :loading="store.isLoading" @click="handleSubmit">
          开始改写
        </n-button>
        <n-button @click="handleReset">
          重置
        </n-button>
      </n-space>
    </n-form>
  </n-card>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useMessage } from 'naive-ui'
import { useAIRewriteStore } from '@/stores/ai-rewrite'

const message = useMessage()
const store = useAIRewriteStore()

const formData = reactive({
  sourceUrl: '',
  rewriteStrategy: 'standard' as 'standard' | 'deep' | 'creative',
  templateType: 'tutorial' as 'tutorial' | 'concept' | 'comparison' | 'practice',
  autoPublish: false,
})

const handleSubmit = async () => {
  if (!formData.sourceUrl.trim()) {
    message.error('请输入文章链接')
    return
  }

  try {
    await store.submitRewrite({
      sourceUrl: formData.sourceUrl.trim(),
      rewriteStrategy: formData.rewriteStrategy,
      templateType: formData.templateType,
      autoPublish: formData.autoPublish,
    })
    message.success('任务已提交，后端开始处理')
  } catch (error: any) {
    message.error(error?.response?.data?.error || '提交失败')
  }
}

const handleReset = () => {
  formData.sourceUrl = ''
  formData.rewriteStrategy = 'standard'
  formData.templateType = 'tutorial'
  formData.autoPublish = false
}
</script>

<style scoped>
.rewrite-panel {
  height: 100%;
}

.panel-tip {
  margin-bottom: 20px;
}
</style>
