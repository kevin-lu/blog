<template>
  <div v-if="articles.length > 0" class="related-articles mt-12 pt-8 border-t border-gray-200">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">相关文章</h3>
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <NuxtLink
        v-for="article in articles"
        :key="article._id"
        :to="`/posts/${article.slug.current}`"
        class="block p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
      >
        <h4 class="font-medium text-gray-800 mb-2 line-clamp-2 hover:text-accent">
          {{ article.title }}
        </h4>
        <div class="flex items-center gap-2 text-xs text-gray-400">
          <time :datetime="article.publishedAt">
            {{ formatDate(article.publishedAt) }}
          </time>
          <span v-if="article.readingTime">{{ article.readingTime }} 分钟</span>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ArticleListItem } from '~/types'
import { formatDate } from '~/utils/helpers'

interface Props {
  articleId: string
  categorySlug?: string
  tags?: { slug: { current: string } }[]
}

const props = defineProps<Props>()

const { fetchRelatedArticles } = useBlogData()

const articles = ref<ArticleListItem[]>([])

const tagSlugs = computed(() => props.tags?.map(t => t.slug.current) || [])

const { pending } = await useAsyncData(
  `related-${props.articleId}`,
  () => fetchRelatedArticles(
    props.articleId,
    props.categorySlug,
    tagSlugs.value,
    3
  ),
  {
    transform: (data) => {
      articles.value = data.map(article => ({
        ...article,
        categorySlug: article.category?.slug?.current || ''
      }))
      return data
    }
  }
)
</script>
