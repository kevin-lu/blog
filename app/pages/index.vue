<template>
  <div class="max-w-4xl mx-auto px-6 py-8">
    <!-- 博客标题 -->
    <header class="mb-10">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">
        {{ siteSettings?.title || '我的博客' }}
      </h1>
      <p class="text-gray-500">
        {{ siteSettings?.bio || '分享技术、探索创新、启迪思想' }}
      </p>
    </header>

    <!-- 文章统计 -->
    <div class="mb-8 pb-6 border-b border-gray-200">
      <span class="text-gray-400">全部文章</span>
      <span class="ml-2 text-2xl font-bold text-gray-900">{{ articles?.length || 0 }} 篇</span>
    </div>

    <!-- 编号文章列表 -->
    <ul class="space-y-1">
      <li v-if="pending" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
      </li>
      
      <li v-else-if="!articles?.length" class="text-center py-12 text-gray-400">
        暂无文章
      </li>

      <li v-else v-for="article in articles" :key="article._id">
        <NuxtLink
          :to="`/posts/${article.slug.current}`"
          class="flex items-start gap-4 py-3 px-3 -mx-3 rounded-lg hover:bg-gray-50 transition-colors group"
        >
          <!-- 编号 -->
          <span class="flex-shrink-0 w-10 text-sm text-gray-300 group-hover:text-gray-400">
            {{ article.order || 0 }}
          </span>
          
          <!-- 标题 -->
          <span class="text-gray-700 group-hover:text-accent transition-colors">
            {{ article.title }}
          </span>
          
          <!-- 箭头 -->
          <span class="text-gray-300 group-hover:text-accent">›</span>
        </NuxtLink>
      </li>
    </ul>

    <!-- 加载更多 -->
    <div v-if="hasMore" class="text-center pt-8">
      <button
        @click="loadMore"
        class="px-6 py-2.5 text-sm font-medium text-gray-500 bg-gray-50 border border-gray-200 rounded-lg hover:border-gray-300 hover:text-gray-700 transition-all"
        :disabled="loadingMore"
      >
        <span v-if="loadingMore">加载中...</span>
        <span v-else>加载更多</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ArticleListItem } from '~/types'

const { fetchArticles, fetchSiteSettings } = useSanity()

// 获取站点设置
const { data: siteSettings } = await useAsyncData('siteSettings', () => fetchSiteSettings())

// 获取文章列表
const pageSize = 50
const page = ref(1)
const articles = ref<ArticleListItem[]>([])
const hasMore = ref(true)
const loadingMore = ref(false)

const { data: initialArticles, pending } = await useAsyncData('articles', () => fetchArticles(pageSize, 0))

if (initialArticles.value) {
  articles.value = initialArticles.value
  hasMore.value = initialArticles.value.length === pageSize
}

// 加载更多
async function loadMore() {
  if (loadingMore.value) return
  
  loadingMore.value = true
  const start = page.value * pageSize
  
  try {
    const newArticles = await fetchArticles(pageSize, start)
    if (newArticles.length) {
      articles.value.push(...newArticles)
      page.value++
    }
    hasMore.value = newArticles.length === pageSize
  } catch (e) {
    console.error('Failed to load more articles:', e)
  } finally {
    loadingMore.value = false
  }
}

// SEO
useHead({
  title: siteSettings.value?.title || '我的博客',
  meta: [
    {
      name: 'description',
      content: siteSettings.value?.description || '一个基于 Nuxt.js 和 Sanity 构建的技术博客'
    }
  ]
})
</script>