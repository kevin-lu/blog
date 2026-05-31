<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="login-title">博客管理后台</h1>
        <p class="login-subtitle">请登录</p>
      </div>

      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <n-form-item path="username" label="用户名">
          <n-input
            v-model:value="formData.username"
            placeholder="请输入用户名"
            size="large"
            clearable
          >
            <template #prefix>
              <n-icon :component="PersonOutline" />
            </template>
          </n-input>
        </n-form-item>

        <n-form-item path="password" label="密码">
          <n-input
            v-model:value="formData.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password-on="click"
          >
            <template #prefix>
              <n-icon :component="LockClosedOutline" />
            </template>
          </n-input>
        </n-form-item>

        <n-form-item>
          <n-checkbox v-model:checked="rememberMe">
            记住我
          </n-checkbox>
        </n-form-item>

        <n-button
          type="primary"
          size="large"
          block
          :loading="loading"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登录' }}
        </n-button>
      </n-form>

      <div class="login-footer">
        <n-text depth="3" style="font-size: 12px">
          © 2026 博客系统。All rights reserved.
        </n-text>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormRules, FormInst } from 'naive-ui'
import { PersonOutline, LockClosedOutline } from '@vicons/ionicons5'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api'

interface LoginForm {
  username: string
  password: string
}

const router = useRouter()
const message = useMessage()
const authStore = useAuthStore()

const formRef = ref<FormInst | null>(null)
const loading = ref(false)
const rememberMe = ref(false)

const formData = reactive<LoginForm>({
  username: '',
  password: '',
})

const formRules: FormRules = {
  username: {
    required: true,
    message: '请输入用户名',
    trigger: 'blur',
  },
  password: {
    required: true,
    message: '请输入密码',
    trigger: 'blur',
  },
  passwordConfirm: {
    required: true,
    message: '请再次输入密码',
    trigger: 'blur',
  },
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (errors) => {
    if (errors) return

    loading.value = true

    try {
      const response = await authApi.login(formData.username, formData.password)

      // 保存 tokens
      authStore.setTokens(response.access_token, response.refresh_token)
      authStore.setUser(response.user)

      message.success('登录成功')

      // 跳转到管理后台
      setTimeout(() => {
        router.push('/admin')
      }, 500)
    } catch (error: any) {
      console.error('Login failed:', error)
      message.error(error.response?.data?.error || '登录失败，请检查用户名和密码')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  margin-bottom: 24px;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
}

:deep(.n-form-item-label) {
  font-weight: 500;
}

:deep(.n-input-wrapper) {
  border-radius: 8px;
}
</style>
