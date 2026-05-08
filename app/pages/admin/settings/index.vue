<template>
  <div class="settings-page">
    <n-card title="站点配置">
      <n-form
        ref="formRef"
        :model="config"
        label-placement="top"
      >
        <n-form-item label="站点标题">
          <n-input v-model:value="config.siteTitle" placeholder="输入站点标题" />
        </n-form-item>

        <n-form-item label="站点描述">
          <n-input
            v-model:value="config.siteDescription"
            type="textarea"
            placeholder="输入站点描述"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="站点关键词">
          <n-input v-model:value="config.siteKeywords" placeholder="输入站点关键词，多个用逗号分隔" />
        </n-form-item>

        <n-form-item label="作者名称">
          <n-input v-model:value="config.authorName" placeholder="输入作者名称" />
        </n-form-item>

        <n-form-item label="GitHub 用户名">
          <n-input v-model:value="config.githubUsername" placeholder="输入 GitHub 用户名" />
        </n-form-item>

        <n-form-item label="每页文章数">
          <n-input-number v-model:value="config.postsPerPage" :min="1" :max="100" />
        </n-form-item>

        <n-form-item label="是否启用评论">
          <n-switch v-model:value="config.commentsEnabled" />
        </n-form-item>

        <n-form-item>
          <n-space>
            <n-button type="primary" :loading="saving" @click="handleSubmit">
              {{ saving ? '保存中...' : '保存配置' }}
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useNotification } from '~/composables/useNotification';
import { apiClient } from '~/utils/api';

definePageMeta({
  layout: 'admin',
});

const notification = useNotification();
const saving = ref(false);

const config = reactive({
  siteTitle: '',
  siteDescription: '',
  siteKeywords: '',
  authorName: '',
  githubUsername: '',
  postsPerPage: 10,
  commentsEnabled: true,
});

const loadConfig = async () => {
  try {
    const response = await apiClient.get<any>('/settings');
    if (response.success) {
      Object.assign(config, response.data);
    }
  } catch (error: any) {
    notification.error('获取配置失败', error.response?.data?.message || '网络错误');
  }
};

const handleSubmit = async () => {
  saving.value = true;
  try {
    const response = await apiClient.put<any>('/settings', config);
    if (response.success) {
      notification.success('保存配置成功');
    } else {
      notification.error('保存配置失败', response.message);
    }
  } catch (error: any) {
    notification.error('保存配置失败', error.response?.data?.message || '网络错误');
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  loadConfig();
});
</script>

<style scoped>
.settings-page {
  max-width: 800px;
}
</style>
