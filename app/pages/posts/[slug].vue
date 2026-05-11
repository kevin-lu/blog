<template>
  <div class="max-w-4xl mx-auto px-6 py-8">
    <!-- 加载中 -->
    <div v-if="pending" class="text-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto"></div>
      <p class="mt-4 text-gray-500">加载中...</p>
    </div>

    <article v-else-if="article">
      <!-- 返回链接 -->
      <NuxtLink to="/" class="inline-flex items-center gap-1 text-gray-400 hover:text-gray-600 mb-6 transition-colors">
        <span>←</span>
        <span>返回首页</span>
      </NuxtLink>

      <!-- 编号和标题 -->
      <header class="mb-8">
        <div class="text-sm text-gray-300 mb-2">No.{{ article.order || 0 }}</div>
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4 leading-tight">
          {{ article.title }}
        </h1>

        <!-- 元信息 -->
        <div class="flex flex-wrap items-center gap-4 text-sm text-gray-400">
          <time :datetime="articleDate">
            {{ formatDate(articleDate) }}
          </time>
          <NuxtLink
            v-if="article.category"
            :to="`/categories/${article.category.slug.current}`"
            class="text-gray-500 hover:text-accent transition-colors"
          >
            {{ article.category.title }}
          </NuxtLink>
          <span v-if="article.readingTime">
            {{ article.readingTime }} 分钟阅读
          </span>
          <span v-if="updatedDate" class="text-gray-400">
            更新于 {{ formatDate(updatedDate) }}
          </span>
        </div>

        <!-- 标签 -->
        <div v-if="article.tags?.length" class="flex flex-wrap gap-2 mt-3">
          <NuxtLink
            v-for="tag in article.tags"
            :key="tag._id"
            :to="`/tags/${tag.slug.current}`"
            class="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
          >
            {{ tag.title }}
          </NuxtLink>
        </div>
      </header>

      <!-- 封面图 -->
      <SanityImage
        v-if="article?.coverImage"
        :asset-id="article.coverImage.asset._ref"
        class="w-full aspect-video object-cover rounded-xl mb-8"
        :alt="article.title"
      />

      <!-- 目录 -->
      <ClientOnly>
        <details v-if="headings.length > 0" class="mb-8 bg-gray-50 rounded-lg p-4">
          <summary class="text-sm font-medium text-gray-700 cursor-pointer list-none flex items-center justify-between">
            <span>目录</span>
            <svg class="w-4 h-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </summary>
          <ul class="mt-3 space-y-2 text-sm">
            <li v-for="heading in headings" :key="heading.id">
              <a
                :href="`#${heading.id}`"
                class="block text-gray-500 hover:text-accent transition-colors"
                :class="{ 'pl-4': heading.level === 3 }"
                @click.prevent="scrollToHeading(heading.id)"
              >
                {{ heading.text }}
              </a>
            </li>
          </ul>
        </details>
      </ClientOnly>

      <!-- 正文内容 -->
      <div v-if="article?.content" class="prose prose-gray max-w-none">
        <ArticleContent :content="article.content" />
      </div>

      <!-- 系列文章导航 -->
      <ClientOnly>
        <SeriesNavigation
          v-if="article?.series"
          :series-slug="article.series.slug.current"
          :series-title="article.series.title"
          :current-article-id="article._id"
        />
      </ClientOnly>

      <!-- 相关文章推荐 -->
      <ClientOnly>
        <RelatedArticles
          :article-id="article._id"
          :category-slug="article.category?.slug?.current"
          :tags="article.tags"
        />
      </ClientOnly>

      <!-- 底部导航 -->
      <nav class="mt-12 pt-6 border-t border-gray-200">
        <NuxtLink to="/" class="inline-flex items-center gap-1 text-gray-400 hover:text-gray-600 transition-colors">
          <span>←</span>
          <span>返回首页</span>
        </NuxtLink>
      </nav>
    </article>

    <!-- 404 -->
    <div v-else class="text-center py-20">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">404</h1>
      <p class="text-gray-400 mb-6">文章未找到</p>
      <NuxtLink to="/" class="text-accent hover:underline">
        ← 返回首页
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatDate } from '~/utils/helpers'
import { extractArticleHeadings } from '~/utils/markdown'
import type { ArticleDetail } from '~/types'

