<template>
  <div class="sidebar">
    <!-- Profile Card -->
    <n-card class="profile-card" content-style="padding: 24px;">
      <div class="profile-content">
        <div class="avatar">
          <n-avatar
            :src="siteSettings.avatar"
            fallback-src="/default-avatar.png"
            round
            size="large"
          >
            <template #icon>
              <n-icon :component="PersonOutline" />
            </template>
          </n-avatar>
        </div>

        <h3 class="site-name">{{ siteSettings.name }}</h3>
        <p class="site-description">{{ siteSettings.description }}</p>

        <div class="social-links">
          <a
            v-if="siteSettings.github"
            :href="siteSettings.github"
            target="_blank"
            class="social-link"
          >
            <n-icon :component="LogoGithub" size="20" />
          </a>
          <a
            v-if="siteSettings.twitter"
            :href="siteSettings.twitter"
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

    <!-- Tags -->
    <n-card class="tags-card" title="标签" content-style="padding: 16px;">
      <div class="tag-cloud">
        <n-tag
          v-for="tag in tags"
          :key="tag.id"
          :bordered="false"
          round
          checkable
          :checked="activeTag === tag.slug"
          @click="goToTag(tag.slug)"
        >
          {{ tag.name }}
        </n-tag>
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
import type { Category, Tag } from '@/types'
import { categoryApi, tagApi } from '@/api'
import DonationCard from '@/components/donation/DonationCard.vue'

const router = useRouter()
const route = useRoute()

const categories = ref<Category[]>([])
const tags = ref<Tag[]>([])

const siteSettings = ref({
  name: '我的博客',
  description: '记录技术，分享生活',
  avatar: '',
  github: '',
  twitter: '',
  email: '',
})

const activeCategory = ref('')
const activeTag = ref('')

const goToCategory = (slug: string) => {
  router.push(`/categories/${slug}`)
}

const goToTag = (slug: string) => {
  router.push(`/tags/${slug}`)
}

onMounted(async () => {
  // Load categories
  try {
    const response = await categoryApi.getList()
    categories.value = response.data
  } catch (error) {
    console.error('Failed to load categories:', error)
  }

  // Load tags
  try {
    const response = await tagApi.getList()
    tags.value = response.data
  } catch (error) {
    console.error('Failed to load tags:', error)
  }

  // Set active from route
  if (route.params.name && route.path.includes('/categories/')) {
    activeCategory.value = route.params.name as string
  }
  if (route.params.name && route.path.includes('/tags/')) {
    activeTag.value = route.params.name as string
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
.categories-card,
.tags-card {
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

.categories-card :deep(.n-card__header),
.tags-card :deep(.n-card__header) {
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

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-cloud .n-tag {
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(24, 160, 88, 0.08);
  color: #18a058;
}

.tag-cloud .n-tag:hover {
  transform: scale(1.05);
  background: rgba(24, 160, 88, 0.15);
}

.tag-cloud .n-tag.n-tag--checked {
  background: #18a058;
  color: white;
}
</style>
