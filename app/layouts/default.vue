<template>
  <div class="min-h-screen flex flex-col bg-white">
    <AppHeader />
    <div class="flex-1">
      <div class="max-w-6xl mx-auto px-6 py-8 flex gap-8">
        <!-- 主内容区 -->
        <main class="flex-1 min-w-0">
          <slot />
        </main>
        
        <!-- 右侧边栏 -->
        <aside class="w-72 flex-shrink-0 hidden lg:block">
          <!-- 推广卡片 -->
          <div class="bg-gray-50 rounded-xl p-4 mb-6">
            <h3 class="text-sm font-medium text-gray-400 mb-3">推荐</h3>
            
            <a
              href="https://api.ssopen.top/"
              target="_blank"
              class="block p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
            >
              <div class="text-xs text-gray-500 mb-1">广告</div>
              <div class="font-medium text-gray-900">API中转站</div>
              <div class="text-xs text-gray-500 mt-1">580+ AI大模型 · 0.95一刀</div>
            </a>
          </div>
          
          <!-- 关于卡片 -->
          <div class="bg-gray-50 rounded-xl p-4">
            <h3 class="text-sm font-medium text-gray-400 mb-3">关于</h3>
            <p class="text-sm text-gray-600">
              专注技术内容分享，探索 AI 与开发前沿，记录每一个值得关注的开源项目。
            </p>
          </div>
        </aside>
      </div>
    </div>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
// 初始化主题
onMounted(() => {
  useTheme().initTheme()
})
</script>