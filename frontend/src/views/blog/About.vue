<template>
  <div class="about-page">
    <div class="page-header">
      <h1>关于</h1>
    </div>

    <n-card class="about-content">
      <div class="about-section">
        <h2>欢迎来到我的博客</h2>
        <p>
          这是一个技术分享平台，主要记录我在学习和工作中的技术心得和经验总结。
          希望通过这个平台，能够帮助到更多正在学习技术的朋友们。
        </p>
      </div>

      <div class="about-section">
        <h2>关于博主</h2>
        <p>
          一名热爱技术的开发者，专注于 Web 开发领域。
          喜欢探索新技术，分享技术文章，参与开源项目。
        </p>
      </div>

      <div class="about-section">
        <h2>技术栈</h2>
        <div class="tech-stack">
          <n-tag v-for="tech in techStack" :key="tech" :bordered="false">
            {{ tech }}
          </n-tag>
        </div>
      </div>

      <div class="about-section">
        <h2>联系方式</h2>
        <div class="contact-info">
          <p>
            <n-icon :component="MailOutline" />
            邮箱：example@email.com
          </p>
          <p>
            <n-icon :component="LogoGithub" />
            GitHub:
            <a href="https://github.com" target="_blank">github.com</a>
          </p>
        </div>
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { MailOutline, LogoGithub } from '@vicons/ionicons5'

const techStack = [
  'Vue.js',
  'React',
  'TypeScript',
  'Node.js',
  'Python',
  'Go',
  'Docker',
  'Kubernetes',
]
</script>

<style scoped>
.about-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 0;
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-header h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
}

.about-content {
  border-radius: 12px;
}

.about-section {
  margin-bottom: 32px;
}

.about-section:last-child {
  margin-bottom: 0;
}

.about-section h2 {
  margin: 0 0 16px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.about-section p {
  margin: 0;
  font-size: 15px;
  color: #666;
  line-height: 1.8;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.contact-info p {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.contact-info p:last-child {
  margin-bottom: 0;
}

.contact-info a {
  color: #18a058;
  text-decoration: none;
}

.contact-info a:hover {
  text-decoration: underline;
}
</style>
