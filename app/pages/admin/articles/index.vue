<template>
  <div class="articles-page">
    <n-card>
      <div class="page-header">
        <h1 class="page-title">文章管理</h1>
        <n-button type="primary" @click="handleCreate">
          <template #icon>
            <n-icon :component="PlusOutlined" />
          </template>
          新建文章
        </n-button>
      </div>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <n-space>
          <n-select
            v-model:value="statusFilter"
            :options="statusOptions"
            placeholder="状态"
            style="width: 150px"
            @update:value="handleFilterChange"
          />
          <n-input
            v-model:value="searchKeyword"
            placeholder="搜索标题或 slug"
            style="width: 300px"
            @input="handleSearch"
          >
            <template #prefix>
              <n-icon :component="SearchOutlined" />
            </template>
          </n-input>
        </n-space>
      </div>

      <!-- 文章列表 -->
      <n-data-table
        :columns="columns"
        :data="articles"
        :loading="loading"
        :pagination="pagination"
        :remote="true"
        @update:checked-row-keys="handleCheck"
        @update:page="handlePageChange"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, h, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { DataTableColumns, SelectOption } from 'naive-ui';
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from '@vicons/antd';
import { NButton, NTag, NPopconfirm, NIcon } from 'naive-ui';
import { apiClient } from '~/utils/api';
import { useNotification } from '~/composables/useNotification';
import { formatDateTime } from '~/utils/helpers';

definePageMeta({
  layout: 'admin',
});

const router = useRouter();
const notification = useNotification();

interface Article {
  id: number;
  slug: string;
  title: string;
  description?: string;
  coverImage?: string;
  status: string;
  publishedAt?: string;
  published_at?: string;
  createdAt?: string;
  created_at?: string;
  updatedAt?: string;
  updated_at?: string;
}

const loading = ref(false);
const articles = ref<Article[]>([]);
const statusFilter = ref<string>('');
const searchKeyword = ref('');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

const statusOptions: SelectOption[] = [
  { label: '全部状态', value: '' },
  { label: '已发布', value: 'published' },
  { label: '草稿', value: 'draft' },
];

const columns = computed<DataTableColumns<Article>>(() => [
  {
    type: 'selection',
  },
  {
    title: '标题',
    key: 'title',
    width: 300,
    render: (row) => h('div', [
      h('div', { style: 'font-weight: 600; margin-bottom: 4px;' }, row.title),
      h('div', { style: 'font-size: 12px; color: #999;' }, `/${row.slug}`),
    ]),
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => h(NTag, {
      type: row.status === 'published' ? 'success' : 'warning',
    }, { default: () => row.status === 'published' ? '已发布' : '草稿' }),
  },
  {
    title: '发布时间',
    key: 'publishedAt',
    width: 180,
    render: (row) => formatDateTime(row.publishedAt || row.published_at),
  },
  {
    title: '创建时间',
    key: 'createdAt',
    width: 180,
    render: (row) => formatDateTime(row.createdAt || row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    fixed: 'right',
    render: (row) => h('div', { style: 'display: flex; gap: 8px;' }, [
      h(NButton, {
        size: 'small',
        type: 'primary',
        onClick: () => handleEdit(row.slug),
      }, { default: () => '编辑', icon: () => h(NIcon, { component: EditOutlined }) }),
      h(NButton, {
        size: 'small',
        onClick: () => handleView(row.slug),
      }, { default: () => '查看', icon: () => h(NIcon, { component: EyeOutlined }) }),
      h(NPopconfirm, {
        onPositiveClick: () => handleDelete(row.slug),
      }, {
        trigger: () => h(NButton, {
          size: 'small',
          type: 'error',
        }, { default: () => '删除', icon: () => h(NIcon, { component: DeleteOutlined }) }),
        default: () => `确定要删除文章"${row.title}"吗？`,
      }),
    ]),
  },
]);

const pagination = computed(() => ({
  page: currentPage.value,
  pageSize: pageSize.value,
  itemCount: total.value,
  showSizePicker: true,
  pageSizes: [10, 20, 50, 100],
  onChange: (page: number) => handlePageChange(page),
  onUpdatePageSize: (size: number) => handlePageSizeChange(size),
}));

const fetchArticles = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: currentPage.value,
      pageSize: pageSize.value,
    };
    if (statusFilter.value) params.status = statusFilter.value;
    if (searchKeyword.value) params.search = searchKeyword.value;

    const response = await apiClient.get<any>('/articles', { params });
    
    if (response.success) {
      articles.value = response.data.data;
      total.value = response.data.total;
    } else {
      notification.error('获取文章列表失败', response.message);
    }
  } catch (error: any) {
    notification.error('获取文章列表失败', error.response?.data?.message || '网络错误');
  } finally {
    loading.value = false;
  }
};

const handleCreate = () => {
  router.push('/admin/articles/create');
};

const handleEdit = (slug: string) => {
  router.push(`/admin/articles/edit/${slug}`);
};

const handleView = (slug: string) => {
  window.open(`/blog/${slug}`, '_blank');
};

const handleDelete = async (slug: string) => {
  try {
    const response = await apiClient.delete<any>(`/articles/${slug}`);
    if (response.success) {
      notification.success('删除成功');
      fetchArticles();
    } else {
      notification.error('删除失败', response.message);
    }
  } catch (error: any) {
    notification.error('删除失败', error.response?.data?.message || '网络错误');
  }
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
  fetchArticles();
};

const handlePageSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchArticles();
};

const handleFilterChange = () => {
  currentPage.value = 1;
  fetchArticles();
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchArticles();
};

const handleCheck = () => {
  // 处理选择
};

onMounted(() => {
  fetchArticles();
});
</script>

<style scoped>
.articles-page {
  max-width: 1400px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.filter-bar {
  margin-bottom: 24px;
}
</style>
