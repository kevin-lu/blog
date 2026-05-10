<template>
  <div class="ai-generator-page">
    <div class="page-header">
      <div class="header-left">
        <h1>🤖 AI 改写任务</h1>
        <p>查看和管理 AI 改写任务进度</p>
      </div>
      <div class="header-right">
        <n-button type="primary" @click="loadTasks" :loading="loading">
          <template #icon>
            <n-icon :component="RefreshOutline" />
          </template>
          刷新
        </n-button>
      </div>
    </div>

    <n-space vertical size="large">
      <!-- 任务列表 -->
      <n-card>
        <template #header>
          <n-space justify="space-between" align="center">
            <span>任务列表</span>
            <n-tag :type="runningTasks > 0 ? 'warning' : 'success'">
              进行中：{{ runningTasks }}
            </n-tag>
          </n-space>
        </template>

        <n-data-table
          :columns="columns"
          :data="tasks"
          :loading="loading"
          :pagination="false"
          striped
        />
      </n-card>
    </n-space>

    <!-- 任务详情弹窗 -->
    <n-modal v-model:show="showDetailModal" preset="card" title="任务详情" style="width: 600px;">
      <n-space vertical v-if="currentTask">
        <n-descriptions bordered :column="2">
          <n-descriptions-item label="任务 ID">
            {{ currentTask.id }}
          </n-descriptions-item>
          <n-descriptions-item label="状态">
            <n-tag :type="getStatusType(currentTask.status)">
              {{ getStatusText(currentTask.status) }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="源 URL" :span="2">
            {{ currentTask.sourceUrl || '无' }}
          </n-descriptions-item>
          <n-descriptions-item label="改写策略">
            {{ currentTask.rewriteStrategy || 'standard' }}
          </n-descriptions-item>
          <n-descriptions-item label="模板类型">
            {{ currentTask.templateType || 'tutorial' }}
          </n-descriptions-item>
          <n-descriptions-item label="创建时间" :span="2">
            {{ formatDate(currentTask.createdAt) }}
          </n-descriptions-item>
          <n-descriptions-item label="完成时间" :span="2" v-if="currentTask.completedAt">
            {{ formatDate(currentTask.completedAt) }}
          </n-descriptions-item>
        </n-descriptions>

        <!-- 进度条 -->
        <n-space vertical>
          <n-progress
            type="line"
            :percentage="currentTask.progress"
            :status="currentTask.status === 'failed' ? 'error' : currentTask.status === 'completed' ? 'success' : 'default'"
          />
          <n-alert :type="currentTask.status === 'failed' ? 'error' : 'info'">
            {{ currentTask.message || '任务执行中...' }}
          </n-alert>
        </n-space>

        <!-- 生成的文章 -->
        <n-card v-if="currentTask.result?.article" title="生成的文章" size="small">
          <n-space vertical>
            <n-input
              v-model:value="currentTask.result.article.title"
              placeholder="标题"
              readonly
            />
            <n-input
              v-model:value="currentTask.result.article.content"
              type="textarea"
              placeholder="内容"
              readonly
              :rows="10"
            />
            <n-space v-if="currentTask.result.article.id">
              <n-button type="primary" @click="editArticle(currentTask.result.article.id)">
                编辑文章
              </n-button>
              <n-button @click="viewArticle(currentTask.result.article.id)">
                查看文章
              </n-button>
            </n-space>
          </n-space>
        </n-card>
      </n-space>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  RefreshOutline,
} from '@vicons/ionicons5'
import type { DataTableColumns } from 'naive-ui'
import { NTag, NButton, NSpace, NIcon } from 'naive-ui'

const message = useMessage()

interface AITask {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  sourceUrl?: string
  rewriteStrategy?: string
  templateType?: string
  progress: number
  message?: string
  result?: {
    article?: {
      id?: number
      title?: string
      content?: string
      slug?: string
    }
  }
  createdAt: string
  completedAt?: string
}

const loading = ref(false)
const tasks = ref<AITask[]>([])
const showDetailModal = ref(false)
const currentTask = ref<AITask | null>(null)

const runningTasks = computed(() => {
  return tasks.value.filter(t => t.status === 'pending' || t.status === 'processing').length
})

const columns: DataTableColumns = [
  {
    title: '任务 ID',
    key: 'id',
    width: 100,
    ellipsis: { tooltip: true },
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => {
      return h(NTag, {
        type: getStatusType(row.status),
        children: () => getStatusText(row.status),
      })
    },
  },
  {
    title: '源 URL',
    key: 'sourceUrl',
    width: 200,
    ellipsis: { tooltip: true },
  },
  {
    title: '改写策略',
    key: 'rewriteStrategy',
    width: 100,
  },
  {
    title: '进度',
    key: 'progress',
    width: 150,
    render: (row) => {
      return h('div', { style: { width: '100px' } }, [
        h((window as any).$naiveUI.NProgress, {
          type: 'line',
          percentage: row.progress,
          showIndicator: false,
          style: { width: '100%' },
        }),
      ])
    },
  },
  {
    title: '创建时间',
    key: 'createdAt',
    width: 180,
    render: (row) => formatDate(row.createdAt),
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row) => {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, {
            size: 'small',
            onClick: () => showDetail(row),
            children: () => '详情',
          }),
        ],
      })
    },
  },
]

function getStatusType(status: string) {
  const types: Record<string, 'default' | 'warning' | 'success' | 'error'> = {
    pending: 'warning',
    processing: 'warning',
    completed: 'success',
    failed: 'error',
  }
  return types[status] || 'default'
}

function getStatusText(status: string) {
  const texts: Record<string, string> = {
    pending: '等待中',
    processing: '执行中',
    completed: '已完成',
    failed: '失败',
  }
  return texts[status] || status
}

function formatDate(dateString: string) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

async function loadTasks() {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch('/api/admin/articles/ai-progress', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })
    
    const result = await response.json()
    
    if (result.success) {
      tasks.value = result.data.tasks || []
    } else {
      message.error(result.message || '加载任务列表失败')
    }
  } catch (error) {
    message.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

function showDetail(task: AITask) {
  currentTask.value = task
  showDetailModal.value = true
}

function editArticle(id: number) {
  window.open(`/admin/articles/edit/${id}`, '_blank')
}

function viewArticle(id: number) {
  window.open(`/posts/${id}`, '_blank')
}

onMounted(() => {
  loadTasks()
  // 每 5 秒自动刷新一次
  const interval = setInterval(loadTasks, 5000)
  // 组件卸载时清除定时器
  return () => clearInterval(interval)
})
</script>

<style scoped>
.ai-generator-page {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.header-left p {
  margin: 0;
  color: #666;
  font-size: 14px;
}
</style>
