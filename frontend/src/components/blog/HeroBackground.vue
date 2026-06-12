<template>
  <canvas ref="canvasRef" class="hero-background"></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const canvasRef = ref<HTMLCanvasElement | null>(null);
let animationFrameId: number | null = null;
let offset = 0;

const drawGrid = (
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  offsetY: number
) => {
  const perspective = 0.5;
  const gridSize = 50;
  const speed = 0.5;

  ctx.clearRect(0, 0, width, height);

  // 绘制横向线条（有透视效果）
  for (let i = 0; i < height + gridSize; i += gridSize) {
    const y = (i + offsetY) % height;
    const alpha = 1 - (y / height);
    ctx.strokeStyle = `rgba(24, 160, 88, ${alpha * 0.6})`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }

  // 绘制纵向线条（汇聚到消失点）
  const centerX = width / 2;
  for (let i = -width; i < width * 2; i += gridSize) {
    const x = (i + offsetY * 0.3) % (width * 2) - width;
    const topX = centerX + (x - centerX) * perspective;
    const bottomX = x;
    
    ctx.strokeStyle = 'rgba(24, 160, 88, 0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(topX, 0);
    ctx.lineTo(bottomX, height);
    ctx.stroke();
  }
};

const animate = () => {
  if (!canvasRef.value) return;
  
  const canvas = canvasRef.value;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const width = canvas.width;
  const height = canvas.height;

  offset = (offset + 0.5) % 50;
  drawGrid(ctx, width, height, offset);

  animationFrameId = requestAnimationFrame(animate);
};

const resizeCanvas = () => {
  if (!canvasRef.value) return;
  
  const canvas = canvasRef.value;
  const parent = canvas.parentElement;
  if (!parent) return;

  canvas.width = parent.clientWidth;
  canvas.height = parent.clientHeight;
  
  const ctx = canvas.getContext('2d');
  if (ctx) {
    drawGrid(ctx, canvas.width, canvas.height, offset);
  }
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
.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}
</style>
