<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1 class="login-title">博客管理后台</h1>
          <p class="login-subtitle">请登录您的管理员账号</p>
        </div>

        <n-form
          ref="formRef"
          :model="form"
          :rules="rules"
          class="login-form"
        >
          <n-form-item path="username">
            <n-input
              v-model:value="form.username"
              placeholder="用户名"
              size="large"
              :prefix="() => h(UserOutlined)"
              @keyup.enter="handleLogin"
            />
          </n-form-item>

          <n-form-item path="password">
            <n-input
              v-model:value="form.password"
              type="password"
              placeholder="密码"
              size="large"
              :prefix="() => h(LockOutlined)"
              show-password-on="click"
              @keyup.enter="handleLogin"
            />
          </n-form-item>

          <n-form-item>
            <n-button
              type="primary"
              size="large"
              block
              :loading="loading"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登录' }}
            </n-button>
          </n-form-item>
        </n-form>

        <div class="login-footer">
          <n-alert type="info" title="提示">
            首次使用请先创建管理员账号，使用命令：<br/>
            <code>npm run create-admin &lt;用户名&gt; &lt;密码&gt;</code>
          </n-alert>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h } from 'vue';
import { useRouter } from 'vue-router';
import type { FormRules, FormInst } from 'naive-ui';
import { UserOutlined, LockOutlined } from '@vicons/antd';
import { useAdminStore } from '~/stores/admin';
import { useNotification } from '~/composables/useNotification';

const router = useRouter();
const adminStore = useAdminStore();
const notification = useNotification();

const formRef = ref<FormInst | null>(null);
const loading = ref(false);

const form = reactive({
  username: '',
  password: '',
});

const rules: FormRules = {
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
};

const handleLogin = async () => {
  try {
    await formRef.value?.validate();
    
    loading.value = true;
    
    const result = await adminStore.login(form);
    
    if (result.success) {
      notification.success('登录成功', '欢迎回来！');
      router.push('/admin/dashboard');
    } else {
      notification.error('登录失败', result.error || '请检查用户名和密码');
    }
  } catch (error) {
    // 表单验证失败
  } finally {
    loading.value = false;
  }
};

// 如果已登录，自动跳转到仪表盘
if (adminStore.isAuthenticated) {
  router.push('/admin/dashboard');
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  width: 100%;
  max-width: 420px;
  padding: 24px;
}

.login-card {
  background: #fff;
  border-radius: 16px;
  padding: 48px 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-title {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.login-form {
  margin-bottom: 24px;
}

.login-footer {
  margin-top: 24px;
}

.login-footer :deep(.n-alert) {
  font-size: 12px;
}

.login-footer :deep(code) {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  color: #4f46e5;
  font-family: monospace;
}
</style>
