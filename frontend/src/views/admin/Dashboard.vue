<template>
  <div class="dashboard-page">
    <div class="page-header">
      <div class="header-left">
        <h1>仪表盘</h1>
        <p>欢迎回来，{{ adminName }}</p>
      </div>
    </div>

    <n-grid :cols="4" :x-gap="24" :y-gap="24">
      <!-- Stats Cards -->
      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-icon articles">
            <n-icon :component="DocumentTextOutline" size="32" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.articleCount }}</div>
            <div class="stat-label">文章总数</div>
          </div>
        </n-card>
      </n-gi>

      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-icon categories">
            <n-icon :component="FolderOutline" size="32" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.categoryCount }}</div>
            <div class="stat-label">分类数量</div>
          </div>
        </n-card>
      </n-gi>

      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-icon tags">
            <n-icon :component="BookmarksOutline" size="32" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.tagCount }}</div>
            <div class="stat-label">标签数量</div>
          </div>
        </n-card>
      </n-gi>

      <n-gi>
        <n-card class="stat-card" hoverable>
          <div class="stat-icon comments">
            <n-icon :component="ChatbubbleOutline" size="32" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.commentCount }}</div>
            <div class="stat-label">评论数量</div>
          </div>
        </n-card>
      </n-gi>
    </n-grid>

    <n-grid :cols="2" :x-gap="24" :y-gap="24" style="margin-top: 24px;">
      <!-- Recent Articles -->
      <n-gi>
        <n-card title="最近文章">
          <template #header-extra>
            <n-button text type="primary" @click="router.push('/admin/articles')">
              查看全部
            </n-button>
          </template>
          <n-list>
            <n-list-item
              v-for="article in recentArticles"
              :key="article.id"
            >
              <div class="article-item">
                <div class="article-info">
                  <div class="article-title">{{ article.title }}</div>
                  <div class="article-meta">
                    <span>{{ formatDate(article.created_at) }}</span>
                    <n-tag
                      :type="article.status === 'published' ? 'success' : 'warning'"
                      size="small"
                      bordered
                    >
                      {{ article.status === 'published' ? '已发布' : '草稿' }}
                    </n-tag>
                  </div>
                </div>
                <n-button text size="small" @click="router.push(`/admin/articles/edit/${article.slug}`)">
                  编辑
                </n-button>
              </div>
            </n-list-item>
          </n-list>
        </n-card>
      </n-gi>

      <!-- Recent Comments -->
      <n-gi>
        <n-card title="最近评论">
          <template #header-extra>
            <n-button text type="primary" @click="router.push('/admin/comments')">
              查看全部
            </n-button>
          </template>
          <n-list>
            <n-list-item
              v-for="comment in recentComments"
              :key="comment.id"
            >
              <div class="comment-item">
                <div class="comment-content">{{ comment.content }}</div>
                <div class="comment-meta">
                  <span>{{ comment.author_name }}</span>
                  <n-tag
                    :type="comment.status === 'approved' ? 'success' : 'warning'"
                    size="small"
                    bordered
                  >
                    {{ comment.status === 'approved' ? '已通过' : '待审核' }}
                  </n-tag>
                </div>
              </div>
            </n-list-item>
          </n-list>
        </n-card>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  DocumentTextOutline,
  FolderOutline,
  BookmarksOutline,
  ChatbubbleOutline,
} from '@vicons/ionicons5'
import { dashboardApi } from '@/api'

const router = useRouter()
const message = useMessage()

const adminName = ref('管理员')
const stats = ref({
  articleCount: 0,
  categoryCount: 0,
  tagCount: 0,
  commentCount: 0,
})
const recentArticles = ref<any[]>([])
const recentComments = ref<any[]>([])

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadDashboard = async () => {
  try {
    const response = await dashboardApi.getStats()
    stats.value = response.stats
    recentArticles.value = response.recent_articles || []
    recentComments.value = response.recent_comments || []
  } catch (error) {
    message.error('加载数据失败')
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.header-left h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-left p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.articles {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.categories {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.tags {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.comments {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.article-item,
.comment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.article-info {
  flex: 1;
}

.article-title {
  font-weight: 500;
  margin-bottom: 8px;
}

.article-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #999;
}

.comment-content {
  margin-bottom: 8px;
  font-size: 14px;
}

.comment-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #999;
}
</style>
