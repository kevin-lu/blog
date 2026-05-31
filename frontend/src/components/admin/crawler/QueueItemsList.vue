<template>
  <div class="queue-items-list">
    <n-data-table
      :columns="columns"
      :data="items"
      :loading="loading"
      :pagination="pagination"
      @update:page="handlePageChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, h } from 'vue'
import { useMessage, type DataTableColumns } from 'naive-ui'
import { crawlerApi } from '@/api/crawler'

interface QueueItem {
  queue_id: string
  title: string
  status: string
  priority: number
  retry_count: number
  created_at: string
  completed_at?: string
  error_message?: string
}

const props = defineProps<{
  status: string
}>()

const message = useMessage()
const loading = ref(false)
const items = ref<QueueItem[]>([])
const pagination = ref({
  page: 1,
  pageSize: 10,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  itemCount: 0,
})

const columns: DataTableColumns = [
  {
    title: '标题',
    key: 'title',
    ellipsis: true,
    width: 300,
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row: any) => {
      const typeMap: Record<string, any> = {
        pending: 'warning',
        processing: 'info',
        completed: 'success',
        failed: 'error',
      }
      const labelMap: Record<string, string> = {
        pending: '待处理',
        processing: '处理中',
        completed: '已完成',
        failed: '失败',
      }
      
      // 如果是已完成，显示草稿标签
      if (row.status === 'completed' && row.article_id) {
        return h('div', { style: { display: 'flex', gap: '4px', alignItems: 'center' } }, [
          h('n-tag', { type: 'success', size: 'small' }, '已完成'),
          h('n-tag', { type: 'warning', size: 'small' }, '草稿')
        ])
      }
      
      return h('n-tag', { type: typeMap[row.status] || 'default' }, labelMap[row.status] || row.status)
    },
  },
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    render: (row: any) => {
      return h('n-tag', { size: 'small' }, row.priority?.toString() || '0')
    },
  },
  {
    title: '重试次数',
    key: 'retry_count',
    width: 80,
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 160,
    render: (row: any) => new Date(row.created_at || '').toLocaleString('zh-CN'),
  },
  {
    title: '文章',
    key: 'article_id',
    width: 120,
    render: (row: any) => {
      if (row.article_id) {
        return h('n-a', { 
          href: `/admin/articles/edit/${row.article_id}`,
          target: '_blank',
        }, '查看文章')
      }
      return h('span', { style: { color: '#999' } }, '-')
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row: any) => {
      if (row.status === 'failed') {
        return h('n-button', { size: 'small', onClick: () => handleRetry(row.queue_id) }, '重试')
      }
      return null
    },
  },
]

const loadItems = async () => {
  loading.value = true
  try {
    const result: any = await crawlerApi.getQueueItems(
      props.status,
      pagination.value.page,
      pagination.value.pageSize
    )
    items.value = result.items || []
    pagination.value.itemCount = result.total || 0
  } catch (error) {
    message.error('加载队列失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page: number) => {
  pagination.value.page = page
  loadItems()
}

const handleRetry = async (queueId: string) => {
  try {
    await crawlerApi.retryFailedTask(queueId)
    message.success('已重新加入队列')
    await loadItems()
  } catch (error) {
    message.error('重试失败')
  }
}

watch(() => props.status, loadItems)

onMounted(() => {
  loadItems()
})
</script>

<style scoped lang="scss">
.queue-items-list {
  :deep(.n-data-table) {
    font-size: 13px;
  }
}
</style>
