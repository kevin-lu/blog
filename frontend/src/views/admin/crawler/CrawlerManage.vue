<template>
  <div class="crawler-manage-page">
    <div class="page-header">
      <div class="header-left">
        <h1>自动文章抓取系统</h1>
        <p>管理 RSS 抓取、AI 改写队列和定时任务</p>
      </div>
      <div class="header-actions">
        <n-button type="primary" @click="handleManualFetch">
          <template #icon>
            <n-icon :component="CloudDownloadOutline" />
          </template>
          手动抓取
        </n-button>
        <n-button @click="refreshData">
          <template #icon>
            <n-icon :component="RefreshOutline" />
          </template>
          刷新
        </n-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <n-grid :cols="4" :x-gap="16" :y-gap="16" class="stats-grid">
      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-icon rss">
            <n-icon :component="CloudDownloadOutline" size="28" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.rssSources }}</div>
            <div class="stat-label">RSS 源数量</div>
          </div>
        </n-card>
      </n-gi>

      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-icon queue">
            <n-icon :component="ListOutline" size="28" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.queuePending }}</div>
            <div class="stat-label">待处理队列</div>
          </div>
        </n-card>
      </n-gi>

      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-icon completed">
            <n-icon :component="CheckmarkCircleOutline" size="28" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.queueCompleted }}</div>
            <div class="stat-label">已完成改写</div>
          </div>
        </n-card>
      </n-gi>

      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-icon tasks">
            <n-icon :component="TimeOutline" size="28" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.scheduledTasks }}</div>
            <div class="stat-label">定时任务</div>
          </div>
        </n-card>
      </n-gi>
    </n-grid>

    <n-grid :cols="2" :x-gap="16" :y-gap="16" class="content-grid">
      <!-- RSS 源管理 -->
      <n-gi>
        <n-card title="RSS 源管理" class="full-height-card">
          <template #header-extra>
            <n-button text type="primary" size="small" @click="showRssSources = !showRssSources">
              {{ showRssSources ? '收起' : '查看全部' }}
            </n-button>
          </template>
          <n-list>
            <n-list-item v-for="source in rssSources" :key="source.name">
              <div class="source-item">
                <div class="source-info">
                  <div class="source-name">
                    {{ source.name }}
                    <n-tag v-if="source.enabled" type="success" size="small" bordered>
                      已启用
                    </n-tag>
                    <n-tag v-else type="default" size="small" bordered>
                      已禁用
                    </n-tag>
                  </div>
                  <div class="source-url">{{ source.url }}</div>
                  <div class="source-meta">
                    <span>类别：{{ source.category }}</span>
                    <span>限制：{{ source.fetch_limit }}篇/次</span>
                  </div>
                </div>
                <n-switch
                  v-model:value="source.enabled"
                  size="small"
                  @update:value="toggleSource(source)"
                />
              </div>
            </n-list-item>
          </n-list>
        </n-card>
      </n-gi>

      <!-- 定时任务状态 -->
      <n-gi>
        <n-card title="定时任务状态" class="full-height-card">
          <template #header-extra>
            <n-button text type="primary" size="small" @click="loadSchedulerJobs">
              <template #icon>
                <n-icon :component="RefreshOutline" />
              </template>
              刷新
            </n-button>
          </template>
          <n-list>
            <n-list-item v-for="job in schedulerJobs" :key="job.id">
              <div class="job-item">
                <div class="job-info">
                  <div class="job-name">
                    {{ job.name }}
                    <n-tag :type="job.enabled ? 'success' : 'default'" size="small" bordered>
                      {{ job.enabled ? '运行中' : '已停止' }}
                    </n-tag>
                  </div>
                  <div class="job-schedule">
                    下次执行：{{ formatNextRun(job.next_run) }}
                  </div>
                  <div class="job-meta">
                    <span>状态：{{ job.status }}</span>
                    <span v-if="job.last_run">上次：{{ formatLastRun(job.last_run) }}</span>
                  </div>
                </div>
                <div class="job-actions">
                  <n-button size="small" @click="triggerJob(job.id)">
                    执行
                  </n-button>
                  <n-button size="small" @click="toggleJob(job)">
                    {{ job.enabled ? '停止' : '启动' }}
                  </n-button>
                </div>
              </div>
            </n-list-item>
          </n-list>
        </n-card>
      </n-gi>
    </n-grid>

    <!-- 队列处理进度 -->
    <n-card title="AI 队列处理进度" class="queue-card">
      <template #header-extra>
        <n-alert type="info" title="提示" class="queue-tip">
          AI 改写后的文章将自动保存为草稿，可在文章管理中查看和编辑
        </n-alert>
      </template>
      <div class="queue-progress">
        <div class="progress-stats">
          <div class="progress-item">
            <div class="progress-label">待处理</div>
            <div class="progress-value pending">{{ stats.queuePending }}</div>
          </div>
          <div class="progress-item">
            <div class="progress-label">处理中</div>
            <div class="progress-value processing">{{ stats.queueProcessing }}</div>
          </div>
          <div class="progress-item">
            <div class="progress-label">已完成</div>
            <div class="progress-value completed">{{ stats.queueCompleted }}</div>
          </div>
          <div class="progress-item">
            <div class="progress-label">失败</div>
            <div class="progress-value failed">{{ stats.queueFailed }}</div>
          </div>
        </div>
        <div class="progress-actions">
          <n-button type="primary" @click="showQueueList = true">
            查看队列详情
          </n-button>
          <n-button @click="processQueue">
            手动处理队列
          </n-button>
        </div>
      </div>
    </n-card>

    <!-- 抓取历史 -->
    <n-card title="抓取历史" class="history-card">
      <template #header-extra>
        <n-button text type="primary" size="small" @click="loadCrawlerHistory">
          <template #icon>
            <n-icon :component="RefreshOutline" />
          </template>
          刷新
        </n-button>
      </template>
      <n-table :columns="historyColumns" :data="crawlerHistory" :pagination="{ pageSize: 10 }" />
    </n-card>

    <!-- 队列列表弹窗 -->
    <n-modal v-model:show="showQueueList" preset="dialog" title="AI 队列列表" class="queue-modal">
      <n-tabs type="line" animated>
        <n-tab-pane name="pending" tab="待处理">
          <queue-items-list status="pending" />
        </n-tab-pane>
        <n-tab-pane name="processing" tab="处理中">
          <queue-items-list status="processing" />
        </n-tab-pane>
        <n-tab-pane name="completed" tab="已完成">
          <queue-items-list status="completed" />
        </n-tab-pane>
        <n-tab-pane name="failed" tab="失败">
          <queue-items-list status="failed" />
        </n-tab-pane>
      </n-tabs>
    </n-modal>

    <!-- 手动抓取弹窗 -->
    <n-modal v-model:show="showManualFetch" preset="dialog" title="手动抓取文章" class="fetch-modal">
      <n-form>
        <n-form-item label="选择 RSS 源">
          <n-select
            v-model:value="fetchForm.sources"
            multiple
            :options="sourceOptions"
            placeholder="选择要抓取的源"
          />
        </n-form-item>
        <n-form-item label="抓取数量">
          <n-input-number v-model:value="fetchForm.limit" :min="1" :max="100" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-button @click="showManualFetch = false">取消</n-button>
        <n-button type="primary" @click="confirmManualFetch" :loading="fetching">
          开始抓取
        </n-button>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useMessage } from 'naive-ui'
