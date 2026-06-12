<template>
  <div class="article-stats-page">
    <div class="page-header">
      <div class="header-left">
        <n-button text @click="goBack">
          <template #icon>
            <n-icon :component="ArrowBackOutline" />
          </template>
        </n-button>
        <div class="title-section">
          <h1>文章统计</h1>
          <p v-if="articleTitle">{{ articleTitle }}</p>
        </div>
      </div>
    </div>

    <n-grid :cols="24" :x-gap="16" :y-gap="16">
      <!-- Summary Cards -->
      <n-grid-item :span="6">
        <n-card>
          <n-statistic label="总 PV">
            <template #prefix>
              <n-icon :component="DocumentTextOutline" />
            </template>
            {{ stats.total_pv || 0 }}
          </n-statistic>
        </n-card>
      </n-grid-item>

      <n-grid-item :span="6">
        <n-card>
          <n-statistic label="总 UV">
            <template #prefix>
              <n-icon :component="PeopleOutline" />
            </template>
            {{ stats.total_uv || 0 }}
          </n-statistic>
        </n-card>
      </n-grid-item>

      <n-grid-item :span="6">
        <n-card>
          <n-statistic label="首次访问">
            <template #prefix>
              <n-icon :component="TimeOutline" />
            </template>
            {{ stats.first_visit ? formatDate(stats.first_visit) : '-' }}
          </n-statistic>
        </n-card>
      </n-grid-item>

      <n-grid-item :span="6">
        <n-card>
          <n-statistic label="最近访问">
            <template #prefix>
              <n-icon :component="TimeOutline" />
            </template>
            {{ stats.last_visit ? formatDate(stats.last_visit) : '-' }}
          </n-statistic>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- Trend Chart -->
    <n-card title="访问趋势" style="margin-top: 16px">
      <template #header-extra>
        <n-select
          v-model:value="selectedPeriod"
          :options="periodOptions"
          size="small"
          style="width: 120px"
          @update:value="loadStats"
        />
      </template>
      <div ref="chartRef" style="height: 300px"></div>
    </n-card>

    <!-- Visits List -->
    <n-card title="访问记录" style="margin-top: 16px">
      <template #header-extra>
        <n-space>
          <n-date-picker
            v-model:value="dateRange"
            type="daterange"
            placeholder="选择日期范围"
            size="small"
            style="width: 240px"
            @update:value="loadVisits"
          />
          <n-input
            v-model:value="ipFilter"
            placeholder="筛选 IP 地址"
            clearable
            size="small"
            style="width: 180px"
            @keyup.enter="loadVisits"
          >
            <template #prefix>
              <n-icon :component="SearchOutline" />
            </template>
          </n-input>
          <n-button size="small" @click="loadVisits">
            筛选
          </n-button>
        </n-space>
      </template>

      <n-data-table
        :columns="columns"
        :data="visits"
        :loading="loadingVisits"
        :pagination="pagination"
        :bordered="false"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage, NIcon } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import {
  ArrowBackOutline,
  DocumentTextOutline,
  PeopleOutline,
  TimeOutline,
  SearchOutline,
} from '@vicons/ionicons5'
import { articleStatsApi } from '@/api'
import type { ArticleStats, ArticleVisit } from '@/types/article_stats'
import { formatDateTime } from '@/utils/date'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

const router = useRouter()
const route = useRoute()
const message = useMessage()

const articleId = ref<number>(Number(route.params.id))
const articleTitle = ref<string>('')

const loading = ref(false)
const loadingVisits = ref(false)

const stats = ref<ArticleStats>({
  total_pv: 0,
  total_uv: 0,
  trend: [],
})

const selectedPeriod = ref<'daily' | 'weekly' | 'monthly'>('daily')
const periodOptions = [
  { label: '按天', value: 'daily' },
  { label: '按周', value: 'weekly' },
  { label: '按月', value: 'monthly' },
]

const dateRange = ref<[number, number] | null>(null)
const ipFilter = ref<string>('')

const visits = ref<ArticleVisit[]>([])

const pagination = reactive({
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page: number) => {
    pagination.page = page
    loadVisits()
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    loadVisits()
  },
})

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const columns: DataTableColumns = [
  {
    title: 'ID',
    key: 'id',
    width: 80,
  },
  {
    title: 'IP 地址',
    key: 'ip_address',
    width: 140,
  },
  {
    title: 'User-Agent',
    key: 'user_agent',
    ellipsis: {
      tooltip: true,
    },
  },
  {
    title: '访问时间',
    key: 'visited_at',
    width: 180,
    render(row) {
      return formatDateTime(row.visited_at)
    },
  },
]

const goBack = () => {
  router.back()
}

const formatDate = (dateString: string) => {
  return formatDateTime(dateString)
}

const loadStats = async () => {
  try {
    loading.value = true
    const data = await articleStatsApi.getAdminStats(articleId.value, {
      period: selectedPeriod.value,
      days: selectedPeriod.value === 'daily' ? 30 : selectedPeriod.value === 'weekly' ? 12 : 12,
    })
    stats.value = data
    articleTitle.value = data.title || ''
    renderChart()
  } catch (error: any) {
    console.error('Load stats failed:', error)
    message.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

const loadVisits = async () => {
  try {
    loadingVisits.value = true
    const params: any = {
      page: pagination.page,
      limit: pagination.pageSize,
    }
    
    if (dateRange.value) {
      params.start_date = new Date(dateRange.value[0]).toISOString()
      params.end_date = new Date(dateRange.value[1]).toISOString()
    }
    
    if (ipFilter.value) {
      params.ip_address = ipFilter.value
    }

    const data = await articleStatsApi.getAdminVisits(articleId.value, params)
    visits.value = data.visits
    pagination.page = data.page
    pagination.pageSize = data.limit
  } catch (error: any) {
    console.error('Load visits failed:', error)
    message.error('加载访问记录失败')
  } finally {
    loadingVisits.value = false
  }
}

const renderChart = () => {
  if (!chartRef.value) return
  
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const trendData = stats.value.trend || []
  const dates = trendData.map(item => item.date)
  const pvData = trendData.map(item => item.pv)
  const uvData = trendData.map(item => item.uv)

  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['PV', 'UV'],
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: 'PV',
        type: 'line',
        data: pvData,
        smooth: true,
        itemStyle: {
          color: '#18a058',
        },
      },
      {
        name: 'UV',
        type: 'line',
        data: uvData,
        smooth: true,
        itemStyle: {
          color: '#2080f0',
        },
      },
    ],
  }

  chart.setOption(option)
  
  window.addEventListener('resize', () => {
    chart?.resize()
  })
}

onMounted(() => {
  loadStats()
  loadVisits()
})
</script>

<style scoped lang="scss">
.article-stats-page {
  padding: 24px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    
    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
      
      .title-section {
        h1 {
          margin: 0;
          font-size: 24px;
          font-weight: 600;
        }
        
        p {
          margin: 4px 0 0 0;
          font-size: 14px;
          color: #666;
        }
      }
    }
  }
}
</style>
