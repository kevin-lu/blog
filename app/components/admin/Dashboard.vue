<template>
  <div class="dashboard">
    <n-grid :cols="4" :x-gap="24" :y-gap="24">
      <!-- 统计卡片 -->
      <n-grid-item>
        <n-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon articles">
              <n-icon :component="FileTextOutlined" size="32" />
            </div>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">文章总数</div>
            </div>
          </div>
        </n-card>
      </n-grid-item>

      <n-grid-item>
        <n-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon categories">
              <n-icon :component="TagsOutlined" size="32" />
            </div>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">分类数量</div>
            </div>
          </div>
        </n-card>
      </n-grid-item>

      <n-grid-item>
        <n-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon comments">
              <n-icon :component="MessageOutlined" size="32" />
            </div>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">评论数量</div>
            </div>
          </div>
        </n-card>
      </n-grid-item>

      <n-grid-item>
        <n-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon views">
              <n-icon :component="EyeOutlined" size="32" />
            </div>
            <div class="stat-info">
              <div class="stat-value">0</div>
              <div class="stat-label">总浏览量</div>
            </div>
          </div>
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 快捷操作 -->
    <n-card title="快捷操作" class="mt-6">
      <n-space>
        <n-button type="primary" @click="router.push('/admin/articles/create')">
          <template #icon>
            <n-icon :component="PlusOutlined" />
          </template>
          新建文章
        </n-button>
        <n-button @click="router.push('/admin/comments')">
          <template #icon>
            <n-icon :component="MessageOutlined" />
          </template>
          查看评论
        </n-button>
        <n-button @click="router.push('/admin/settings')">
          <template #icon>
            <n-icon :component="SettingOutlined" />
          </template>
          站点配置
        </n-button>
      </n-space>
    </n-card>

    <!-- 最近文章 -->
    <n-card title="最近文章" class="mt-6">
      <n-empty description="暂无文章" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue';
import { useRouter } from 'vue-router';
import {
  FileTextOutlined,
  TagsOutlined,
  MessageOutlined,
  SettingOutlined,
  PlusOutlined,
  EyeOutlined,
} from '@vicons/antd';

const router = useRouter();
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
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
  color: #fff;
}

.stat-icon.articles {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.categories {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.comments {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.views {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

.mt-6 {
  margin-top: 24px;
}
</style>
