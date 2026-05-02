<template>
  <header class="sticky top-0 z-50 bg-white border-b border-gray-200">
    <div class="max-w-4xl mx-auto px-6 h-14 flex items-center justify-between">
      <!-- Logo -->
      <NuxtLink to="/" class="flex items-center gap-2 text-gray-900 hover:opacity-70 transition-opacity">
        <span class="font-bold text-lg">我的博客</span>
      </NuxtLink>

      <!-- 导航 -->
      <nav class="flex items-center gap-1">
        <NuxtLink
          to="/"
          class="px-3 py-1.5 text-sm font-medium text-gray-600 rounded-lg hover:text-gray-900 hover:bg-gray-50 transition-all"
          :class="{ 'bg-gray-100 text-gray-900': route.path === '/' }"
        >
          首页
        </NuxtLink>
        <NuxtLink
          to="/categories"
          class="px-3 py-1.5 text-sm font-medium text-gray-600 rounded-lg hover:text-gray-900 hover:bg-gray-50 transition-all"
          :class="{ 'bg-gray-100 text-gray-900': route.path.startsWith('/categories') }"
        >
          分类
        </NuxtLink>
        <NuxtLink
          to="/about"
          class="px-3 py-1.5 text-sm font-medium text-gray-600 rounded-lg hover:text-gray-900 hover:bg-gray-50 transition-all"
          :class="{ 'bg-gray-100 text-gray-900': route.path === '/about' }"
        >
          关于
        </NuxtLink>
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
const route = useRoute()
</script>