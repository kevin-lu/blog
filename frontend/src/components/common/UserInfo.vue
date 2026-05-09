<template>
  <div class="user-info">
    <n-dropdown
      :options="dropdownOptions"
      @select="handleSelect"
    >
      <div class="user-trigger">
        <n-avatar
          :src="user?.avatar"
          fallback-src="/default-avatar.png"
          round
          size="small"
        >
          <template #icon>
            <n-icon :component="PersonOutline" />
          </template>
        </n-avatar>
        <span class="username">{{ user?.username || '用户' }}</span>
        <n-icon :component="ChevronDownOutline" size="small" />
      </div>
    </n-dropdown>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { DropdownOption } from 'naive-ui'
import { PersonOutline, ChevronDownOutline, LogOutOutline, SettingsOutline } from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'
import { h } from 'vue'

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

const renderIcon = (icon: any) => {
  return () => h('div', { style: 'display: flex; align-items: center;' }, [h(icon)])
}

const dropdownOptions: DropdownOption[] = [
  {
    label: '个人设置',
    key: 'profile',
    icon: renderIcon(SettingsOutline),
  },
  {
    type: 'divider',
    key: 'd1',
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: renderIcon(LogOutOutline),
  },
]

const handleSelect = async (key: string) => {
  switch (key) {
    case 'profile':
      router.push('/admin/settings')
      break
    case 'logout':
      await handleLogout()
      break
  }
}

const handleLogout = async () => {
  try {
    await authApi.logout()
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    authStore.logout()
    message.success('已退出登录')
    router.push('/admin/login')
  }
}
</script>

<style scoped>
.user-info {
  display: flex;
  align-items: center;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-trigger:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.username {
  font-size: 14px;
  color: #333;
}

:deep(.n-avatar) {
  background-color: #18a058;
}
</style>
