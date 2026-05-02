<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <!-- Hero Section -->
    <section v-if="siteSettings" class="mb-12">
      <div class="flex flex-col md:flex-row items-center gap-6 bg-bg-card rounded-2xl p-6 shadow-md">
        <SanityImage
          v-if="siteSettings.avatar"
          :asset-id="siteSettings.avatar.asset._ref"
          class="w-20 h-20 rounded-full object-cover"
          :alt="siteSettings.author || 'Avatar'"
        />
        <div class="text-center md:text-left">
          <h1 class="text-2xl font-bold text-text mb-2">
            {{ siteSettings.title }}
          </h1>
          <p v-if="siteSettings.bio" class="text-text-muted">
            {{ siteSettings.bio }}
          </p>
        </div>
      </div>
    </section>

    <!-- Articles Section -->
    <section>
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold text-text">最新文章</h2>
        <NuxtLink
          to="/categories"
          class="text-sm text-accent hover:underline"
        >
          查看全部 →
        </NuxtLink>
      </div>

      <ArticleList
        :articles="articles"
        :pending="pending"
        :error="error"
        :show-load-more="hasMore"
        :loading-more="loadingMore"
        @load-more="loadMore"
      />
    </section>
  </div>
</template>

<script setup lang="ts">
const { fetchArticles, fetchSiteSettings } = useSanity()

// 获取站点设置
const { data: siteSettings } = await useAsyncData('siteSettings', () => fetchSiteSettings())

// 获取文章列表
const pageSize = 10
const page = ref(1)
const articles = ref<ArticleListItem[]>([])
const hasMore = ref(true)
const loadingMore = ref(false)

const { data: initialArticles, pending, error } = await useAsyncData('articles', () => fetchArticles(pageSize, 0))

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
