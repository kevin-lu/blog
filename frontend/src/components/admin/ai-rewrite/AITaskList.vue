<template>
  <n-card title="任务历史">
    <div class="task-toolbar">
      <n-button secondary @click="reloadTasks">
        刷新
      </n-button>
      <n-button tertiary @click="clearFinished">
        清理已完成任务
      </n-button>
    </div>

    <n-data-table
      :columns="columns"
      :data="store.tasks"
      :pagination="{ pageSize: 10 }"
      :bordered="false"
    />
  </n-card>
</template>

<script setup lang="ts">
import { h } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NButton, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import type { AIRewriteTask } from '@/api'
import { useAIRewriteStore } from '@/stores/ai-rewrite'
import { formatDateTime } from '@/utils/date'

const router = useRouter()
const message = useMessage()
const store = useAIRewriteStore()

const columns: DataTableColumns<AIRewriteTask> = [
  {
    title: '状态',
    key: 'status',
    width: 110,
    render(row) {
      const typeMap: Record<string, 'info' | 'warning' | 'success' | 'error'> = {
        pending: 'info',
        processing: 'warning',
        completed: 'success',
        failed: 'error',
      }
      const textMap: Record<string, string> = {
        pending: '等待处理',
        processing: '处理中',
        completed: '已完成',
        failed: '失败',
      }
      return h(NTag, { type: typeMap[row.status] || 'info', bordered: false }, {
        default: () => textMap[row.status] || row.status,
      })
    },
  },
  {
    title: '源链接',
    key: 'source_url',
    ellipsis: {
      tooltip: true,
    },
  },
  {
    title: '策略',
    key: 'rewrite_strategy',
    width: 120,
  },
  {
    title: '进度',
    key: 'progress',
    width: 90,
    render(row) {
      return `${row.progress || 0}%`
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render(row) {
      return formatDateTime(row.created_at)
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    render(row) {
      if (!row.article_slug) return '-'
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        h(NButton, {
          size: 'small',
          onClick: () => router.push(`/admin/articles/edit/${row.article_slug}`),
        }, {
          default: () => '编辑',
        }),
        row.auto_publish ? h(NButton, {
          size: 'small',
          type: 'primary',
          onClick: () => window.open(`/posts/${row.article_slug}`, '_blank'),
        }, {
          default: () => '查看',
        }) : null,
      ])
    },
  },
]

const reloadTasks = async () => {
  try {
    await store.loadTasks()
  } catch (error) {
    message.error('刷新失败')
  }
}

const clearFinished = async () => {
  try {
    await store.clearFinished()
    message.success('已清理完成任务')
  } catch (error) {
    message.error('清理失败')
  }
}
</script>

<style scoped>
.task-toolbar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-bottom: 16px;
}
</style>
