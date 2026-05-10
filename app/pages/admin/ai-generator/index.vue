<!-- app/pages/admin/ai-generator/index.vue -->

<template>
  <div class="ai-generator-page">
    <n-grid :cols="24" :x-gap="20">
      <n-gi :span="24">
        <n-page title="AI 智能改写">
          <template #header>
            <n-space align="center">
              <n-text style="font-size: 24px; font-weight: bold">
                🤖 AI 智能改写
              </n-text>
              <n-text depth="3">
                输入文章链接，AI 自动改写并发布
              </n-text>
            </n-space>
          </template>

          <AIRewritePanel />
          <AIProgress />
          <AITaskList />
        </n-page>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAIRewriteStore } from '@/stores/ai-rewrite';
import AIRewritePanel from '@/components/admin/ai-rewrite/AIRewritePanel.vue';
import AIProgress from '@/components/admin/ai-rewrite/AIProgress.vue';
import AITaskList from '@/components/admin/ai-rewrite/AITaskList.vue';

const store = useAIRewriteStore();

onMounted(() => {
  store.loadTasks();
});
</script>

<style scoped>
.ai-generator-page {
  padding: 24px;
}
</style>
