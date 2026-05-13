<template>
  <div class="home-page">
    <div class="home-content">
      <div class="main-content">
        <!-- Search Bar -->
        <div class="search-bar">
          <n-input
            v-model:value="searchQuery"
            placeholder="搜索文章..."
            round
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <n-icon :component="SearchOutline" />
            </template>
            <template #suffix>
              <n-button text type="primary" @click="handleSearch">
                搜索
              </n-button>
            </template>
          </n-input>
        </div>

        <!-- Tag Filter -->
        <TagFilter />

        <!-- Article List -->
        <ArticleList />
      </div>

      <!-- Sidebar -->
      <aside class="sidebar">
        <Sidebar />
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { SearchOutline } from '@vicons/ionicons5'
import ArticleList from '@/components/article/ArticleList.vue'
import Sidebar from '@/components/article/Sidebar.vue'
import TagFilter from '@/components/article/TagFilter.vue'

const router = useRouter()
const route = useRoute()

const searchQuery = ref('')

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({
      query: {
        ...route.query,
        search: searchQuery.value,
        page: '1',
      },
    })
  } else {
    const newQuery = { ...route.query }
    delete newQuery.search
    router.push({ query: newQuery })
  }
}

// Initialize search query from route
if (route.query.search) {
  searchQuery.value = route.query.search as string
}
</script>

<style scoped>
.home-page {
  padding: 24px 0;
}

@media (max-width: 768px) {
  .home-page {
    padding: 16px 0;
  }
}

.home-content {
  display: block;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

@media (min-width: 1200px) {
  .home-content {
    display: grid;
    grid-template-columns: 1fr 320px;
    gap: 32px;
  }
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-width: 0;
}

.search-bar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: transparent;
  padding: 16px 0;
}

@media (max-width: 768px) {
  .search-bar {
    padding: 12px 0;
  }
}

.search-bar .n-input {
  height: 48px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(24, 160, 88, 0.1);
  border-radius: 24px;
  transition: all 0.2s;
}

.search-bar .n-input:hover {
  border-color: rgba(24, 160, 88, 0.3);
}

.search-bar .n-input:focus-within {
  border-color: #18a058;
  box-shadow: 0 0 0 3px rgba(24, 160, 88, 0.1);
}

@media (max-width: 768px) {
  .search-bar .n-input {
    height: 44px;
  }
}

.sidebar {
  display: none;
}

@media (min-width: 1200px) {
  .sidebar {
    display: block;
    position: sticky;
    top: 88px;
    height: fit-content;
  }
}
</style>
