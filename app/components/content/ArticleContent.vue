<template>
  <article class="prose prose-lg max-w-none">
    <SanityContent :blocks="content" />
  </article>
</template>

<script setup lang="ts">
interface Props {
  content?: any[]
}

defineProps<Props>()
</script>
