<template>
  <div class="ai-generator-page">
    <div class="page-header">
      <div class="header-left">
        <h1>AI 改写</h1>
        <p>抓取公众号文章并生成草稿或直接发布</p>
      </div>
    </div>

    <n-tabs type="line" animated>
      <n-tab-pane name="single" tab="单篇改写">
        <n-grid :cols="24" :x-gap="24" :y-gap="24" responsive="screen">
          <n-gi :span="24" :md="12">
            <AIRewritePanel />
          </n-gi>
          <n-gi :span="24" :md="12">
            <AIProgress />
          </n-gi>
          <n-gi :span="24">
            <AITaskList />
          </n-gi>
        </n-grid>
      </n-tab-pane>
      <n-tab-pane name="batch" tab="批量改写">
        <AIBatchRewrite />
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import AIRewritePanel from '@/components/admin/ai-rewrite/AIRewritePanel.vue'
import AIProgress from '@/components/admin/ai-rewrite/AIProgress.vue'
import AITaskList from '@/components/admin/ai-rewrite/AITaskList.vue'
import AIBatchRewrite from '@/components/admin/ai-rewrite/AIBatchRewrite.vue'
import { useAIRewriteStore } from '@/stores/ai-rewrite'

const store = useAIRewriteStore()

onMounted(() => {
  store.loadTasks().catch(() => undefined)
})

onBeforeUnmount(() => {
  store.stopPolling()
})
</script>

<style scoped>
.ai-generator-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-left p {
  margin: 0;
  font-size: 14px;
  color: #666;
}
</style>
