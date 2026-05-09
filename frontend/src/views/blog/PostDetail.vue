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
    article.value = response.article
  } catch (error) {
    console.error('Failed to load article:', error)
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
  color: #666;
}

.back-btn:hover {
  color: #18a058;
}

.post-title {
  margin: 0 0 16px 0;
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.4;
}

.post-meta {
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.publish-date {
  font-size: 14px;
  color: #999;
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

.post-body :deep(pre) {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
}

.post-body :deep(code) {
  font-family: 'Fira Code', monospace;
  font-size: 14px;
}
</style>
