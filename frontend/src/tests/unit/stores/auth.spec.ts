import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia } from 'pinia'
import { createTestingPinia } from '@pinia/testing'
import { useAuthStore } from '@/stores/auth'
import type { User } from '@/types'

describe('AuthStore', () => {
  let authStore: ReturnType<typeof useAuthStore>

  beforeEach(() => {
    setActivePinia(
      createTestingPinia({
        createSpy: vi.fn,
        stubActions: false,
      })
    )
    authStore = useAuthStore()
  })

  describe('初始状态', () => {
    it('应该初始化为未登录状态', () => {
      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.user).toBeNull()
      expect(authStore.accessToken).toBe('')
    })
  })

  describe('setTokens', () => {
    it('应该正确设置访问令牌和刷新令牌', () => {
      const accessToken = 'test-access-token'
      const refreshToken = 'test-refresh-token'
      authStore.setTokens(accessToken, refreshToken)

      expect(authStore.accessToken).toBe(accessToken)
      expect(authStore.refreshToken).toBe(refreshToken)
    })
  })

  describe('setUser', () => {
    it('应该正确设置用户信息', () => {
      const userInfo: User = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        avatar: null,
        role: 'admin',
        created_at: '2024-01-01T00:00:00Z',
      }

      authStore.setUser(userInfo)

      expect(authStore.user).toEqual(userInfo)
    })
  })

  describe('logout', () => {
    it('应该清除所有用户数据和令牌', () => {
      const userInfo: User = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        avatar: null,
        role: 'admin',
        created_at: '2024-01-01T00:00:00Z',
      }

      authStore.setUser(userInfo)
      authStore.setTokens('access-token', 'refresh-token')

      authStore.logout()

      expect(authStore.isAuthenticated).toBe(false)
      expect(authStore.user).toBeNull()
      expect(authStore.accessToken).toBe('')
      expect(authStore.refreshToken).toBe('')
    })
  })

  describe('从本地存储恢复', () => {
    it('应该从 localStorage 恢复令牌', () => {
      const token = 'stored-token'
      localStorage.setItem('access_token', token)

      setActivePinia(
        createTestingPinia({
          createSpy: vi.fn,
          stubActions: false,
        })
      )
      const newStore = useAuthStore()

      expect(newStore.accessToken).toBe(token)
      localStorage.removeItem('access_token')
    })
  })
})
