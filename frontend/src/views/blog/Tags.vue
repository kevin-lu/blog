<template>
  <div class="tags-page">
    <div class="page-header">
      <h1>标签</h1>
      <p>浏览所有标签</p>
    </div>

    <div v-if="loading" class="loading">
      <n-spin size="large" description="加载中..." />
    </div>

    <div v-else class="tags-cloud">
      <n-tag
        v-for="tag in tags"
        :key="tag.id"
        :bordered="false"
        round
        size="large"
        checkable
        @click="goToTagPosts(tag.slug)"
      >
        {{ tag.name }}
        <template #icon>
          <span style="margin-left: 4px; opacity: 0.6">
            {{ tag.article_count || 0 }}
          </span>
        </template>
      </n-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { Tag } from '@/types'
import { tagApi } from '@/api'

const router = useRouter()

const loading = ref(false)
const tags = ref<Tag[]>([])

const goToTagPosts = (slug: string) => {
  router.push(`/tags/${slug}`)
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await tagApi.getList()
    tags.value = response.data
  } catch (error) {
    console.error('Failed to load tags:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.tags-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 0;
}

.page-header {
  margin-bottom: 40px;
  text-align: center;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
}

.page-header p {
  margin: 0;
  font-size: 16px;
  color: #666;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
}

.tags-cloud .n-tag {
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.tags-cloud .n-tag:hover {
  transform: scale(1.1);
  background-color: #18a058;
  color: white;
}
</style>
