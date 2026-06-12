<template>
  <section class="hero-section" ref="sectionRef">
    <HeroBackground />
    <HeroParticles />
    <HeroContent />
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as anime from 'animejs';
import HeroBackground from './HeroBackground.vue';
import HeroParticles from './HeroParticles.vue';
import HeroContent from './HeroContent.vue';

const sectionRef = ref<HTMLElement | null>(null);

const playEntranceAnimation = () => {
  const tl = anime.timeline({
    easing: 'easeOutExpo',
    duration: 1000
  });

  tl
    .add({
      targets: '.hero-section',
      opacity: [0, 1],
      duration: 1000
    })
    .add(
      {
        targets: '.hero-title',
        opacity: [0, 1],
        rotateX: [90, 0],
        rotateY: [180, 0],
        duration: 2000
      },
      '-=200'
    )
    .add(
      {
        targets: '.hero-slogan',
        opacity: [0, 1],
        translateY: [50, 0],
        duration: 1500
      },
      '-=500'
    )
    .add(
      {
        targets: '.hero-cta',
        opacity: [0, 1],
        scale: [0.8, 1],
        duration: 1000
      },
      '-=500'
    );

  setTimeout(() => {
    startContinuousAnimation();
  }, 2000);
};

const startContinuousAnimation = () => {
  const titleElement = document.querySelector('.hero-title');
  if (titleElement) {
    anime({
      targets: titleElement,
      translateY: [0, -10, 0],
      rotateX: [0, 5, 0],
      duration: 6000,
      easing: 'easeInOutSine',
      loop: true
    });
  }
};

onMounted(() => {
  playEntranceAnimation();
});
</script>

<style scoped>
.hero-section {
  position: relative;
  width: 100%;
  height: 600px;
  background: linear-gradient(
    180deg,
    var(--hero-gradient-start) 0%,
    var(--hero-gradient-middle) 50%,
    var(--hero-gradient-end) 100%
  );
  overflow: hidden;
}

@media (max-width: 768px) {
  .hero-section {
    height: 400px;
  }
}
</style>
