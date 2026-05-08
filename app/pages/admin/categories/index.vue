<template>
  <div class="categories-page">
    <n-grid :cols="2" :x-gap="24">
      <!-- 分类列表 -->
      <n-grid-item>
        <n-card title="分类列表">
          <n-button type="primary" @click="showCreateModal = true" style="margin-bottom: 16px;">
            <template #icon>
              <n-icon :component="PlusOutlined" />
            </template>
            新建分类
          </n-button>

          <n-data-table
            :columns="columns"
            :data="categories"
            :loading="loading"
            size="small"
          />
        </n-card>
      </n-grid-item>

      <!-- 标签列表 -->
      <n-grid-item>
        <n-card title="标签列表">
          <n-button type="primary" @click="showTagModal = true" style="margin-bottom: 16px;">
            <template #icon>
              <n-icon :component="PlusOutlined" />
            </template>
            新建标签
          </n-button>

          <n-data-table
            :columns="tagColumns"
            :data="tags"
            :loading="tagLoading"
            size="small"
          />
        </n-card>
      </n-grid-item>
    </n-grid>

    <!-- 新建分类模态框 -->
    <n-modal v-model:show="showCreateModal" preset="dialog" title="新建分类">
      <n-form
        ref="categoryFormRef"
        :model="categoryForm"
        :rules="categoryRules"
        label-placement="top"
      >
        <n-form-item label="名称" path="name">
          <n-input v-model:value="categoryForm.name" placeholder="分类名称" />
        </n-form-item>
        <n-form-item label="Slug" path="slug">
          <n-input v-model:value="categoryForm.slug" placeholder="分类标识" />
        </n-form-item>
        <n-form-item label="描述" path="description">
          <n-input v-model:value="categoryForm.description" type="textarea" placeholder="分类描述" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="handleCreateCategory">保存</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- 新建标签模态框 -->
    <n-modal v-model:show="showTagModal" preset="dialog" title="新建标签">
      <n-form
        ref="tagFormRef"
        :model="tagForm"
        :rules="tagRules"
        label-placement="top"
      >
        <n-form-item label="名称" path="name">
          <n-input v-model:value="tagForm.name" placeholder="标签名称" />
        </n-form-item>
        <n-form-item label="Slug" path="slug">
          <n-input v-model:value="tagForm.slug" placeholder="标签标识" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showTagModal = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="handleCreateTag">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, computed, onMounted } from 'vue';
import type { DataTableColumns, FormRules, FormInst } from 'naive-ui';
import { PlusOutlined, DeleteOutlined } from '@vicons/antd';
import { NButton, NTag, NPopconfirm, NIcon } from 'naive-ui';
import { apiClient } from '~/utils/api';
import { useNotification } from '~/composables/useNotification';

definePageMeta({
  layout: 'admin',
});

const notification = useNotification();

interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  parentId?: number;
  sortOrder: number;
  createdAt: string;
}

interface Tag {
  id: number;
  name: string;
  slug: string;
  createdAt: string;
}

const loading = ref(false);
const tagLoading = ref(false);
const saving = ref(false);
const categories = ref<Category[]>([]);
const tags = ref<Tag[]>([]);
const showCreateModal = ref(false);
const showTagModal = ref(false);

const categoryFormRef = ref<FormInst | null>(null);
const tagFormRef = ref<FormInst | null>(null);

const categoryForm = reactive({
  name: '',
  slug: '',
  description: '',
  sortOrder: 0,
});

const tagForm = reactive({
  name: '',
  slug: '',
});

const categoryRules: FormRules = {
  name: { required: true, message: '请输入分类名称', trigger: 'blur' },
  slug: { required: true, message: '请输入分类标识', trigger: 'blur' },
};

const tagRules: FormRules = {
  name: { required: true, message: '请输入标签名称', trigger: 'blur' },
  slug: { required: true, message: '请输入标签标识', trigger: 'blur' },
};

