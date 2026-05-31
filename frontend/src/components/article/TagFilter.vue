<template>
  <div class="tag-filter">
    <div class="tag-filter-header">
      <span class="tag-filter-title">
        <n-icon :component="PricetagsOutline" size="16" />
        标签筛选
      </span>
      <n-text v-if="activeTag" class="tag-filter-count">
        已选择：<n-tag :bordered="false" size="small" type="success" round>{{ activeTagName }}</n-tag>
        <n-button text type="primary" size="small" @click="clearFilter">
          <template #icon>
            <n-icon :component="CloseOutline" />
          </template>
          清除
        </n-button>
      </n-text>
    </div>
    <div class="tag-list">
      <n-tag
        v-for="tag in tags"
        :key="tag.id"
        :bordered="false"
        round
        checkable
        :checked="activeTag === tag.slug"
        @click="handleTagClick(tag.slug)"
        class="tag-item"
      >
        <template #icon>
          <span class="tag-icon">#</span>
        </template>
        {{ tag.name }}
      </n-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { PricetagsOutline, CloseOutline } from '@vicons/ionicons5'
import type { Tag } from '@/types'
import { tagApi } from '@/api'

const router = useRouter()
const route = useRoute()

const tags = ref<Tag[]>([])
const activeTag = ref('')

const activeTagName = computed(() => {
  const tag = tags.value.find(t => t.slug === activeTag.value)
  return tag?.name || activeTag.value
})

const handleTagClick = (slug: string) => {
  if (activeTag.value === slug) {
    const newQuery = { ...route.query }
    delete newQuery.tag
    router.push({ query: newQuery })
  } else {
    router.push({
      query: {
        ...route.query,
        tag: slug,
        page: '1',
      },
    })
  }
}

const clearFilter = () => {
  const newQuery = { ...route.query }
  delete newQuery.tag
  router.push({ query: newQuery })
}

onMounted(async () => {
  try {
    const response = await tagApi.getList()
    tags.value = response.data
  } catch (error) {
    console.error('Failed to load tags:', error)
  }
  
  if (route.query.tag) {
    activeTag.value = route.query.tag as string
  }
})
</script>

<style scoped>
.tag-filter {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(24, 160, 88, 0.02) 0%, rgba(24, 160, 88, 0.05) 100%);
  border-radius: 12px;
  border: 1px solid rgba(24, 160, 88, 0.08);
}

.tag-filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.tag-filter-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #18a058;
  letter-spacing: 0.5px;
}

.tag-filter-count {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #666;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-item {
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(24, 160, 88, 0.12);
  font-size: 13px;
  padding: 4px 12px;
  height: auto;
  line-height: 1.5;
}

.tag-item:hover {
  transform: translateY(-2px);
  background: rgba(24, 160, 88, 0.08);
  border-color: rgba(24, 160, 88, 0.3);
  box-shadow: 0 4px 12px rgba(24, 160, 88, 0.15);
}

.tag-item.n-tag--checked {
  background: linear-gradient(135deg, #18a058 0%, #0c7a43 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px rgba(24, 160, 88, 0.3);
}

.tag-icon {
  font-size: 12px;
  opacity: 0.6;
  margin-right: 2px;
  font-weight: 300;
}

.n-tag--checked .tag-icon {
  opacity: 0.8;
  color: rgba(255, 255, 255, 0.9);
}
</style>
