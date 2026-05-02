<template>
  <div class="max-w-4xl mx-auto px-6 py-8">
    <article v-if="article">
      <!-- 返回链接 -->
      <NuxtLink to="/" class="inline-flex items-center gap-1 text-gray-400 hover:text-gray-600 mb-6 transition-colors">
        <span>←</span>
        <span>返回首页</span>
      </NuxtLink>

      <!-- 编号和标题 -->
      <header class="mb-8">
        <div class="text-sm text-gray-300 mb-2">No.{{ article.order || 0 }}</div>
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4 leading-tight">
          {{ article.title }}
        </h1>

        <!-- 元信息 -->
        <div class="flex flex-wrap items-center gap-4 text-sm text-gray-400">
          <time :datetime="article.publishedAt">
            {{ formatDate(article.publishedAt) }}
          </time>
          <span v-if="article.category" class="text-gray-500">
            {{ article.category.title }}
          </span>
          <span v-if="article.readingTime">
            {{ article.readingTime }} 分钟阅读
          </span>
        </div>
      </header>

      <!-- 封面图 -->
      <SanityImage
        v-if="article.coverImage"
        :asset-id="article.coverImage.asset._ref"
        class="w-full aspect-video object-cover rounded-xl mb-8"
        :alt="article.title"
      />

      <!-- 正文内容 -->
      <div class="prose prose-gray max-w-none">
        <ArticleContent :content="article.content" />
      </div>

      <!-- 底部导航 -->
      <nav class="mt-12 pt-6 border-t border-gray-200">
        <NuxtLink to="/" class="inline-flex items-center gap-1 text-gray-400 hover:text-gray-600 transition-colors">
          <span>←</span>
          <span>返回首页</span>
        </NuxtLink>
      </nav>
    </article>

    <!-- 404 -->
    <div v-else class="text-center py-20">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">404</h1>
      <p class="text-gray-400 mb-6">文章未找到</p>
      <NuxtLink to="/" class="text-accent hover:underline">
        ← 返回首页
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDate } from '~/utils/helpers'

const route = useRoute()
const { fetchArticleBySlug } = useSanity()

const slug = route.params.slug as string

const { data: article } = await useAsyncData(`article-${slug}`, () => fetchArticleBySlug(slug))

// SEO
useHead(() => {
  if (!article.value) return {}
  
  return {
    title: `${article.value.title} - 我的博客`,
    meta: [
      {
        name: 'description',
        content: article.value.excerpt || ''
      }
    ]
  }
})
</script>