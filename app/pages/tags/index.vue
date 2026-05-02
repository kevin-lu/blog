<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <h1 class="text-2xl font-bold text-text mb-8">文章标签</h1>
    
    <div v-if="pending" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
    </div>

    <div v-else-if="error" class="text-center py-12 text-text-muted">
      <p>加载失败，请稍后重试</p>
    </div>

    <div v-else class="flex flex-wrap gap-3">
      <NuxtLink
        v-for="tag in tags"
        :key="tag._id"
        :to="`/tags/${tag.slug.current}`"
        class="px-4 py-2 bg-bg-card border border-border rounded-full text-sm text-text-muted hover:border-accent hover:text-accent transition-all"
      >
        {{ tag.title }}
        <span class="ml-1 text-text-light">({{ tag.articleCount || 0 }})</span>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const { fetchTags } = useSanity()

const { data: tags, pending, error } = await useAsyncData('tags', () => fetchTags())

useHead({
  title: '文章标签 - 我的博客',
  meta: [
    { name: 'description', content: '浏览所有文章标签' }
  ]
})
</script>
