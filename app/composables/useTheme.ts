import { useState, useCookie } from '#imports'

type Theme = 'light' | 'dark' | 'system'

export function useTheme() {
  const theme = useState<Theme>('theme', () => 'system')
  const isDark = useState<boolean>('isDark', () => false)
  const themeCookie = useCookie<Theme>('theme', {
    default: () => 'system',
    maxAge: 60 * 60 * 24 * 365, // 1 year
  })

  /**
   * 初始化主题
   */
  function initTheme() {
    const savedTheme = themeCookie.value || 'system'
    theme.value = savedTheme
    applyTheme(savedTheme)
  }

  /**
   * 应用主题
   */
  function applyTheme(newTheme: Theme) {
    const root = document.documentElement
    
    if (newTheme === 'dark') {
      root.classList.add('dark')
      isDark.value = true
    } else if (newTheme === 'light') {
      root.classList.remove('dark')
      isDark.value = false
    } else {
      // system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      if (prefersDark) {
        root.classList.add('dark')
        isDark.value = true
      } else {
        root.classList.remove('dark')
        isDark.value = false
      }
    }
  }

  /**
   * 设置主题
   */
  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    themeCookie.value = newTheme
    applyTheme(newTheme)
  }

  /**
   * 切换主题（light <-> dark）
   */
  function toggleTheme() {
    if (isDark.value) {
      setTheme('light')
    } else {
      setTheme('dark')
    }
  }

  /**
   * 监听系统主题变化
   */
  function watchSystemTheme() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', (e) => {
      if (theme.value === 'system') {
        applyTheme('system')
      }
    })
  }

  return {
    theme: readonly(theme),
    isDark: readonly(isDark),
    setTheme,
    toggleTheme,
    initTheme,
    watchSystemTheme,
  }
}
