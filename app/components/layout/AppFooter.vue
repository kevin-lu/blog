<template>
  <footer class="border-t border-gray-200 mt-auto">
    <div class="max-w-4xl mx-auto px-6 py-6">
      <div class="flex items-center justify-between text-sm text-gray-400">
        <p>© {{ currentYear }} {{ siteTitle }}. 保留所有权利</p>
        <p class="text-xs">Powered by Nuxt + Sanity</p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const { data: siteSettings } = await useAsyncData('siteSettings', () => useSanity().fetchSiteSettings())

const currentYear = new Date().getFullYear()
const siteTitle = computed(() => siteSettings.value?.title || '我的博客')
</script>