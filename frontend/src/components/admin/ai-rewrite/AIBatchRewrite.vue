<template>
  <n-card title="批量改写">
    <n-form :model="form" label-placement="top">
      <!-- 合集链接输入 -->
      <n-form-item label="微信合集链接">
        <n-input
          v-model:value="form.albumUrl"
          placeholder="https://mp.weixin.qq.com/mp/appmsgalbum?..."
          size="large"
        >
          <template #prefix>
            <n-icon :component="LinkOutline" />
          </template>
        </n-input>
        <n-button
          type="primary"
          @click="fetchAlbumArticles"
          :loading="fetching"
          :disabled="!form.albumUrl"
          size="large"
        >
          抓取文章列表
        </n-button>
      </n-form-item>

      <!-- 文章列表展示 -->
      <div v-if="articles.length > 0" class="article-list-wrp">
        <div class="article-list-header">
          <h3>找到 {{ articles.length }} 篇文章</h3>
          <n-checkbox v-model:checked="selectAll" @change="toggleSelectAll">
            全选
          </n-checkbox>
        </div>
        
        <n-list hoverable clickable style="max-height: 400px; overflow-y: auto;">
          <n-list-item
            v-for="article in articles"
            :key="article.url"
            @click="toggleArticleSelect(article)"
          >
            <template #prefix>
              <n-checkbox
                :checked="article.selected"
                @update:checked="article.selected = $event"
              />
            </template>
            <n-thing :title="article.title">
              <template #description>
                <n-tag size="small" type="info">第{{ article.index }}篇</n-tag>
              </template>
            </n-thing>
          </n-list-item>
        </n-list>

        <!-- 批量操作按钮 -->
        <div class="batch-actions">
          <n-alert
            :title="`已选择 ${selectedCount} 篇文章`"
            type="info"
            show-icon
          />
          <n-space>
            <n-select
              v-model:value="form.rewriteStrategy"
              :options="strategyOptions"
              placeholder="选择改写策略"
              size="large"
              style="width: 200px"
            />
            <n-select
              v-model:value="form.templateType"
              :options="templateOptions"
              placeholder="选择模板类型"
              size="large"
              style="width: 200px"
            />
            <n-button
              type="success"
              size="large"
              @click="submitBatchRewrite"
              :loading="submitting"
              :disabled="selectedCount === 0"
            >
              开始批量改写 (并发 2 个)
            </n-button>
          </n-space>
        </div>
      </div>
    </n-form>
  </n-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { LinkOutline } from '@vicons/ionicons5'
import { useAIRewriteStore } from '@/stores/ai-rewrite'

interface Article {
  index: number
  title: string
  url: string
  msgid: string
  selected: boolean
}

const message = useMessage()
const store = useAIRewriteStore()

const form = ref({
  albumUrl: '',
  rewriteStrategy: 'standard',
  templateType: 'tutorial',
  autoPublish: false,
})

const fetching = ref(false)
const submitting = ref(false)
const articles = ref<Article[]>([])
const selectAll = ref(false)
const selectedCount = ref(0)

const strategyOptions = [
  { label: '标准改写', value: 'standard' },
  { label: '深度改写', value: 'deep' },
  { label: '创意改写', value: 'creative' },
]

const templateOptions = [
  { label: '教程类', value: 'tutorial' },
  { label: '概念类', value: 'concept' },
  { label: '对比类', value: 'comparison' },
  { label: '实战类', value: 'practice' },
]

// 抓取合集文章
async function fetchAlbumArticles() {
  if (!form.value.albumUrl) {
    message.warning('请输入合集链接')
    return
  }

  fetching.value = true
  try {
    const response = await fetch(
      `/api/v1/articles/album/articles?url=${encodeURIComponent(form.value.albumUrl)}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    )
    const data = await response.json()
    
    if (data.success) {
      articles.value = data.data.articles.map((article: any) => ({
        ...article,
        selected: false,
      }))
      selectAll.value = false
      selectedCount.value = 0
      message.success(`找到 ${articles.value.length} 篇文章`)
    } else {
      message.error(data.error || '抓取失败')
    }
  } catch (error: any) {
    message.error('抓取失败：' + error.message)
  } finally {
    fetching.value = false
  }
}

// 全选/取消全选
function toggleSelectAll() {
  articles.value.forEach(article => {
    article.selected = selectAll.value
  })
  updateSelectedCount()
}

// 切换文章选中状态
function toggleArticleSelect(article: Article) {
  article.selected = !article.selected
  updateSelectedCount()
}

// 更新选中数量
function updateSelectedCount() {
  selectedCount.value = articles.value.filter(a => a.selected).length
}

// 提交批量改写
async function submitBatchRewrite() {
  const selectedArticles = articles.value.filter(a => a.selected)
  
  if (selectedArticles.length === 0) {
    message.warning('请至少选择一篇文章')
    return
  }

  submitting.value = true
  try {
    const response = await fetch('/api/v1/articles/ai-batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({
        sourceUrls: selectedArticles.map(a => a.url),
        rewriteStrategy: form.value.rewriteStrategy,
        templateType: form.value.templateType,
        autoPublish: false, // 保存到草稿箱
      }),
    })
    
    const data = await response.json()
    
    if (data.success) {
      message.success(`已提交 ${data.data.total} 个改写任务，并发限制：${data.data.concurrentLimit} 个`)
      // 清空列表
      articles.value = []
      form.value.albumUrl = ''
      // 刷新任务列表
      await store.loadTasks()
    } else {
      message.error(data.error || '提交失败')
    }
  } catch (error: any) {
    message.error('提交失败：' + error.message)
  } finally {
    submitting.value = false
  }
}

// 监听选中状态变化
watch(() => articles.value, () => {
  updateSelectedCount()
}, { deep: true })
</script>

<style scoped>
.article-list-wrp {
  margin-top: 24px;
}

.article-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.article-list-header h3 {
  margin: 0;
  font-size: 16px;
  color: #1a1a1a;
}

.batch-actions {
  margin-top: 24px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
}

.batch-actions .n-space {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
