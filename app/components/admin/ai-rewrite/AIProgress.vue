<!-- app/components/admin/ai-rewrite/AIProgress.vue -->

<template>
  <div class="ai-progress">
    <n-card title="📊 改写进度" size="large">
      <div v-if="store.currentTask" class="current-task">
        <n-alert :type="getAlertType(store.currentTask.status)">
          <template #header>
            <n-space align="center">
              <n-icon :component="getStatusIcon(store.currentTask.status)" />
              <span>{{ getStatusText(store.currentTask.status) }}</span>
            </n-space>
          </template>
          
          <n-descriptions :column="2" bordered>
            <n-descriptions-item label="任务 ID">
              {{ store.currentTask.id }}
            </n-descriptions-item>
            <n-descriptions-item label="状态">
              <n-tag :type="getStatusTagType(store.currentTask.status)">
                {{ store.currentTask.status }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="源链接">
              <n-a :href="store.currentTask.sourceUrl" target="_blank">
                {{ store.currentTask.sourceUrl }}
              </n-a>
            </n-descriptions-item>
            <n-descriptions-item label="改写策略">
              {{ getStrategyName(store.currentTask.rewriteStrategy) }}
            </n-descriptions-item>
            <n-descriptions-item v-if="store.currentTask.tokenUsage" label="Token 消耗">
              {{ store.currentTask.tokenUsage }}
            </n-descriptions-item>
            <n-descriptions-item v-if="store.currentTask.cost" label="成本">
              ¥{{ (store.currentTask.cost * 7).toFixed(4) }}
            </n-descriptions-item>
          </n-descriptions>

          <div v-if="store.currentTask.status === 'completed'" class="actions">
            <n-space>
              <n-button
                v-if="store.currentTask.articleSlug"
                type="primary"
                @click="goToArticle(store.currentTask.articleSlug)"
              >
                查看文章
              </n-button>
              <n-button
                v-if="store.currentTask.articleId"
                secondary
                @click="goToEdit(store.currentTask.articleId)"
              >
                编辑草稿
              </n-button>
            </n-space>
          </div>

          <div v-if="store.currentTask.status === 'failed'" class="error">
            <n-text type="error">
              错误信息：{{ store.currentTask.error }}
            </n-text>
          </div>
        </n-alert>
      </div>

      <div v-else class="no-task">
        <n-empty description="当前没有进行中的任务" />
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAIRewriteStore } from '@/stores/ai-rewrite';
import { CheckCircleOutline, CloseCircleOutline, TimeOutline, SyncOutline } from '@vicons/ionicons5';

const router = useRouter();
const store = useAIRewriteStore();

const getAlertType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'error',
  };
  return map[status];
};

const getStatusIcon = (status: string) => {
  const map: Record<string, any> = {
    pending: TimeOutline,
    processing: SyncOutline,
    completed: CheckCircleOutline,
    failed: CloseCircleOutline,
  };
  return map[status];
};

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待处理',
    processing: '正在改写',
    completed: '改写完成',
    failed: '改写失败',
  };
  return map[status];
};

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'error',
  };
  return map[status];
};

const getStrategyName = (strategy: string) => {
  const map: Record<string, string> = {
    standard: '标准改写',
    deep: '深度改写',
    creative: '创意改写',
  };
  return map[strategy];
};

const goToArticle = (slug: string) => {
  window.open(`/posts/${slug}`, '_blank');
};

const goToEdit = (articleId: number) => {
  router.push(`/admin/articles/edit/${articleId}`);
};
</script>

<style scoped>
.ai-progress {
  max-width: 800px;
  margin: 20px auto;
}

.current-task {
  margin-top: 20px;
}

.actions {
  margin-top: 20px;
  text-align: right;
}

.error {
  margin-top: 16px;
  padding: 12px;
  background: #fee;
  border-radius: 4px;
}
</style>
