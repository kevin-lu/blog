<template>
  <div class="admin-layout">
    <n-layout has-sider class="admin-layout-container">
      <!-- 侧边栏 -->
      <n-layout-sider
        bordered
        collapse-mode="width"
        :collapsed-width="64"
        :width="240"
        class="admin-sidebar"
      >
        <div class="sidebar-header">
          <h2 v-if="!collapsed" class="sidebar-title">博客管理</h2>
          <h2 v-else class="sidebar-title-short">博客</h2>
        </div>
        
        <n-menu
          :options="menuOptions"
          :collapsed="collapsed"
          :collapsed-width="64"
          :collapsed-icon-size="22"
          :default-value="route.path"
          @update:value="handleMenuClick"
        />
      </n-layout-sider>

      <!-- 主内容区 -->
      <n-layout class="admin-main">
        <!-- 顶部导航 -->
        <n-layout-header bordered class="admin-header">
          <div class="header-left">
            <n-button text @click="collapsed = !collapsed">
              <template #icon>
                <n-icon :component="MenuUnfoldOutlined" v-if="collapsed" />
                <n-icon :component="MenuFoldOutlined" v-else />
              </template>
            </n-button>
          </div>
          
          <div class="header-right">
            <n-dropdown :options="userMenuOptions" @select="handleUserMenu">
              <n-button text class="user-info">
                <template #icon>
                  <n-icon :component="UserOutlined" />
                </template>
                {{ adminStore.currentUser?.username }}
              </n-button>
            </n-dropdown>
          </div>
        </n-layout-header>

        <!-- 内容区 -->
        <n-layout-content class="admin-content">
          <slot />
        </n-layout-content>
      </n-layout>
    </n-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  FileTextOutlined,
  TagsOutlined,
  MessageOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@vicons/antd';
import type { MenuOption } from 'naive-ui';
import { useAdminStore } from '~/stores/admin';
import { useAuth } from '~/composables/useAuth';

const router = useRouter();
const route = useRoute();
const adminStore = useAdminStore();
const { logout } = useAuth();

const collapsed = ref(false);

// 菜单选项
const menuOptions = computed<MenuOption[]>(() => [
  {
    label: '仪表盘',
    key: '/admin/dashboard',
    icon: () => h(DashboardOutlined),
  },
  {
    label: '文章管理',
    key: '/admin/articles',
    icon: () => h(FileTextOutlined),
  },
  {
    label: '分类标签',
    key: '/admin/categories',
    icon: () => h(TagsOutlined),
  },
  {
    label: '评论管理',
    key: '/admin/comments',
    icon: () => h(MessageOutlined),
  },
  {
    label: '站点配置',
    key: '/admin/settings',
    icon: () => h(SettingOutlined),
  },
]);

// 用户菜单选项
const userMenuOptions = computed<MenuOption[]>(() => [
  {
    label: '退出登录',
    key: 'logout',
    icon: () => h(LogoutOutlined),
  },
]);

const handleMenuClick = (key: string) => {
  router.push(key);
};

const handleUserMenu = (key: string) => {
  if (key === 'logout') {
    logout();
  }
};
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  overflow: hidden;
}

.admin-layout-container {
  height: 100%;
}

.admin-sidebar {
  background-color: #001529;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-title {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.sidebar-title-short {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.admin-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  background-color: #fff;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  font-size: 14px;
}

.admin-content {
  padding: 24px;
  background-color: #f0f2f5;
}
</style>
