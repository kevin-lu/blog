import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string>(localStorage.getItem('access_token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refresh_token') || '')
  const loading = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value)

  async function initAuth() {
    if (!accessToken.value) return

    loading.value = true
    try {
      const response = await authApi.getCurrentUser()
      user.value = response.user
    } catch (error) {
      console.error('Failed to get current user:', error)
      logout()
    } finally {
      loading.value = false
    }
  }

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function setUser(userData: User) {
    user.value = userData
  }

  function logout() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    loading,
    setTokens,
    setUser,
    logout,
    initAuth,
  }
})
