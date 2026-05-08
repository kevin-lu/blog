<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <h1 class="text-2xl font-bold text-text mb-8">文章分类</h1>
    
    <div v-if="pending" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
    </div>

    <div v-else-if="error" class="text-center py-12 text-text-muted">
      <p>加载失败，请稍后重试</p>
    </div>

    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      <NuxtLink
        v-for="category in categories"
        :key="category._id"
        :to="`/categories/${category.slug.current}`"
        class="block p-6 bg-bg-card rounded-xl border border-border hover:border-border-hover hover:shadow-md transition-all"
      >
        <h2 class="text-lg font-semibold text-text mb-2">{{ category.title }}</h2>
        <p v-if="category.description" class="text-sm text-text-muted mb-3 line-clamp-2">
          {{ category.description }}
        </p>
        <span class="text-xs text-text-light">{{ category.articleCount || 0 }} 篇文章</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const { fetchCategories } = useBlogData()

const { data: categories, pending, error } = await useAsyncData('categories', () => fetchCategories())

useHead({
  title: '文章分类 - 我的博客',
  meta: [
    { name: 'description', content: '浏览所有文章分类' }
  ]
})
</script>
