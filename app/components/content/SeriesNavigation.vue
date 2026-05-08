<template>
  <div v-if="seriesArticles.length > 0" class="series-navigation mt-8 p-4 bg-gray-50 rounded-lg">
    <div class="flex items-center gap-2 mb-3">
      <svg class="w-4 h-4 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
        <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
      </svg>
      <NuxtLink
        v-if="seriesSlug"
        :to="`/series/${seriesSlug}`"
        class="text-sm font-medium text-accent hover:underline"
      >
        {{ seriesTitle }}
      </NuxtLink>
      <span v-else class="text-sm font-medium text-gray-700">{{ seriesTitle }}</span>
    </div>
    <ul class="space-y-2">
      <li v-for="article in seriesArticles" :key="article._id">
        <NuxtLink
          :to="`/posts/${article.slug.current}`"
          class="flex items-center gap-2 text-sm text-gray-600 hover:text-accent transition-colors"
        >
          <span
            class="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs"
            :class="article._id === currentArticleId ? 'bg-accent text-white' : 'bg-gray-200 text-gray-500'"
          >
            {{ article.order || '' }}
          </span>
          <span :class="{ 'font-medium text-accent': article._id === currentArticleId }">
            {{ article.title }}
          </span>
        </NuxtLink>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { ArticleListItem } from '~/types'

interface Props {
  seriesSlug?: string
  seriesTitle?: string
  currentArticleId: string
}

const props = defineProps<Props>()

const { fetchSeriesArticles } = useBlogData()

const seriesArticles = ref<ArticleListItem[]>([])

await useAsyncData(
  `series-${props.seriesSlug}`,
  () => fetchSeriesArticles(props.seriesSlug!, props.currentArticleId, 10),
  {
    transform: (data) => {
      seriesArticles.value = data.map(article => ({
        ...article,
        categorySlug: article.category?.slug?.current || ''
      }))
      return data
    }
  }
)
</script>
