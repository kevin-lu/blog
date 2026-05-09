<template>
  <div class="categories-page">
    <div class="page-header">
      <h1>分类</h1>
      <p>浏览所有分类</p>
    </div>

    <div v-if="loading" class="loading">
      <n-spin size="large" description="加载中..." />
    </div>

    <div v-else class="categories-grid">
      <n-card
        v-for="category in categories"
        :key="category.id"
        class="category-card"
        hoverable
        @click="goToCategoryPosts(category.slug)"
      >
        <div class="category-content">
          <div class="category-icon">
            <n-icon :component="FolderOutline" size="40" />
          </div>

          <h3 class="category-name">{{ category.name }}</h3>

          <p v-if="category.description" class="category-description">
            {{ category.description }}
          </p>

          <div class="category-meta">
            <n-tag :bordered="false" size="small" type="info">
              {{ category.article_count || 0 }} 篇文章
            </n-tag>
          </div>
        </div>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { FolderOutline } from '@vicons/ionicons5'
import type { Category } from '@/types'
import { categoryApi } from '@/api'

const router = useRouter()

const loading = ref(false)
const categories = ref<Category[]>([])

const goToCategoryPosts = (slug: string) => {
  router.push(`/categories/${slug}`)
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await categoryApi.getList()
    categories.value = response.data
  } catch (error) {
    console.error('Failed to load categories:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.categories-page {
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

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.category-card {
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.category-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
  padding: 16px 0;
}

.category-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 8px;
}

.category-name {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.category-description {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.category-meta {
  margin-top: 8px;
}
</style>