const columns = computed<DataTableColumns<Category>>(() => [
  { title: '名称', key: 'name', width: 150 },
  { title: 'Slug', key: 'slug', width: 150 },
  { title: '描述', key: 'description', ellipsis: { tooltip: true }, maxWidth: 200 },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row) => h(NPopconfirm, {
      onPositiveClick: () => handleDeleteCategory(row.id),
    }, {
      trigger: () => h(NButton, { size: 'small', type: 'error' }, {
        default: () => '删除',
        icon: () => h(NIcon, { component: DeleteOutlined }),
      }),
      default: () => `确定要删除分类"${row.name}"吗？`,
    }),
  },
]);

const tagColumns = computed<DataTableColumns<Tag>>(() => [
  { title: '名称', key: 'name', width: 150 },
  { title: 'Slug', key: 'slug', width: 150 },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row) => h(NPopconfirm, {
      onPositiveClick: () => handleDeleteTag(row.id),
    }, {
      trigger: () => h(NButton, { size: 'small', type: 'error' }, {
        default: () => '删除',
        icon: () => h(NIcon, { component: DeleteOutlined }),
      }),
      default: () => `确定要删除标签"${row.name}"吗？`,
    }),
  },
]);

const fetchCategories = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get<any>('/categories');
    if (response.success) {
      categories.value = response.data;
    }
  } catch (error: any) {
    notification.error('获取分类失败', error.response?.data?.message || '网络错误');
  } finally {
    loading.value = false;
  }
};

const fetchTags = async () => {
  tagLoading.value = true;
  try {
    const response = await apiClient.get<any>('/tags');
    if (response.success) {
      tags.value = response.data;
    }
  } catch (error: any) {
    notification.error('获取标签失败', error.response?.data?.message || '网络错误');
  } finally {
    tagLoading.value = false;
  }
};

const handleCreateCategory = async () => {
  try {
    await categoryFormRef.value?.validate();
    saving.value = true;

    const response = await apiClient.post<any>('/categories', categoryForm);
    if (response.success) {
      notification.success('创建分类成功');
      showCreateModal.value = false;
      fetchCategories();
      // 重置表单
      Object.assign(categoryForm, { name: '', slug: '', description: '', sortOrder: 0 });
    } else {
      notification.error('创建分类失败', response.message);
    }
  } catch (error: any) {
    if (error.response) {
      notification.error('创建分类失败', error.response.data.message);
    }
  } finally {
    saving.value = false;
  }
};

const handleCreateTag = async () => {
  try {
    await tagFormRef.value?.validate();
    saving.value = true;

    const response = await apiClient.post<any>('/tags', tagForm);
    if (response.success) {
      notification.success('创建标签成功');
      showTagModal.value = false;
      fetchTags();
      // 重置表单
      Object.assign(tagForm, { name: '', slug: '' });
    } else {
      notification.error('创建标签失败', response.message);
    }
  } catch (error: any) {
    if (error.response) {
      notification.error('创建标签失败', error.response.data.message);
    }
  } finally {
    saving.value = false;
  }
};

const handleDeleteCategory = async (id: number) => {
  try {
    const response = await apiClient.delete<any>(`/categories/${id}`);
    if (response.success) {
      notification.success('删除分类成功');
      fetchCategories();
    } else {
      notification.error('删除分类失败', response.message);
    }
  } catch (error: any) {
    notification.error('删除分类失败', error.response?.data?.message || '网络错误');
  }
};

const handleDeleteTag = async (id: number) => {
  try {
    const response = await apiClient.delete<any>(`/tags/${id}`);
    if (response.success) {
      notification.success('删除标签成功');
      fetchTags();
    } else {
      notification.error('删除标签失败', response.message);
    }
  } catch (error: any) {
    notification.error('删除标签失败', error.response?.data?.message || '网络错误');
  }
};

onMounted(() => {
  fetchCategories();
  fetchTags();
});
</script>

<style scoped>
.categories-page {
  max-width: 1400px;
}
</style>
