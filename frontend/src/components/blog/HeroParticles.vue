<template>
  <canvas ref="canvasRef" class="hero-particles"></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const canvasRef = ref<HTMLCanvasElement | null>(null);
let animationFrameId: number | null = null;
let particles: Particle[] = [];

class Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  alpha: number;

  constructor(x: number, y: number, vx: number, vy: number, radius: number) {
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.radius = radius;
    this.alpha = Math.random() * 0.5 + 0.5;
  }

  update(width: number, height: number) {
    this.x += this.vx;
    this.y += this.vy;

    if (this.x < 0 || this.x > width) this.vx *= -1;
    if (this.y < 0 || this.y > height) this.vy *= -1;

    this.alpha += (Math.random() - 0.5) * 0.02;
    this.alpha = Math.max(0.3, Math.min(1, this.alpha));
  }

  draw(ctx: CanvasRenderingContext2D) {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(0, 255, 136, ${this.alpha})`;
    ctx.fill();
  }
}

const createParticles = (width: number, height: number): Particle[] => {
  const particleCount = width > 768 ? 80 : 40;
  const newParticles: Particle[] = [];

  for (let i = 0; i < particleCount; i++) {
    const x = Math.random() * width;
    const y = Math.random() * height;
    const vx = (Math.random() - 0.5) * 0.5;
    const vy = (Math.random() - 0.5) * 0.5;
    const radius = Math.random() * 2 + 1;
    newParticles.push(new Particle(x, y, vx, vy, radius));
  }

  return newParticles;
};

const drawConnections = (
  ctx: CanvasRenderingContext2D,
  particles: Particle[]
) => {
  for (let i = 0; i < particles.length; i++) {
    for (let j = i + 1; j < particles.length; j++) {
      const dx = particles[i].x - particles[j].x;
      const dy = particles[i].y - particles[j].y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < 150) {
        const alpha = (1 - distance / 150) * 0.5;
        ctx.strokeStyle = `rgba(0, 255, 136, ${alpha})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(particles[i].x, particles[i].y);
        ctx.lineTo(particles[j].x, particles[j].y);
        ctx.stroke();
      }
    }
  }
};

const animate = () => {
  if (!canvasRef.value) return;

  const canvas = canvasRef.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const width = canvas.width;
  const height = canvas.height;

  ctx.clearRect(0, 0, width, height);

  particles.forEach((particle) => {
    particle.update(width, height);
    particle.draw(ctx);
  });

  drawConnections(ctx, particles);

  animationFrameId = requestAnimationFrame(animate);
};

const resizeCanvas = () => {
  if (!canvasRef.value) return;

  const canvas = canvasRef.value;
  const parent = canvas.parentElement;
  if (!parent) return;

  canvas.width = parent.clientWidth;
  canvas.height = parent.clientHeight;

  particles = createParticles(canvas.width, canvas.height);
};

onMounted(() => {
  resizeCanvas();
  animate();

  window.addEventListener('resize', resizeCanvas);
});

onUnmounted(() => {
  if (animationFrameId !== null) {
    cancelAnimationFrame(animationFrameId);
  }
  window.removeEventListener('resize', resizeCanvas);
});
</script>

<style scoped>
.hero-particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
}
</style>
