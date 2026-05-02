<template>
  <div class="space-y-6">
    <div v-if="pending" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent" />
    </div>

    <div v-else-if="error" class="text-center py-12 text-text-muted">
      <p>加载文章失败，请稍后重试</p>
      <button
        @click="refresh"
        class="mt-4 px-4 py-2 text-sm bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors"
      >
        重新加载
      </button>
    </div>

    <div v-else-if="!articles?.length" class="text-center py-12 text-text-muted">
      <p>暂无文章</p>
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2">
      <ArticleCard
        v-for="article in articles"
        :key="article._id"
        :article="article"
      />
    </div>

    <!-- Load More -->
    <div v-if="showLoadMore && articles?.length" class="text-center pt-6">
      <button
        @click="$emit('loadMore')"
        class="px-6 py-2.5 text-sm font-medium text-text-muted bg-bg-card border border-border rounded-lg hover:border-border-hover hover:text-text transition-all"
        :disabled="loadingMore"
      >
        <span v-if="loadingMore">加载中...</span>
        <span v-else>加载更多</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ArticleListItem } from '~/types'

interface Props {
  articles?: ArticleListItem[]
  pending?: boolean
  error?: Error | null
  showLoadMore?: boolean
  loadingMore?: boolean
}

interface Emits {
  (e: 'refresh'): void
  (e: 'loadMore'): void
}

defineProps<Props>()
defineEmits<Emits>()

const refresh = () => {
  location.reload()
}
</script>
