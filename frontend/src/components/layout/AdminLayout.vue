<template>
  <n-layout class="layout" has-sider>
    <n-layout-sider
      class="sider"
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="240"
      :native-scrollbar="false"
    >
      <div class="logo">
        <h1 v-if="!collapsed">博客管理</h1>
        <n-icon v-else :component="MenuOutline" size="24" />
      </div>

      <n-menu
        class="menu"
        :options="menuOptions"
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="22"
        :value="activeKey"
        @update:value="handleMenuSelect"
      />
    </n-layout-sider>

    <n-layout class="main-content">
      <n-layout-header class="header" bordered>
        <div class="header-left">
          <n-button
            text
            @click="toggleCollapsed"
          >
            <template #icon>
              <n-icon :component="collapsed ? MenuOutline : CloseOutline" size="20" />
            </template>
          </n-button>
        </div>

        <div class="header-right">
          <n-badge :value="notificationCount" :show="notificationCount > 0">
            <n-button text>
              <template #icon>
                <n-icon :component="NotificationsOutline" size="20" />
              </template>
            </n-button>
          </n-badge>

          <UserInfo />
        </div>
      </n-layout-header>

      <n-layout-content class="content">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { MenuOption } from 'naive-ui'
import {
  MenuOutline,
  CloseOutline,
  NotificationsOutline,
  HomeOutline,
  DocumentTextOutline,
  GridOutline,
  BookmarksOutline,
  ChatbubbleOutline,
  SettingsOutline,
  SparklesOutline,
} from '@vicons/ionicons5'
import UserInfo from '@/components/common/UserInfo.vue'

const router = useRouter()
const route = useRoute()

const collapsed = ref(false)
const notificationCount = ref(0)

const activeKey = computed(() => route.name as string)

const renderIcon = (icon: any) => {
  return () => h('div', { style: 'display: flex; align-items: center;' }, [h(icon)])
}

const menuOptions: MenuOption[] = [
  {
    label: '仪表盘',
    key: 'admin',
    icon: renderIcon(HomeOutline),
  },
  {
    label: '文章管理',
    key: 'admin-articles',
    icon: renderIcon(DocumentTextOutline),
  },
  {
    label: 'AI 改写',
    key: 'admin-ai-generator',
    icon: renderIcon(SparklesOutline),
  },
  {
    label: '分类管理',
    key: 'admin-categories',
    icon: renderIcon(GridOutline),
  },
  {
    label: '标签管理',
    key: 'admin-tags',
    icon: renderIcon(BookmarksOutline),
  },
  {
    label: '评论管理',
    key: 'admin-comments',
    icon: renderIcon(ChatbubbleOutline),
  },
  {
    label: '站点设置',
    key: 'admin-settings',
    icon: renderIcon(SettingsOutline),
  },
]

const toggleCollapsed = () => {
  collapsed.value = !collapsed.value
}

const handleMenuSelect = (key: string) => {
  router.push(`/admin${key === 'admin' ? '' : `/${key.replace('admin-', '')}`}`)
}
</script>

<style scoped>
.layout {
  min-height: 100vh;
}

.sider {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 64px;
  padding: 0 20px;
  border-bottom: 1px solid #f0f0f0;
}

.logo h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
}

.menu {
  margin-top: 16px;
}

.main-content {
  margin-left: 240px;
  transition: margin-left 0.2s;
}

:deep(.n-layout-sider.collapsed) ~ .main-content {
  margin-left: 64px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 24px;
  background: white;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.content {
  padding: 24px;
  background: #f5f5f5;
  min-height: calc(100vh - 64px - 64px);
}
</style>