import {
  DocumentTextOutline,
  FolderOutline,
  BookmarksOutline,
  ChatbubbleOutline,
  CloudDownloadOutline,
  RefreshOutline,
  ListOutline,
  CheckmarkCircleOutline,
  TimeOutline,
} from '@vicons/ionicons5'
import type { DataTableColumns } from 'naive-ui'
import QueueItemsList from '@/components/admin/crawler/QueueItemsList.vue'
import { crawlerApi } from '@/api/crawler'

interface Stats {
  rssSources: number
  queuePending: number
  queueProcessing: number
  queueCompleted: number
  queueFailed: number
  scheduledTasks: number
}

interface RSSSource {
  name: string
  url: string
  enabled: boolean
  fetch_limit: number
  category: string
}

interface SchedulerJob {
  id: string
  name: string
  enabled: boolean
  status: string
  next_run: string
  last_run?: string
}

interface CrawlerHistory {
  id: number
  source: string
  found: number
  new: number
  duplicates: number
  errors: number
  created_at: string
}

const message = useMessage()

// 数据
const stats = ref<Stats>({
  rssSources: 0,
  queuePending: 0,
  queueProcessing: 0,
  queueCompleted: 0,
  queueFailed: 0,
  scheduledTasks: 0,
})

const rssSources = ref<RSSSource[]>([])
const schedulerJobs = ref<SchedulerJob[]>([])
const crawlerHistory = ref<CrawlerHistory[]>([])
const showRssSources = ref(true)
const showQueueList = ref(false)
const showManualFetch = ref(false)
const fetching = ref(false)

