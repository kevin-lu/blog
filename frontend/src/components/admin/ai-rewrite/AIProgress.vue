<template>
  <n-card title="任务进度" class="progress-panel">
    <div v-if="store.currentTask" class="task-body">
      <div class="status-row">
        <n-tag :type="statusType">
          {{ statusText }}
        </n-tag>
        <span class="task-time">{{ formatDateTime(store.currentTask.created_at) }}</span>
      </div>

      <n-progress
        type="line"
        :percentage="store.currentTask.progress || 0"
        :status="progressStatus"
        indicator-placement="inside"
      />

      <n-descriptions :column="1" label-placement="left" size="small" class="task-meta">
        <n-descriptions-item label="源链接">
          <n-a :href="store.currentTask.source_url" target="_blank">
            {{ store.currentTask.source_url }}
          </n-a>
        </n-descriptions-item>
        <n-descriptions-item label="改写策略">
          {{ strategyLabel }}
        </n-descriptions-item>
        <n-descriptions-item label="处理信息">
          {{ store.currentTask.message || '-' }}
        </n-descriptions-item>
        <n-descriptions-item v-if="store.currentTask.token_usage" label="Token">
          {{ store.currentTask.token_usage }}
        </n-descriptions-item>
        <n-descriptions-item v-if="store.currentTask.cost" label="预估成本">
          ¥{{ store.currentTask.cost.toFixed(4) }}
        </n-descriptions-item>
        <n-descriptions-item v-if="store.currentTask.error" label="错误信息">
          <span class="error-text">{{ store.currentTask.error }}</span>
        </n-descriptions-item>
      </n-descriptions>

      <n-space v-if="store.currentTask.article_slug" class="task-actions">
        <n-button @click="goToEdit(store.currentTask.article_slug)">
          编辑草稿
        </n-button>
        <n-button
          v-if="store.currentTask.auto_publish"
          type="primary"
          @click="goToArticle(store.currentTask.article_slug)"
        >
          查看文章
        </n-button>
      </n-space>
    </div>

    <n-empty v-else description="当前没有正在跟踪的 AI 任务" />
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAIRewriteStore } from '@/stores/ai-rewrite'
import { formatDateTime } from '@/utils/date'

const router = useRouter()
const store = useAIRewriteStore()

const statusText = computed(() => {
  const map: Record<string, string> = {
    pending: '等待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
  }
  return map[store.currentTask?.status || 'pending'] || store.currentTask?.status || '-'
})

const statusType = computed(() => {
  const map: Record<string, 'default' | 'info' | 'success' | 'warning' | 'error'> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'error',
  }
  return map[store.currentTask?.status || 'pending'] || 'default'
})

const progressStatus = computed(() => {
  if (store.currentTask?.status === 'failed') return 'error'
  if (store.currentTask?.status === 'completed') return 'success'
  return 'default'
})

const strategyLabel = computed(() => {
  const map: Record<string, string> = {
    standard: '标准改写',
    deep: '深度改写',
    creative: '创意改写',
  }
  return map[store.currentTask?.rewrite_strategy || 'standard'] || store.currentTask?.rewrite_strategy || '-'
})

const goToEdit = (slug: string) => {
  router.push(`/admin/articles/edit/${slug}`)
}

const goToArticle = (slug: string) => {
  window.open(`/posts/${slug}`, '_blank')
}
</script>

<style scoped>
.progress-panel {
  height: 100%;
}

.task-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.task-time {
  font-size: 13px;
  color: #666;
}

.task-meta {
  margin-top: 4px;
}

.task-actions {
  margin-top: 8px;
}

.error-text {
  color: #d03050;
}
</style>
