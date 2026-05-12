<template>
  <div class="blog-layout">
    <header class="header">
      <div class="container">
        <div class="header-left">
        <router-link to="/" class="logo">
          <h1>{{ siteName }}</h1>
        </router-link>

        <!-- Desktop Nav -->
        <nav class="nav desktop-nav">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/categories" class="nav-link">分类</router-link>
          <router-link to="/tags" class="nav-link">标签</router-link>
          <router-link to="/about" class="nav-link">关于</router-link>
        </nav>

        <!-- Mobile Menu Button -->
        <n-button class="mobile-menu-btn" text @click="toggleMobileMenu">
          <template #icon>
            <n-icon :component="menuOpen ? CloseOutline : MenuOutline" size="24" />
          </template>
        </n-button>
      </div>
      </div>

      <!-- Mobile Nav -->
      <transition name="slide-down">
        <nav v-if="menuOpen" class="mobile-nav">
          <router-link to="/" class="nav-link" @click="menuOpen = false">首页</router-link>
          <router-link to="/categories" class="nav-link" @click="menuOpen = false">分类</router-link>
          <router-link to="/tags" class="nav-link" @click="menuOpen = false">标签</router-link>
          <router-link to="/about" class="nav-link" @click="menuOpen = false">关于</router-link>
        </nav>
      </transition>
    </header>

    <main class="main">
      <router-view />
    </main>

    <footer class="footer">
      <div class="container">
        <p>© 2026 {{ siteName }}. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { MenuOutline, CloseOutline } from '@vicons/ionicons5'

const menuOpen = ref(false)
const siteName = computed(() => '老卢的博客')

const toggleMobileMenu = () => {
  menuOpen.value = !menuOpen.value
}
</script>

<style scoped>
.blog-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(24, 160, 88, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header {
  height: 64px;
  display: flex;
  align-items: center;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header-left {
  width: 100%;
}

.header-right {
  display: none;
}

.logo {
  text-decoration: none;
  color: inherit;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #18a058 0%, #0c7a43 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Desktop Nav */
.desktop-nav {
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }
}

.nav-link {
  padding: 8px 16px;
  text-decoration: none;
  color: #333;
  border-radius: 6px;
  transition: all 0.2s;
  white-space: nowrap;
  position: relative;
}

.nav-link:hover {
  background-color: rgba(24, 160, 88, 0.08);
  color: #18a058;
}

.nav-link.router-link-active {
  background: linear-gradient(135deg, #18a058 0%, #0c7a43 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(24, 160, 88, 0.3);
}

/* Mobile Menu Button */
.mobile-menu-btn {
  display: none;
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
  }
}

/* Mobile Nav */
.mobile-nav {
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #f0f0f0;
  gap: 8px;
}

.mobile-nav .nav-link {
  padding: 12px 16px;
  border-radius: 8px;
}

/* Slide Down Transition */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.main {
  flex: 1;
  padding: 24px 0;
}

@media (max-width: 768px) {
  .main {
    padding: 16px 0;
  }
}

.footer {
  background: #f5f5f5;
  padding: 24px 0;
  text-align: center;
  color: #666;
}

.footer p {
  margin: 0;
  font-size: 14px;
}

@media (max-width: 768px) {
  .footer {
    padding: 16px 0;
  }
}
</style>
