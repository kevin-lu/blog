import { defineStore } from 'pinia'
import { ref } from 'vue'
import { aiRewriteApi, type AIRewritePayload, type AIRewriteTask } from '@/api'

const POLL_INTERVAL = 3000

export const useAIRewriteStore = defineStore('ai-rewrite', () => {
  const tasks = ref<AIRewriteTask[]>([])
  const currentTask = ref<AIRewriteTask | null>(null)
  const isLoading = ref(false)
  let pollTimer: number | null = null

  const stopPolling = () => {
    if (pollTimer !== null) {
      window.clearTimeout(pollTimer)
      pollTimer = null
    }
  }

  const syncCurrentTaskFromList = () => {
    const activeTask = tasks.value.find((task) => task.status === 'processing' || task.status === 'pending')
    if (!currentTask.value || currentTask.value.status === 'completed' || currentTask.value.status === 'failed') {
      currentTask.value = activeTask || currentTask.value
    }
  }

  const loadTasks = async () => {
    const response = await aiRewriteApi.getTasks()
    tasks.value = response.tasks || []
    syncCurrentTaskFromList()
  }

  const fetchTask = async (taskId: string) => {
    const response = await aiRewriteApi.getTask(taskId)
    currentTask.value = response.task

    const taskIndex = tasks.value.findIndex((task) => task.id === response.task.id)
    if (taskIndex >= 0) {
      tasks.value.splice(taskIndex, 1, response.task)
    } else {
      tasks.value.unshift(response.task)
    }

    if (response.task.status === 'completed' || response.task.status === 'failed') {
      stopPolling()
      await loadTasks()
      return
    }

    pollTimer = window.setTimeout(() => {
      fetchTask(taskId)
    }, POLL_INTERVAL)
  }

  const submitRewrite = async (data: AIRewritePayload) => {
    isLoading.value = true
    try {
      const response = await aiRewriteApi.submit(data)
      currentTask.value = response.task
      await loadTasks()
      stopPolling()
      await fetchTask(response.task.id)
      return response.task
    } finally {
      isLoading.value = false
    }
  }

  const clearFinished = async () => {
    await aiRewriteApi.clearFinished()
    tasks.value = tasks.value.filter((task) => task.status === 'processing' || task.status === 'pending')
    if (currentTask.value && (currentTask.value.status === 'completed' || currentTask.value.status === 'failed')) {
      currentTask.value = tasks.value[0] || null
    }
  }

  return {
    tasks,
    currentTask,
    isLoading,
    submitRewrite,
    loadTasks,
    fetchTask,
    clearFinished,
    stopPolling,
  }
})
