<template>
  <div class="min-h-screen flex flex-col bg-bg text-text">
    <AppHeader />
    <main class="flex-1">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
// 初始化主题
onMounted(() => {
  useTheme().initTheme()
})
</script>
