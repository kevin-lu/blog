<template>
  <div class="tag-filter">
    <div class="tag-list">
      <n-tag
        v-for="tag in tags"
        :key="tag.id"
        :bordered="false"
        round
        checkable
        :checked="activeTag === tag.slug"
        @click="handleTagClick(tag.slug)"
      >
        {{ tag.name }}
      </n-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { Tag } from '@/types'
import { tagApi } from '@/api'

const router = useRouter()
const route = useRoute()

const tags = ref<Tag[]>([])
const activeTag = ref('')

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
  margin-bottom: 24px;
  padding: 16px 0;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-list .n-tag {
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(24, 160, 88, 0.08);
  color: #18a058;
}

.tag-list .n-tag:hover {
  transform: scale(1.05);
  background: rgba(24, 160, 88, 0.15);
}

.tag-list .n-tag.n-tag--checked {
  background: #18a058;
  color: white;
}
</style>
