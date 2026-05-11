<template>
  <article class="article-content prose prose-lg max-w-none" data-article-content>
    <SanityContent v-if="isPortableText" :blocks="content" />
    <div v-else v-html="renderedContent" />
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { renderArticleContent } from '~/utils/markdown'

interface Props {
  content?: any[] | string
}

const props = defineProps<Props>()

const isPortableText = computed(() => Array.isArray(props.content))
const renderedContent = computed(() => {
  return typeof props.content === 'string' ? renderArticleContent(props.content) : ''
})
</script>
