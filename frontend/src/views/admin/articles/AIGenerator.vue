<template>
  <div class="ai-generator-page">
    <div class="page-header">
      <div class="header-left">
        <h1>🤖 AI 改写任务</h1>
        <p>查看和管理 AI 改写任务进度</p>
      </div>
      <div class="header-right">
        <n-space>
          <n-button type="primary" @click="loadTasks" :loading="loading">
            <template #icon>
              <n-icon :component="RefreshOutline" />
            </template>
            刷新
          </n-button>
          <n-button @click="clearCompletedTasks">
            清理已完成
          </n-button>
        </n-space>
      </div>
    </div>

    <n-space vertical size="large">
      <!-- 任务列表 -->
      <n-card>
        <template #header>
          <n-space justify="space-between" align="center">
            <span>任务列表</span>
            <n-space>
              <n-tag :type="runningTasks > 0 ? 'warning' : 'success'">
                进行中：{{ runningTasks }}
              </n-tag>
              <n-tag :type="failedTasks > 0 ? 'error' : 'success'">
                失败：{{ failedTasks }}
              </n-tag>
              <n-tag type="success">
                成功：{{ completedTasks }}
              </n-tag>
            </n-space>
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
    <n-modal v-model:show="showDetailModal" preset="card" title="任务详情" style="width: 700px;">
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
            <n-a :href="currentTask.sourceUrl" target="_blank" v-if="currentTask.sourceUrl">
              {{ currentTask.sourceUrl }}
            </n-a>
            <span v-else>无</span>
          </n-descriptions-item>
          <n-descriptions-item label="改写策略">
            {{ getStrategyText(currentTask.rewriteStrategy) }}
          </n-descriptions-item>
          <n-descriptions-item label="模板类型">
            {{ getTemplateText(currentTask.templateType) }}
          </n-descriptions-item>
          <n-descriptions-item label="创建时间" :span="2">
            {{ formatDate(currentTask.createdAt) }}
          </n-descriptions-item>
          <n-descriptions-item label="完成时间" :span="2" v-if="currentTask.completedAt">
            {{ formatDate(currentTask.completedAt) }}
          </n-descriptions-item>
          <n-descriptions-item label="Token 使用" :span="2" v-if="currentTask.tokenUsage">
            {{ currentTask.tokenUsage }}
          </n-descriptions-item>
          <n-descriptions-item label="成本" :span="2" v-if="currentTask.cost">
            ¥{{ currentTask.cost.toFixed(4) }}
          </n-descriptions-item>
        </n-descriptions>

        <!-- 错误信息 -->
        <n-alert 
          v-if="currentTask.status === 'failed' && currentTask.error" 
          type="error" 
          title="失败原因"
        >
          {{ currentTask.error }}
          <template #action>
            <n-button size="small" type="error" @click="retryTask(currentTask)">
              重试此任务
            </n-button>
          </template>
        </n-alert>

        <!-- 进度条 -->
        <n-space vertical v-if="currentTask.status === 'processing' || currentTask.status === 'pending'">
          <n-progress
            type="line"
            :percentage="currentTask.progress"
            status="default"
          />
          <n-alert type="info">
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
            <n-space v-if="currentTask.result.article.slug || currentTask.articleSlug">
              <n-button type="primary" @click="editArticle(currentTask.result.article.slug || currentTask.articleSlug)">
                编辑文章
              </n-button>
              <n-button @click="viewArticle(currentTask.result.article.slug || currentTask.articleSlug)">
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
import { ref, computed, onMounted, h } from 'vue'
import { useMessage } from 'naive-ui'
import {
  RefreshOutline,
} from '@vicons/ionicons5'
import type { DataTableColumns } from 'naive-ui'
import { NTag, NButton, NSpace, NIcon, NProgress, NA } from 'naive-ui'
import { formatDateTime } from '@/utils/date'

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
  articleId?: number
  articleSlug?: string
  error?: string
  tokenUsage?: number
  cost?: number
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

const failedTasks = computed(() => {
  return tasks.value.filter(t => t.status === 'failed').length
})

const completedTasks = computed(() => {
  return tasks.value.filter(t => t.status === 'completed').length
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
    render: (row: any) => {
      return h(NTag, {
        type: getStatusType(row.status),
      }, {
        default: () => getStatusText(row.status),
      })
    },
  },
  {
    title: '错误信息',
    key: 'error',
    width: 250,
    ellipsis: { tooltip: true },
    render: (row: any) => {
      if (row.status === 'failed' && row.error) {
        return h('span', { style: { color: '#ff4d4f' } }, row.error)
      }
      return '-'
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
    render: (row: any) => {
      return h(NProgress, {
        type: 'line',
        percentage: row.progress,
        showIndicator: false,
        style: { width: '100px' },
      })
    },
  },
  {
    title: '创建时间',
    key: 'createdAt',
    width: 180,
    render: (row: any) => formatDate(row.createdAt),
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row: any) => {
      return h(NSpace, {}, {
        default: () => [
          h(NButton, {
            size: 'small',
            onClick: () => showDetail(row),
          }, {
            default: () => '详情',
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

function getStrategyText(strategy?: string) {
  const texts: Record<string, string> = {
    standard: '标准改写',
    deep: '深度改写',
    creative: '创意改写',
  }
  return texts[strategy || 'standard'] || strategy
}

function getTemplateText(template?: string) {
  const texts: Record<string, string> = {
    tutorial: '教程风格',
    concept: '概念解析',
    comparison: '对比分析',
    practice: '实战演练',
  }
  return texts[template || 'tutorial'] || template
}

function formatDate(dateString: string) {
  return formatDateTime(dateString)
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

function clearCompletedTasks() {
  tasks.value = tasks.value.filter(t => t.status === 'pending' || t.status === 'processing')
  message.success('已清理已完成任务')
}

function showDetail(task: AITask) {
  currentTask.value = task
  showDetailModal.value = true
}

async function retryTask(task: AITask) {
  if (!task.sourceUrl) {
    message.error('任务没有源 URL，无法重试')
    return
  }

  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch('/api/admin/articles/ai-rewrite', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        sourceUrl: task.sourceUrl,
        rewriteStrategy: task.rewriteStrategy,
        templateType: task.templateType,
      }),
    })

    const result = await response.json()

    if (result.success) {
      message.success('重试任务已创建')
      showDetailModal.value = false
      loadTasks()
    } else {
      message.error(result.message || '重试失败')
    }
  } catch (error) {
    message.error('重试失败')
  }
}

function editArticle(slug?: string) {
  if (!slug) return
  window.open(`/admin/articles/edit/${slug}`, '_blank')
}

function viewArticle(slug?: string) {
  if (!slug) return
  window.open(`/posts/${slug}`, '_blank')
}

onMounted(() => {
  loadTasks()
  // 每 5 秒自动刷新一次
  const interval = setInterval(loadTasks, 5000)
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
