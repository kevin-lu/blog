<template>
  <div class="category-posts-page">
    <div class="page-header">
      <n-breadcrumb>
        <n-breadcrumb-item @click="router.push('/categories')">
          分类
        </n-breadcrumb-item>
        <n-breadcrumb-item>
          {{ categoryName }}
        </n-breadcrumb-item>
      </n-breadcrumb>

      <h1>{{ categoryName }}</h1>
      <p>共有 {{ total }} 篇文章</p>
    </div>

    <ArticleList />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ArticleList from '@/components/article/ArticleList.vue'

const router = useRouter()
const route = useRoute()

const categoryName = ref('')
const total = ref(0)

onMounted(() => {
  // TODO: 从 API 获取分类信息
  categoryName.value = route.params.name as string
  total.value = 0
})
</script>

<style scoped>
.category-posts-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 0;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
}

.page-header p {
  margin: 0;
  font-size: 14px;
  color: #666;
}
</style>
