<template>
  <div class="comment-manage-page">
    <div class="page-header">
      <div class="header-left">
        <h1>评论管理</h1>
        <p>管理用户评论</p>
      </div>
    </div>

    <n-card>
      <!-- Filters -->
      <div class="filters">
        <n-space>
          <n-select
            v-model:value="filters.status"
            :options="statusOptions"
            placeholder="状态"
            clearable
            style="width: 120px"
            @update:value="handleFilterChange"
          />
        </n-space>
      </div>

      <n-data-table
        :columns="columns"
        :data="comments"
        :loading="loading"
        :pagination="pagination"
        :row-key="rowKey"
      />
    </n-card>

    <!-- Delete Dialog -->
    <n-modal
      v-model:show="showDeleteModal"
      preset="dialog"
      title="删除评论"
      content="确定要删除该评论吗？此操作不可恢复。"
      positive-text="确定"
      negative-text="取消"
      @positive-click="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted } from 'vue'
import { useMessage, NButton, NTag, NIcon } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { CheckmarkOutline, CloseOutline, TrashOutline } from '@vicons/ionicons5'
import type { Comment } from '@/types'
import { commentApi } from '@/api'

const message = useMessage()

const loading = ref(false)
const comments = ref<Comment[]>([])
const showDeleteModal = ref(false)
const deleteComment = ref<Comment | null>(null)

const filters = reactive({
  status: '',
})

const statusOptions = [
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
]

const pagination = reactive({
  page: 1,
  pageSize: 20,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page: number) => {
    pagination.page = page
    loadComments()
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    loadComments()
  },
})

const rowKey = (row: Comment) => row.id

const columns: DataTableColumns = [
  {
    title: 'ID',
    key: 'id',
    width: 60,
  },
  {
    title: '评论者',
    key: 'github_id',
    width: 150,
    render(row) {
      return h('div', [
        h('div', { style: 'font-weight: 500;' }, row.github_id || '未记录'),
        h('div', { style: 'font-size: 12px; color: #999;' }, `ID: ${row.id}`),
      ])
    },
  },
  {
    title: '文章',
    key: 'article_slug',
    ellipsis: {
      tooltip: true,
    },
    width: 240,
    render(row) {
      return h('span', { style: 'font-size: 13px;' }, row.article_slug || '未关联文章')
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render(row) {
      const typeMap: any = {
        pending: 'warning',
        approved: 'success',
        rejected: 'error',
      }
      const labelMap: any = {
        pending: '待审核',
        approved: '已通过',
        rejected: '已拒绝',
      }
      return h(NTag, {
        type: typeMap[row.status] || 'default',
        bordered: false,
        size: 'small',
      }, {
        default: () => labelMap[row.status] || row.status,
      })
    },
  },
  {
    title: '置顶',
    key: 'is_pinned',
    width: 90,
    render(row) {
      return row.is_pinned
        ? h(NTag, {
            type: 'info',
            bordered: false,
            size: 'small',
          }, {
            default: () => '已置顶',
          })
        : h('span', { style: 'font-size: 13px; color: #999;' }, '否')
    },
  },
  {
    title: '时间',
    key: 'created_at',
    width: 160,
    render(row) {
      return h(
        'span',
        { style: 'font-size: 13px; color: #666;' },
        row.created_at ? new Date(row.created_at).toLocaleString('zh-CN') : '-'
      )
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 220,
    fixed: 'right',
    render(row) {
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        row.status === 'pending' ? h(NButton, {
          size: 'small',
          type: 'success',
          onClick: () => handleApprove(row),
        }, {
          default: () => '通过',
          icon: () => h(NIcon, { component: CheckmarkOutline }),
        }) : null,
        row.status === 'pending' ? h(NButton, {
          size: 'small',
          type: 'warning',
          onClick: () => handleReject(row),
        }, {
          default: () => '拒绝',
          icon: () => h(NIcon, { component: CloseOutline }),
        }) : null,
        h(NButton, {
          size: 'small',
          type: 'error',
          onClick: () => handleDelete(row),
        }, {
          default: () => '删除',
          icon: () => h(NIcon, { component: TrashOutline }),
        }),
      ])
    },
  },
]

const handleApprove = async (comment: any) => {
  try {
    await commentApi.approve(comment.id)
    message.success('已通过')
    loadComments()
  } catch (error) {
    message.error('操作失败')
  }
}

const handleReject = async (comment: Comment) => {
  try {
    await commentApi.reject(comment.id)
    message.success('已拒绝')
    loadComments()
  } catch (error) {
    message.error('操作失败')
  }
}

const handleDelete = (comment: Comment) => {
  deleteComment.value = comment
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  if (!deleteComment.value) return

  try {
    await commentApi.delete(deleteComment.value.id)
    message.success('删除成功')
    loadComments()
  } catch (error) {
    message.error('删除失败')
  } finally {
    showDeleteModal.value = false
    deleteComment.value = null
  }
}

const loadComments = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      limit: pagination.pageSize,
    }
    if (filters.status) params.status = filters.status

    const response = await commentApi.getList(params)
    comments.value = response.comments || []
    pagination.page = response.page || 1
    pagination.pageSize = response.limit || pagination.pageSize
    pagination.itemCount = response.total || 0
  } catch (error) {
    message.error('加载评论失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  pagination.page = 1
  loadComments()
}

onMounted(() => {
  loadComments()
})
</script>

<style scoped>
.comment-manage-page {
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

.filters {
  margin-bottom: 20px;
}
</style>
