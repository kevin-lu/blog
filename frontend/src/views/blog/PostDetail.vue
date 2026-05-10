<template>
  <div class="post-detail">
    <div v-if="loading" class="loading">
      <n-spin size="large" description="加载中..." />
    </div>

    <div v-else-if="!article" class="not-found">
      <n-empty description="文章未找到" size="large" />
      <n-button type="primary" @click="router.push('/')">
        返回首页
      </n-button>
    </div>

    <div v-else>
      <!-- Article Header -->
      <div class="post-header">
        <n-button text @click="router.push('/')" class="back-btn">
          <template #icon>
            <n-icon :component="ArrowBackOutline" />
          </template>
          返回首页
        </n-button>
      </div>

      <article class="post-content">
        <h1 class="post-title">{{ article.title }}</h1>
        
        <div class="post-meta">
          <n-text depth="3" class="publish-date">
            {{ formatDate(article.published_at) }}
          </n-text>
        </div>

        <div class="post-body" v-html="article.content"></div>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowBackOutline } from '@vicons/ionicons5'
import type { Article } from '@/types'
import { articleApi } from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const article = ref<Article | null>(null)

const formatDate = (dateString: string | null) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return ''
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const loadArticle = async () => {
  loading.value = true
  try {
    const response = await articleApi.getDetail(route.params.slug as string)
    if (response.success && response.data) {
      article.value = response.data
    } else {
      article.value = null
    }
  } catch (error) {
    console.error('Failed to load article:', error)
    article.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadArticle()
})
</script>

<style scoped>
.post-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
}

.loading,
.not-found {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  gap: 24px;
}

.post-header {
  margin-bottom: 40px;
}

.back-btn {
  font-size: 14px;
  color: #18a058;
  transition: all 0.2s;
}

.back-btn:hover {
  color: #0c7a43;
  background: rgba(24, 160, 88, 0.08);
}

.post-title {
  margin: 0 0 16px 0;
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #1a1a1a 0%, #333 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.4;
}

.post-meta {
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(24, 160, 88, 0.1);
}

.publish-date {
  font-size: 14px;
  color: #18a058;
}

.post-body {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
}

.post-body :deep(p) {
  margin-bottom: 1.5em;
}

.post-body :deep(h1),
.post-body :deep(h2),
.post-body :deep(h3) {
  margin-top: 2em;
  margin-bottom: 1em;
  font-weight: 600;
}

.post-body :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 16px 0;
}

/* 代码块样式 */
.post-body :deep(pre) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-left: 4px solid #18a058;
  border-radius: 8px;
  padding: 16px 20px;
  margin: 20px 0;
  overflow-x: auto;
  box-shadow: 0 2px 8px rgba(24, 160, 88, 0.1);
}

.post-body :deep(code) {
  font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

/* 引用块样式 */
.post-body :deep(blockquote) {
  background: rgba(24, 160, 88, 0.05);
  border-left: 4px solid #18a058;
  padding: 16px 20px;
  margin: 20px 0;
  color: #555;
  font-style: italic;
  border-radius: 0 8px 8px 0;
}

/* 标题样式 */
.post-body :deep(h2) {
  font-size: 24px;
  font-weight: 700;
  color: #18a058;
  margin: 40px 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(24, 160, 88, 0.2);
}

.post-body :deep(h3) {
  font-size: 20px;
  font-weight: 600;
  color: #0c7a43;
  margin: 30px 0 15px 0;
}

/* 表格样式 */
.post-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(24, 160, 88, 0.1);
}

.post-body :deep(th) {
  background: linear-gradient(135deg, #18a058 0%, #0c7a43 100%);
  color: white;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
}

.post-body :deep(td) {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.post-body :deep(tr:nth-child(even)) {
  background: rgba(24, 160, 88, 0.02);
}

.post-body :deep(tr:hover) {
  background: rgba(24, 160, 88, 0.05);
}

/* 列表样式 */
.post-body :deep(ul),
.post-body :deep(ol) {
  padding-left: 24px;
  margin: 16px 0;
}

.post-body :deep(li) {
  margin: 8px 0;
  line-height: 1.8;
}

/* 重点内容加粗 */
.post-body :deep(strong),
.post-body :deep(b) {
  color: #18a058;
  font-weight: 600;
}
</style>