const fetchForm = reactive({
  sources: [] as string[],
  limit: 20,
})

// 表格列定义
const historyColumns: DataTableColumns = [
  { title: '源', key: 'source' },
  { title: '发现', key: 'found' },
  { title: '新增', key: 'new' },
  { title: '重复', key: 'duplicates' },
  { title: '错误', key: 'errors' },
  {
    title: '时间',
    key: 'created_at',
    render: (row: any) => new Date(row.created_at || '').toLocaleString('zh-CN'),
  },
]

// 计算属性
const sourceOptions = computed(() => {
  return rssSources.value.map((source) => ({
    label: `${source.name} (${source.category})`,
    value: source.name,
  }))
})

// 方法
const loadStats = async () => {
  try {
    const [queueStatus, jobs] = await Promise.all([
      crawlerApi.getQueueStatus(),
      crawlerApi.getSchedulerJobs(),
    ])

    stats.value.rssSources = rssSources.value.filter((s) => s.enabled).length
    stats.value.queuePending = (queueStatus as any).pending || 0
    stats.value.queueProcessing = (queueStatus as any).processing || 0
    stats.value.queueCompleted = (queueStatus as any).completed || 0
    stats.value.queueFailed = (queueStatus as any).failed || 0
    stats.value.scheduledTasks = (jobs as any).length || 0
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

const loadRSSSources = async () => {
  try {
    const sources: any = await crawlerApi.getRSSSources()
    rssSources.value = sources as RSSSource[]
  } catch (error) {
    console.error('加载 RSS 源失败:', error)
  }
}

const loadSchedulerJobs = async () => {
  try {
    const jobs: any = await crawlerApi.getSchedulerJobs()
    schedulerJobs.value = jobs as SchedulerJob[]
  } catch (error) {
    console.error('加载定时任务失败:', error)
  }
}

const loadCrawlerHistory = async () => {
  try {
    const history: any = await crawlerApi.getCrawlerHistory()
    crawlerHistory.value = history as CrawlerHistory[]
  } catch (error) {
    console.error('加载抓取历史失败:', error)
  }
}

const refreshData = async () => {
  await Promise.all([
    loadStats(),
    loadRSSSources(),
    loadSchedulerJobs(),
    loadCrawlerHistory(),
  ])
  message.success('数据已刷新')
}

const toggleSource = async (source: RSSSource) => {
  try {
    await crawlerApi.toggleRSSSource(source.name, source.enabled)
    message.success(`${source.enabled ? '启用' : '禁用'} ${source.name} 成功`)
  } catch (error) {
    message.error('操作失败')
    source.enabled = !source.enabled
  }
}

const triggerJob = async (jobId: string) => {
  try {
    await crawlerApi.triggerSchedulerJob(jobId)
    message.success('任务已触发')
  } catch (error) {
    message.error('触发任务失败')
  }
}

const toggleJob = async (job: SchedulerJob) => {
  try {
    const newEnabled = !job.enabled
    await crawlerApi.toggleSchedulerJob(job.id, newEnabled)
    job.enabled = newEnabled
    message.success(`${newEnabled ? '启动' : '停止'}任务成功`)
  } catch (error) {
    message.error('操作失败')
  }
}

const processQueue = async () => {
  try {
    await crawlerApi.processQueue(50)
    message.success('已开始处理队列')
  } catch (error) {
    message.error('处理队列失败')
  }
}

const handleManualFetch = () => {
  showManualFetch.value = true
}

const confirmManualFetch = async () => {
  if (fetchForm.sources.length === 0) {
    message.warning('请选择 RSS 源')
    return
  }

  fetching.value = true
  try {
    await crawlerApi.manualFetch(fetchForm.sources, fetchForm.limit)
    message.success('抓取任务已启动')
    showManualFetch.value = false
    await loadStats()
  } catch (error) {
    message.error('抓取失败')
  } finally {
    fetching.value = false
  }
}

const formatNextRun = (time: string) => {
  if (!time) return '未知'
  const date = new Date(time)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  
  if (diff < 0) return '即将执行'
  if (diff < 60000) return '不到 1 分钟'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟后`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时后`
  return `${Math.floor(diff / 86400000)}天后`
}

const formatLastRun = (time: string) => {
  if (!time) return '未执行'
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

// 生命周期
onMounted(() => {
  refreshData()
})
</script>

<style scoped lang="scss">
.crawler-manage-page {
  padding: 24px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    .header-left {
      h1 {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
      }

      p {
        margin: 0;
        color: var(--n-color-text-secondary);
        font-size: 14px;
      }
    }

    .header-actions {
      display: flex;
      gap: 12px;
    }
  }

  .stats-grid {
    margin-bottom: 16px;

    .stat-card {
      display: flex;
      align-items: center;
      padding: 16px;

      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;

        &.rss {
          background: var(--info-color-supernova);
          color: var(--info-color);
        }

        &.queue {
          background: var(--warning-color-supernova);
          color: var(--warning-color);
        }

        &.completed {
          background: var(--success-color-supernova);
          color: var(--success-color);
        }

        &.tasks {
          background: var(--primary-color-supernova);
          color: var(--primary-color);
        }
      }

      .stat-content {
        flex: 1;

        .stat-value {
          font-size: 28px;
          font-weight: 600;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 13px;
          color: var(--n-color-text-secondary);
        }
      }
    }
  }

  .content-grid {
    margin-bottom: 16px;

    .full-height-card {
      height: 100%;

      :deep(.n-card__content) {
        max-height: 400px;
        overflow-y: auto;
      }
    }
  }

  .source-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;

    .source-info {
      flex: 1;

      .source-name {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        margin-bottom: 4px;
      }

      .source-url {
        font-size: 12px;
        color: var(--n-color-text-secondary);
        margin-bottom: 4px;
        word-break: break-all;
      }

      .source-meta {
        font-size: 12px;
        color: var(--n-color-text-secondary);
        display: flex;
        gap: 16px;
      }
    }
  }

  .job-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;

    .job-info {
      flex: 1;

      .job-name {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        margin-bottom: 4px;
      }

      .job-schedule {
        font-size: 12px;
        color: var(--n-color-text-secondary);
        margin-bottom: 4px;
      }

      .job-meta {
        font-size: 12px;
        color: var(--n-color-text-secondary);
        display: flex;
        gap: 16px;
      }
    }

    .job-actions {
      display: flex;
      gap: 8px;
    }
  }

  .queue-card {
    margin-bottom: 16px;
    
    .queue-tip {
      width: 400px;
      margin-right: 16px;
    }

    .queue-progress {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .progress-stats {
        display: flex;
        gap: 32px;

        .progress-item {
          text-align: center;

          .progress-label {
            font-size: 13px;
            color: var(--n-color-text-secondary);
            margin-bottom: 8px;
          }

          .progress-value {
            font-size: 32px;
            font-weight: 600;

            &.pending {
              color: var(--warning-color);
            }

            &.processing {
              color: var(--info-color);
            }

            &.completed {
              color: var(--success-color);
            }

            &.failed {
              color: var(--error-color);
            }
          }
        }
      }

      .progress-actions {
        display: flex;
        gap: 12px;
      }
    }
  }

  .history-card {
    :deep(.n-data-table) {
      font-size: 13px;
    }
  }

  .queue-modal {
    width: 800px;
  }

  .fetch-modal {
    width: 500px;
  }
}
</style>
