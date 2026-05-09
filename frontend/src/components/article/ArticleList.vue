<template>
  <div class="article-list">
    <div v-if="loading" class="loading">
      <n-spin size="large" description="加载中..." />
    </div>

    <div v-else-if="articles.length === 0" class="empty">
      <n-empty description="暂无文章" size="large" />
    </div>

    <div v-else class="articles">
      <ArticleCard
        v-for="article in articles"
        :key="article.id"
        :article="article"
      />

      <div class="pagination" v-if="pagination.pages > 1">
        <n-pagination
          v-model:page="currentPage"
          v-model:page-size="pageSize"
          :item-count="pagination.total"
          :page-sizes="[10, 20, 30, 50]"
          show-size-picker
          @update-page="handlePageChange"
        >
          <template #prefix="{ itemCount }">
            共 {{ itemCount }} 篇文章
          </template>
        </n-pagination>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Article } from '@/types'
import { articleApi } from '@/api'
import ArticleCard from '@/components/article/ArticleCard.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const articles = ref<Article[]>([])
const currentPage = ref(1)
const pageSize = ref(10)

const pagination = ref({
  total: 0,
  pages: 0,
  page: 1,
  limit: 10,
})

const loadArticles = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      limit: pageSize.value,
    }

    // 从路由参数中获取筛选条件
    if (route.query.category) {
      params.category = route.query.category as string
    }
    if (route.query.tag) {
      params.tag = route.query.tag as string
    }
    if (route.query.search) {
      params.search = route.query.search as string
    }

    const response = await articleApi.getList(params)
    articles.value = response.data.data
    pagination.value = {
      total: response.data.total,
      pages: response.data.totalPages,
      page: response.data.page,
      limit: response.data.pageSize,
    }
  } catch (error) {
    console.error('Failed to load articles:', error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page: number) => {
  router.push({
    query: {
      ...route.query,
      page: page.toString(),
    },
  })
}

watch(() => route.query, () => {
  const page = route.query.page ? parseInt(route.query.page as string) : 1
  currentPage.value = page
  loadArticles()
}, { deep: true })

onMounted(() => {
  const page = route.query.page ? parseInt(route.query.page as string) : 1
  currentPage.value = page
  loadArticles()
})
</script>

<style scoped>
.article-list {
  max-width: 900px;
  margin: 0 auto;
}

.loading,
.empty {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.articles {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.pagination {
  margin-top: 40px;
  display: flex;
  justify-content: center;
}
</style>
