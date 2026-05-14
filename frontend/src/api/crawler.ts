/**
 * Crawler API
 * 自动文章抓取系统相关 API
 */
import { apiClient } from '@/utils/api'

export const crawlerApi = {
  /**
   * 获取 RSS 源列表
   */
  async getRSSSources() {
    return await apiClient.get('/crawler/sources')
  },

  /**
   * 切换 RSS 源启用状态
   */
  async toggleRSSSource(name: string, enabled: boolean) {
    return await apiClient.post(`/crawler/sources/${name}/toggle`, { enabled })
  },

  /**
   * 手动触发抓取
   */
  async manualFetch(sources: string[], limit: number) {
    return await apiClient.post('/crawler/fetch', { sources, limit })
  },

  /**
   * 获取抓取历史
   */
  async getCrawlerHistory() {
    return await apiClient.get('/crawler/history')
  },

  /**
   * 获取队列状态
   */
  async getQueueStatus() {
    return await apiClient.get('/queue/status')
  },

  /**
   * 获取队列项列表
   */
  async getQueueItems(status: string, page = 1, limit = 20) {
    return await apiClient.get('/queue/items', { params: { status, page, limit } })
  },

  /**
   * 处理队列
   */
  async processQueue(count: number) {
    return await apiClient.post('/queue/process', { count })
  },

  /**
   * 重试失败任务
   */
  async retryFailedTask(queueId: string) {
    return await apiClient.post(`/queue/retry/${queueId}`)
  },

  /**
   * 获取定时任务列表
   */
  async getSchedulerJobs() {
    return await apiClient.get('/scheduler/jobs')
  },

  /**
   * 触发定时任务
   */
  async triggerSchedulerJob(jobId: string) {
    return await apiClient.post(`/scheduler/trigger/${jobId}`)
  },

  /**
   * 切换定时任务启用状态
   */
  async toggleSchedulerJob(jobId: string, enabled: boolean) {
    return await apiClient.post(`/scheduler/toggle/${jobId}`, { enabled })
  },
}
