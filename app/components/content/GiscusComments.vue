<template>
  <div class="mt-12 pt-8 border-t border-border">
    <h3 class="text-lg font-semibold text-text mb-6">评论</h3>
    <div ref="giscusContainer" />
  </div>
</template>

<script setup lang="ts">
const giscusContainer = ref<HTMLElement>()
const config = useRuntimeConfig()

onMounted(() => {
  if (!giscusContainer.value) return
  
  const script = document.createElement('script')
  script.src = 'https://giscus.app/client.js'
  script.setAttribute('data-repo', config.public.giscusRepo as string)
  script.setAttribute('data-repo-id', config.public.giscusRepoId as string)
  script.setAttribute('data-category', config.public.giscusCategory as string)
  script.setAttribute('data-category-id', config.public.giscusCategoryId as string)
  script.setAttribute('data-mapping', 'pathname')
  script.setAttribute('data-strict', '0')
  script.setAttribute('data-reactions-enabled', '1')
  script.setAttribute('data-emit-metadata', '0')
  script.setAttribute('data-input-position', 'bottom')
  script.setAttribute('data-theme', 'preferred_color_scheme')
  script.setAttribute('data-lang', 'zh-CN')
  script.setAttribute('data-loading', 'lazy')
  script.setAttribute('crossorigin', 'anonymous')
  script.async = true
  
  giscusContainer.value.appendChild(script)
})
</script>
