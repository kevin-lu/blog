<template>
  <nav v-if="headings.length > 0" class="toc bg-gray-50 rounded-lg p-4 sticky top-8">
    <h4 class="text-sm font-semibold text-gray-700 mb-3">目录</h4>
    <ul class="space-y-2 text-sm">
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
  </nav>
</template>

<script setup lang="ts">
interface Heading {
  id: string
  text: string
  level: number
}

interface Props {
  content?: any[]
}

const props = defineProps<Props>()

const headings = ref<Heading[]>([])

function generateId(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\u4e00-\u9fa5]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function extractHeadings() {
  if (!props.content) return

  const result: Heading[] = []

  function traverse(blocks: any[]) {
    for (const block of blocks) {
      if (block._type === 'block') {
        const style = block.style || 'normal'
        if (style === 'h2' || style === 'h3') {
          const text = block.children?.map((c: any) => c.text).join('') || ''
          if (text) {
            result.push({
              id: generateId(text),
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

  traverse(props.content)
  headings.value = result
}

function scrollToHeading(id: string) {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    history.pushState(null, '', `#${id}`)
  }
}

onMounted(() => {
  extractHeadings()
})

watch(() => props.content, () => {
  extractHeadings()
})
</script>

<style scoped>
.toc {
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}
</style>
