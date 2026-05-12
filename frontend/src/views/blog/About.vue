<template>
  <div class="about-page">
    <div class="page-header">
      <h1>关于</h1>
    </div>

    <n-card class="about-content" v-if="loading">
      <n-spin size="large" description="加载中..." />
    </n-card>

    <n-card class="about-content" v-else-if="settings">
      <!-- Welcome Section -->
      <div class="about-section" v-if="settings.about_welcome_title || settings.about_welcome_content">
        <h2>{{ settings.about_welcome_title }}</h2>
        <p>{{ settings.about_welcome_content }}</p>
      </div>

      <!-- About Author Section -->
      <div class="about-section" v-if="settings.about_author_title || settings.about_author_content">
        <h2>{{ settings.about_author_title }}</h2>
        <p>{{ settings.about_author_content }}</p>
      </div>

      <!-- Tech Stack Section -->
      <div class="about-section" v-if="settings.about_tech_stack_title && settings.about_tech_stack_items?.length">
        <h2>{{ settings.about_tech_stack_title }}</h2>
        <div class="tech-stack">
          <n-tag v-for="tech in settings.about_tech_stack_items" :key="tech" :bordered="false">
            {{ tech }}
          </n-tag>
        </div>
      </div>

      <!-- Contact Section -->
      <div class="about-section" v-if="settings.about_contact_title && (settings.about_contact_email || settings.about_contact_github)">
        <h2>{{ settings.about_contact_title }}</h2>
        <div class="contact-info">
          <p v-if="settings.about_contact_email">
            <n-icon :component="MailOutline" />
            邮箱：{{ settings.about_contact_email }}
          </p>
          <p v-if="settings.about_contact_github">
            <n-icon :component="LogoGithub" />
            {{ settings.about_contact_github_label || 'GitHub' }}:
            <a :href="settings.about_contact_github" target="_blank" rel="noopener noreferrer">
              {{ settings.about_contact_github.replace(/^https?:\/\//, '') }}
            </a>
          </p>
        </div>
      </div>
    </n-card>

    <n-card class="about-content" v-else>
      <div class="empty-state">
        <n-empty description="暂无内容" />
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { MailOutline, LogoGithub } from '@vicons/ionicons5'
import { settingApi } from '@/api/setting'

const loading = ref(true)
const settings = ref<any>(null)

const loadSettings = async () => {
  try {
    loading.value = true
    const response = await settingApi.get()
    settings.value = response.settings
  } catch (error) {
    console.error('Failed to load about page settings:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSettings()
})
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

.empty-state {
  padding: 60px 0;
  text-align: center;
}
</style>
