<template>
  <div class="max-w-content mx-auto px-6 py-8">
    <div v-if="siteSettings" class="max-w-2xl mx-auto">
      <!-- Profile -->
      <div class="text-center mb-12">
        <SanityImage
          v-if="siteSettings.avatar"
          :asset-id="siteSettings.avatar.asset._ref"
          class="w-24 h-24 rounded-full object-cover mx-auto mb-4"
          :alt="siteSettings.author || 'Avatar'"
        />
        <h1 class="text-2xl font-bold text-text mb-2">
          {{ siteSettings.author || siteSettings.title }}
        </h1>
        <p v-if="siteSettings.bio" class="text-text-muted">
          {{ siteSettings.bio }}
        </p>
      </div>

      <!-- Social Links -->
      <div v-if="siteSettings.socialLinks?.length" class="mb-12">
        <h2 class="text-lg font-semibold text-text mb-4">联系方式</h2>
        <div class="flex flex-wrap gap-4">
          <a
            v-for="link in siteSettings.socialLinks"
            :key="link.platform"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-2 px-4 py-2 bg-bg-card border border-border rounded-lg hover:border-accent hover:text-accent transition-all"
          >
            <span class="capitalize">{{ link.platform }}</span>
          </a>
        </div>
      </div>

      <!-- Description -->
      <div v-if="siteSettings.description" class="prose prose-lg max-w-none">
        <h2 class="text-lg font-semibold text-text mb-4">关于本站</h2>
        <p class="text-text-muted">{{ siteSettings.description }}</p>
      </div>
    </div>

    <div v-else class="text-center py-20 text-text-muted">
      <p>暂无内容</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { fetchSiteSettings } = useBlogData()

const { data: siteSettings } = await useAsyncData('about', () => fetchSiteSettings())

useHead({
  title: '关于 - 我的博客',
  meta: [
    { name: 'description', content: siteSettings.value?.description || '关于本站' }
  ]
})
</script>
