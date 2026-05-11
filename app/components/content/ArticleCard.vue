<template>
  <article class="bg-bg-card rounded-xl shadow-md overflow-hidden transition-all duration-200 hover:shadow-lg hover:border-border-hover border border-transparent">
    <!-- Cover Image -->
    <NuxtLink v-if="article.coverImage" :to="`/posts/${article.slug.current}`" class="block aspect-video overflow-hidden">
      <SanityImage
        :asset-id="article.coverImage.asset._ref"
        class="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
        :alt="article.title"
      />
    </NuxtLink>

    <div class="p-5">
      <!-- Category -->
      <NuxtLink
        :to="`/categories/${article.categorySlug}`"
        class="inline-block text-xs font-medium text-accent mb-2 hover:underline"
      >
        {{ article.category }}
      </NuxtLink>

      <!-- Title -->
      <h2 class="text-lg font-semibold text-text mb-2 leading-tight">
        <NuxtLink :to="`/posts/${article.slug.current}`" class="hover:text-accent transition-colors">
          {{ article.title }}
        </NuxtLink>
      </h2>

      <!-- Excerpt -->
      <p v-if="article.excerpt" class="text-sm text-text-muted line-clamp-2 mb-3">
        {{ article.excerpt }}
      </p>

      <!-- Meta -->
      <div class="flex items-center gap-3 text-xs text-text-light">
        <time :datetime="articleDate">
          {{ formatDate(articleDate) }}
        </time>
        <span v-if="article.readingTime" class="flex items-center gap-1">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <polyline points="12 6 12 12 16 14" />
          </svg>
          {{ article.readingTime }} 分钟
        </span>
      </div>

      <!-- Tags -->
      <div v-if="article.tags?.length" class="flex flex-wrap gap-2 mt-3">
        <span
          v-for="tag in article.tags.slice(0, 3)"
          :key="tag"
          class="text-xs px-2 py-0.5 bg-accent-light text-accent rounded"
        >
          {{ tag }}
        </span>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ArticleListItem } from '~/types'
import { formatDate } from '~/utils/helpers'

interface Props {
  article: ArticleListItem
}

const props = defineProps<Props>()

const articleDate = computed(() => props.article.publishedAt || props.article.published_at || props.article.createdAt || props.article.created_at)
</script>