definePageMeta({
  ssr: false
})

const route = useRoute()
const { fetchArticleBySlug } = useBlogData()

console.log('Route params:', route.params)
console.log('Route path:', route.path)

const slug = computed(() => route.params.slug as string)

console.log('Slug value:', slug.value)

const { data: article, pending } = await useAsyncData<ArticleDetail | null>(
  `article-${slug.value}`,
  () => fetchArticleBySlug(slug.value),
  {
    lazy: true,
    default: () => null
  }
)

// 调试日志
watch(article, (newArticle) => {
  console.log('Article data:', newArticle)
  if (newArticle) {
    console.log('Article content:', newArticle.content)
  }
}, { immediate: true })

const headings = ref<{ id: string; text: string; level: number }[]>([])
const articleDate = computed(() => article.value?.publishedAt || article.value?.published_at || article.value?.createdAt || article.value?.created_at)
const updatedDate = computed(() => article.value?.updatedAt || article.value?.updated_at)

function generateId(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fa5]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function uniqueHeadingId(text: string, seen: Map<string, number>): string {
  const base = generateId(text) || 'section'
  const count = seen.get(base) || 0
  seen.set(base, count + 1)
  return count === 0 ? base : `${base}-${count + 1}`
}

function extractHeadings() {
  const content = article.value?.content
  if (!content) {
    headings.value = []
    return
  }

  if (typeof content === 'string') {
    headings.value = extractArticleHeadings(content)
    return
  }

  const result: { id: string; text: string; level: number }[] = []
  const seen = new Map<string, number>()

  function traverse(blocks: any[]) {
    for (const block of blocks) {
      if (block._type === 'block') {
        const style = block.style || 'normal'
        if (style === 'h2' || style === 'h3') {
          const text = block.children?.map((c: any) => c.text).join('') || ''
          if (text) {
            result.push({
              id: uniqueHeadingId(text, seen),
              text,
              level: style === 'h2' ? 2 : 3
            })
          }
        }
      }
      if (block._type === 'block' && block.children) {
        traverse(block.children)
      }
    }
  }

  traverse(article.value.content)
  headings.value = result
}

function scrollToHeading(id: string) {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    history.pushState(null, '', `#${id}`)
  }
}

function addIdsToHeadings() {
  if (!article.value?.content) return
  
  nextTick(() => {
    const articleEl = document.querySelector('[data-article-content]')
    if (!articleEl) return
    
    const domHeadings = articleEl.querySelectorAll('h2, h3')
    const seen = new Map<string, number>()
    const renderedHeadings: { id: string; text: string; level: number }[] = []

    domHeadings.forEach((heading) => {
      const text = heading.textContent?.trim() || ''
      if (!text) return

      const id = uniqueHeadingId(text, seen)
      heading.id = id
      renderedHeadings.push({
        id,
        text,
        level: heading.tagName.toLowerCase() === 'h2' ? 2 : 3
      })
    })

    if (typeof article.value?.content === 'string') {
      headings.value = renderedHeadings
    }
  })
}

onMounted(() => {
  extractHeadings()
  addIdsToHeadings()
})

watch(() => article.value, () => {
  nextTick(() => {
    extractHeadings()
    addIdsToHeadings()
  })
})

useHead(() => {
  if (!article.value) return {}
  
  return {
    title: `${article.value.title} - 我的博客`,
    meta: [
      {
        name: 'description',
        content: article.value.excerpt || ''
      }
    ]
  }
})
</script>
