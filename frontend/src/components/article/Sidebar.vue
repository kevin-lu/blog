<template>
  <div class="sidebar">
    <!-- Profile Card -->
    <n-card class="profile-card" content-style="padding: 24px;">
      <div class="profile-content">
        <div class="avatar">
          <n-avatar
            :src="siteSettings.site_avatar"
            fallback-src="/default-avatar.png"
            round
            size="large"
          >
            <template #icon>
              <n-icon :component="PersonOutline" />
            </template>
          </n-avatar>
        </div>

        <h3 class="site-name">{{ siteSettings.site_name }}</h3>
        <p class="site-description">{{ siteSettings.site_description }}</p>

        <div class="social-links">
          <a
            v-if="siteSettings.github_url"
            :href="siteSettings.github_url"
            target="_blank"
            class="social-link"
          >
            <n-icon :component="LogoGithub" size="20" />
          </a>
          <a
            v-if="siteSettings.twitter_url"
            :href="siteSettings.twitter_url"
            target="_blank"
            class="social-link"
          >
            <n-icon :component="LogoTwitter" size="20" />
          </a>
          <a
            v-if="siteSettings.email"
            :href="`mailto:${siteSettings.email}`"
            class="social-link"
          >
            <n-icon :component="MailOutline" size="20" />
          </a>
        </div>
      </div>
    </n-card>

    <!-- Categories -->
    <n-card class="categories-card" title="分类" content-style="padding: 16px;">
      <div class="category-list">
        <div
          v-for="category in categories"
          :key="category.id"
          class="category-item"
          :class="{ active: activeCategory === category.slug }"
          @click="goToCategory(category.slug)"
        >
          <span class="category-name">{{ category.name }}</span>
          <n-tag :bordered="false" size="small" type="info">
            {{ category.article_count || 0 }}
          </n-tag>
        </div>
      </div>
    </n-card>

    <!-- Donation Card -->
    <DonationCard />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  PersonOutline,
  LogoGithub,
  LogoTwitter,
  MailOutline,
} from '@vicons/ionicons5'
import type { Category } from '@/types'
import { categoryApi, settingApi } from '@/api'
import DonationCard from '@/components/donation/DonationCard.vue'
import { resolveServerAssetUrl } from '@/utils/assets'

const router = useRouter()
const route = useRoute()

const categories = ref<Category[]>([])

const siteSettings = ref({
  site_name: '我的博客',
  site_description: '技术分享平台',
  site_avatar: '',
  github_url: '',
  twitter_url: '',
  email: '',
})

const activeCategory = ref('')

const goToCategory = (slug: string) => {
  router.push(`/categories/${slug}`)
}

onMounted(async () => {
  // Load site settings
  try {
    const response = await settingApi.get()
    const settings = response.settings
    console.log('[Sidebar] Raw settings:', settings)
    siteSettings.value = {
      site_name: settings.site_name || '我的博客',
      site_description: settings.site_description || '技术分享平台',
      site_avatar: resolveServerAssetUrl(settings.site_avatar || ''),
      github_url: settings.github_url || '',
      twitter_url: settings.twitter_url || '',
      email: settings.email || '',
    }
    console.log('[Sidebar] Processed settings:', siteSettings.value)
  } catch (error) {
    console.error('Failed to load site settings:', error)
  }

  // Load categories
  try {
    const response = await categoryApi.getList()
    categories.value = response.data
  } catch (error) {
    console.error('Failed to load categories:', error)
  }

  // Set active from route
  if (route.params.name && route.path.includes('/categories/')) {
    activeCategory.value = route.params.name as string
  }
})
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card,
.categories-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(24, 160, 88, 0.1);
  border: 1px solid rgba(24, 160, 88, 0.05);
}

.profile-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
}

.avatar {
  margin-bottom: 8px;
}

.site-name {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  background: linear-gradient(135deg, #18a058 0%, #0c7a43 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.site-description {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.social-links {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #f5f5f5;
  color: #666;
  transition: all 0.2s;
  text-decoration: none;
}

.social-link:hover {
  background-color: #18a058;
  color: white;
}

.categories-card :deep(.n-card__header) {
  font-size: 18px;
  font-weight: 600;
  color: #18a058;
  padding: 16px 20px !important;
  border-bottom: 2px solid rgba(24, 160, 88, 0.1);
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.category-item:hover {
  background: rgba(24, 160, 88, 0.08);
}

.category-item.active {
  background: rgba(24, 160, 88, 0.12);
}

.category-name {
  font-size: 14px;
  color: #333;
}
</style>
