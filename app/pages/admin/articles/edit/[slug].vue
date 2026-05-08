<template>
  <div class="article-editor-page">
    <n-card>
      <template #header>
        编辑文章
      </template>

      <n-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-placement="top"
      >
        <n-form-item label="标题" path="title">
          <n-input
            v-model:value="form.title"
            placeholder="输入文章标题"
            size="large"
          />
        </n-form-item>

        <n-form-item label="Slug" path="slug">
          <n-input
            v-model:value="form.slug"
            placeholder="文章 URL 标识"
            disabled
          />
        </n-form-item>

        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="form.description"
            type="textarea"
            placeholder="文章简要描述"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="封面图片" path="coverImage">
          <n-input
            v-model:value="form.coverImage"
            placeholder="封面图片 URL"
          />
        </n-form-item>

        <n-form-item label="状态" path="status">
          <n-radio-group v-model:value="form.status">
            <n-radio-button value="draft">草稿</n-radio-button>
            <n-radio-button value="published">已发布</n-radio-button>
          </n-radio-group>
        </n-form-item>

        <n-form-item>
          <n-space>
            <n-button type="primary" :loading="saving" @click="handleSubmit">
              {{ saving ? '保存中...' : '保存' }}
            </n-button>
            <n-button @click="handleCancel">
              取消
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import type { FormRules, FormInst } from 'naive-ui';
import { apiClient } from '~/utils/api';
import { useNotification } from '~/composables/useNotification';

definePageMeta({
  layout: 'admin',
});

const router = useRouter();
const route = useRoute();
const notification = useNotification();

const formRef = ref<FormInst | null>(null);
const saving = ref(false);

const form = reactive({
  slug: '',
  title: '',
  description: '',
  coverImage: '',
  status: 'draft',
});

const rules: FormRules = {
  slug: {
    required: true,
    message: '请输入 slug',
    trigger: 'blur',
  },
  title: {
    required: true,
    message: '请输入标题',
    trigger: 'blur',
  },
};

const loadArticle = async (slug: string) => {
  try {
    const response = await apiClient.get<any>(`/articles/${slug}`);
    if (response.success) {
      const article = response.data;
      form.slug = article.slug;
      form.title = article.title;
      form.description = article.description || '';
      form.coverImage = article.coverImage || '';
      form.status = article.status;
    } else {
      notification.error('获取文章失败', response.message);
    }
  } catch (error: any) {
    notification.error('获取文章失败', error.response?.data?.message || '网络错误');
  }
};

const handleSubmit = async () => {
  try {
    await formRef.value?.validate();
    saving.value = true;

    const response = await apiClient.put<any>(`/articles/${form.slug}`, {
      title: form.title,
      description: form.description,
      coverImage: form.coverImage,
      status: form.status,
    });

    if (response.success) {
      notification.success('更新成功');
      router.push('/admin/articles');
    } else {
      notification.error('更新失败', response.message);
    }
  } catch (error: any) {
    if (error.response) {
      notification.error('更新失败', error.response.data.message);
    }
  } finally {
    saving.value = false;
  }
};

const handleCancel = () => {
  router.push('/admin/articles');
};

onMounted(() => {
  if (route.params.slug) {
    loadArticle(route.params.slug as string);
  }
});
</script>

<style scoped>
.article-editor-page {
  max-width: 800px;
}
</style>
