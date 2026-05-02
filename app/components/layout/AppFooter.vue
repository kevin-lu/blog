<template>
  <footer class="border-t border-border mt-auto">
    <div class="max-w-content mx-auto px-6 py-8">
      <div class="flex flex-col md:flex-row items-center justify-between gap-4">
        <!-- Copyright -->
        <p class="text-sm text-text-muted">
          © {{ currentYear }} {{ siteTitle }}. All rights reserved.
        </p>

        <!-- Social Links -->
        <div v-if="socialLinks?.length" class="flex items-center gap-4">
          <a
            v-for="link in socialLinks"
            :key="link.platform"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-text-muted hover:text-text transition-colors"
            :aria-label="link.platform"
          >
            <span class="capitalize text-sm">{{ link.platform }}</span>
          </a>
        </div>

        <!-- Powered by -->
        <p class="text-xs text-text-light">
          Powered by 
          <a href="https://nuxt.com" target="_blank" rel="noopener" class="hover:text-text-muted transition-colors">Nuxt</a>
          &
          <a href="https://sanity.io" target="_blank" rel="noopener" class="hover:text-text-muted transition-colors">Sanity</a>
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const { data: siteSettings } = await useAsyncData('siteSettings', () => useSanity().fetchSiteSettings())

const currentYear = new Date().getFullYear()
const siteTitle = computed(() => siteSettings.value?.title || '我的博客')
const socialLinks = computed(() => siteSettings.value?.socialLinks || [])
</script>
