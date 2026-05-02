<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <article v-if="article">
      <!-- Header -->
      <header class="mb-8">
        <!-- Category -->
        <NuxtLink
          :to="`/categories/${article.category.slug.current}`"
          class="inline-block text-sm font-medium text-accent mb-3 hover:underline"
        >
          {{ article.category.title }}
        </NuxtLink>

        <!-- Title -->
        <h1 class="text-3xl md:text-4xl font-bold text-text mb-4 leading-tight">
          {{ article.title }}
        </h1>

        <!-- Meta -->
        <div class="flex flex-wrap items-center gap-4 text-sm text-text-muted">
          <time :datetime="article.publishedAt">
            {{ formatDate(article.publishedAt) }}
          </time>
          <span v-if="article.readingTime" class="flex items-center gap-1">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            {{ article.readingTime }} 分钟阅读
          </span>
          <span v-if="article.updatedAt" class="text-text-light">
            更新于 {{ formatDate(article.updatedAt) }}
          </span>
        </div>

        <!-- Tags -->
        <div v-if="article.tags?.length" class="flex flex-wrap gap-2 mt-4">
          <NuxtLink
            v-for="tag in article.tags"
            :key="tag._id"
            :to="`/tags/${tag.slug.current}`"
            class="text-xs px-3 py-1 bg-accent-light text-accent rounded-full hover:bg-accent hover:text-white transition-colors"
          >
            {{ tag.title }}
          </NuxtLink>
        </div>
      </header>

      <!-- Cover Image -->
      <SanityImage
        v-if="article.coverImage"
        :asset-id="article.coverImage.asset._ref"
        class="w-full aspect-video object-cover rounded-xl mb-8"
        :alt="article.title"
      />

      <!-- Content -->
      <ArticleContent :content="article.content" />

      <!-- Series Navigation -->
      <div v-if="article.series && article.seriesArticles?.length" class="mt-12 p-6 bg-bg-card rounded-xl border border-border">
        <h3 class="text-lg font-semibold text-text mb-4">
          系列：{{ article.series.title }}
        </h3>
        <ul class="space-y-2">
          <li
            v-for="(seriesArticle, index) in article.seriesArticles"
            :key="seriesArticle.slug.current"
            class="flex items-center gap-2"
          >
            <span class="text-sm text-text-light">{{ index + 1 }}.</span>
            <NuxtLink
              :to="`/posts/${seriesArticle.slug.current}`"
              class="text-sm hover:text-accent transition-colors"
              :class="seriesArticle.slug.current === article.slug.current ? 'text-accent font-medium' : 'text-text-muted'"
            >
              {{ seriesArticle.title }}
            </NuxtLink>
          </li>
        </ul>
      </div>

      <!-- Comments -->
      <GiscusComments />
    </article>

    <!-- 404 -->
    <div v-else class="text-center py-20">
      <h1 class="text-4xl font-bold text-text mb-4">404</h1>
      <p class="text-text-muted mb-6">文章未找到</p>
      <NuxtLink to="/" class="text-accent hover:underline">
        ← 返回首页
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { fetchArticleBySlug } = useSanity()

const slug = route.params.slug as string

const { data: article, pending, error } = await useAsyncData(`article-${slug}`, () => fetchArticleBySlug(slug))

// SEO
useHead(() => {
  if (!article.value) return {}
  
  return {
    title: `${article.value.title} - 我的博客`,
    meta: [
      {
        name: 'description',
        content: article.value.excerpt || ''
      },
      {
        property: 'og:title',
        content: article.value.title
      },
      {
        property: 'og:description',
        content: article.value.excerpt || ''
      },
      {
        property: 'og:type',
        content: 'article'
      }
    ]
  }
})
</script>
