<template>
  <div class="article-list-item" @click="goToArticle">
    <div class="article-id">{{ article.id }}</div>
    <div class="article-dot"></div>
    <div class="article-info">
      <h2 class="article-title">{{ article.title }}</h2>
      <p v-if="article.description" class="article-description">
        {{ article.description }}
      </p>
      <div class="article-meta">
        <n-text depth="3" class="publish-date">
          {{ formatDate(article.published_at) }}
        </n-text>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Article } from '@/types'

interface Props {
  article: Article
}

const props = defineProps<Props>()
const router = useRouter()

const goToArticle = () => {
  router.push(`/posts/${props.article.slug}`)
}

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
</script>

<style scoped>
.article-list-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.article-list-item:hover {
  background-color: #f9f9f9;
}

.article-id {
  font-size: 14px;
  color: #999;
  min-width: 32px;
  text-align: right;
}

.article-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #ddd;
  margin-top: 8px;
  flex-shrink: 0;
}

.article-info {
  flex: 1;
  min-width: 0;
}

.article-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
}

.article-description {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  gap: 12px;
}

.publish-date {
  font-size: 13px;
  color: #999;
}
</style>
