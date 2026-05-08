<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <div class="mb-8">
      <NuxtLink to="/tags" class="text-sm text-text-muted hover:text-accent transition-colors">
        ← 全部标签
      </NuxtLink>
      <h1 class="text-2xl font-bold text-text mt-4">
        <span class="text-accent">#</span>{{ tagName }}
      </h1>
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
const { fetchArticlesByTag } = useBlogData()

const tagName = computed(() => route.params.name as string)

const { data: articles, pending, error } = await useAsyncData(
  `tag-${tagName.value}`,
  () => fetchArticlesByTag(tagName.value, 20)
)

useHead({
  title: `#${tagName.value} - 文章标签 - 我的博客`
})
</script>
