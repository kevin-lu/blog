<template>
  <div class="hero-content">
    <h1 class="hero-title">{{ config.title }}</h1>
    <p class="hero-slogan">{{ config.slogan }}</p>
    <button class="hero-cta" @click="scrollToArticles">
      {{ config.ctaText }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface HeroConfig {
  title: string;
  slogan: string;
  ctaText: string;
  ctaTarget: string;
}

const config = ref<HeroConfig>({
  title: '我的技术博客',
  slogan: '探索技术深度 · 分享创新思维',
  ctaText: '开始阅读',
  ctaTarget: '#article-list'
});

const scrollToArticles = () => {
  const target = document.querySelector(config.value.ctaTarget);
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};
</script>

<style scoped>
.hero-content {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 0 20px;
}

.hero-title {
  font-size: 4rem;
  font-weight: 700;
  color: var(--hero-text-primary);
  margin-bottom: 1.5rem;
  text-shadow: 0 0 20px var(--hero-accent-glow);
  transform-style: preserve-3d;
  perspective: 1000px;
}

.hero-slogan {
  font-size: 1.5rem;
  color: var(--hero-text-secondary);
  margin-bottom: 2.5rem;
  max-width: 600px;
}

.hero-cta {
  padding: 1rem 2.5rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--hero-primary);
  background: var(--hero-text-primary);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
}

.hero-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 255, 136, 0.4);
}

.hero-cta:active {
  transform: translateY(0);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-slogan {
    font-size: 1.125rem;
  }

  .hero-cta {
    padding: 0.875rem 2rem;
    font-size: 1rem;
  }
}
</style>
