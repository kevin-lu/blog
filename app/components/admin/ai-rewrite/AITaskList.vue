<!-- app/components/admin/ai-rewrite/AITaskList.vue -->

<template>
  <div class="ai-task-list">
    <n-card title="📝 改写历史" size="large">
      <n-data-table
        :columns="columns"
        :data="store.tasks"
        :pagination="{ pageSize: 10 }"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue';
import { NTag, NButton } from 'naive-ui';
import { useRouter } from 'vue-router';
import { useAIRewriteStore } from '@/stores/ai-rewrite';

const router = useRouter();
const store = useAIRewriteStore();

interface TaskColumn {
  title: string;
  key: string;
  width?: number;
  ellipsis?: boolean;
  render?: (row: any) => any;
}

const columns: TaskColumn[] = [
  {
    title: '任务 ID',
    key: 'id',
    width: 200,
    ellipsis: true,
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row: any) => {
      const typeMap: Record<string, string> = {
        pending: 'info',
        processing: 'warning',
        completed: 'success',
        failed: 'error',
      };
      return h(NTag, { type: typeMap[row.status] }, () => row.status);
    },
  },
  {
    title: '源链接',
    key: 'sourceUrl',
    ellipsis: true,
  },
  {
    title: '改写策略',
    key: 'rewriteStrategy',
    width: 120,
  },
  {
    title: '成本',
    key: 'cost',
    width: 100,
    render: (row: any) => {
      return row.cost ? `¥${(row.cost * 7).toFixed(4)}` : '-';
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row: any) => {
      if (row.status === 'completed' && row.articleSlug) {
        return h(NButton, {
          size: 'small',
          type: 'primary',
          onClick: () => router.push(`/posts/${row.articleSlug}`),
        }, { default: () => '查看' });
      }
      return '-';
    },
  },
];
</script>

<style scoped>
.ai-task-list {
  max-width: 1200px;
  margin: 20px auto;
}
</style>
