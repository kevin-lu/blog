<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <div class="mb-8">
      <NuxtLink to="/categories" class="text-sm text-text-muted hover:text-accent transition-colors">
        ← 全部分类
      </NuxtLink>
      <h1 class="text-2xl font-bold text-text mt-4">{{ categoryName }}</h1>
    </div>

    <ArticleList
      :articles="articles"
      :pending="pending"
      :error="error"
    />
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { fetchArticlesByCategory } = useBlogData()

const categoryName = computed(() => route.params.name as string)

const { data: articles, pending, error } = await useAsyncData(
  `category-${categoryName.value}`,
  () => fetchArticlesByCategory(categoryName.value, 20)
)

useHead({
  title: `${categoryName.value} - 文章分类 - 我的博客`
})
</script>
