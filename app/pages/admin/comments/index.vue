<template>
  <div class="comments-page">
    <n-card>
      <div class="page-header">
        <h1 class="page-title">评论管理</h1>
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
        </n-space>
      </div>

      <!-- 评论列表 -->
      <n-data-table
        :columns="columns"
        :data="comments"
        :loading="loading"
        :pagination="pagination"
        :remote="true"
        @update:page="handlePageChange"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, h, computed, onMounted } from 'vue';
import type { DataTableColumns, SelectOption, NTag } from 'naive-ui';
import { NButton, NTag, NPopconfirm, NIcon, NSpace } from 'naive-ui';
import { CheckOutlined, CloseOutlined, DeleteOutlined } from '@vicons/antd';
import { apiClient } from '~/utils/api';
import { useNotification } from '~/composables/useNotification';

definePageMeta({
  layout: 'admin',
});

const notification = useNotification();

interface Comment {
  id: number;
  articleSlug: string;
  githubId?: string;
  status: string;
  isPinned: boolean;
  createdAt: string;
  updatedAt: string;
}

const loading = ref(false);
const comments = ref<Comment[]>([]);
const statusFilter = ref<string>('');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);

const statusOptions: SelectOption[] = [
  { label: '全部状态', value: '' },
  { label: '待审核', value: 'pending' },
  { label: '已通过', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
];

const columns = computed<DataTableColumns<Comment>>(() => [
  {
    title: '文章',
    key: 'articleSlug',
    width: 200,
    render: (row) => h('a', {
      href: `/blog/${row.articleSlug}`,
      target: '_blank',
      style: 'color: #1890ff;',
    }, row.articleSlug),
  },
  {
    title: 'GitHub ID',
    key: 'githubId',
    width: 150,
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row) => {
      const typeMap: Record<string, any> = {
        pending: 'warning',
        approved: 'success',
        rejected: 'error',
      };
      const textMap: Record<string, string> = {
        pending: '待审核',
        approved: '已通过',
        rejected: '已拒绝',
      };
      return h(NTag, { type: typeMap[row.status] || 'default' }, {
        default: () => textMap[row.status] || row.status,
      });
    },
  },
  {
    title: '置顶',
    key: 'isPinned',
    width: 80,
    render: (row) => row.isPinned ? '是' : '否',
  },
  {
    title: '创建时间',
    key: 'createdAt',
    width: 180,
    render: (row) => new Date(row.createdAt).toLocaleString('zh-CN'),
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    fixed: 'right',
    render: (row) => h(NSpace, { size: 'small' }, {
      default: () => [
        row.status !== 'approved' ? h(NButton, {
          size: 'small',
          type: 'success',
          onClick: () => handleApprove(row.id),
        }, {
          default: () => '通过',
          icon: () => h(NIcon, { component: CheckOutlined }),
        }) : null,
        row.status !== 'rejected' ? h(NButton, {
          size: 'small',
          type: 'error',
          onClick: () => handleReject(row.id),
        }, {
          default: () => '拒绝',
          icon: () => h(NIcon, { component: CloseOutlined }),
        }) : null,
        h(NPopconfirm, {
          onPositiveClick: () => handleDelete(row.id),
        }, {
          trigger: () => h(NButton, {
            size: 'small',
            type: 'error',
          }, {
            default: () => '删除',
            icon: () => h(NIcon, { component: DeleteOutlined }),
          }),
          default: () => '确定要删除这条评论吗？',
        }),
      ],
    }),
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

const fetchComments = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: currentPage.value,
      pageSize: pageSize.value,
    };
    if (statusFilter.value) params.status = statusFilter.value;

    const response = await apiClient.get<any>('/comments', { params });
    
    if (response.success) {
      comments.value = response.data.data;
      total.value = response.data.total;
    } else {
      notification.error('获取评论列表失败', response.message);
    }
  } catch (error: any) {
    notification.error('获取评论列表失败', error.response?.data?.message || '网络错误');
  } finally {
    loading.value = false;
  }
};

const handleApprove = async (id: number) => {
  try {
    const response = await apiClient.put<any>(`/comments/${id}`, { status: 'approved' });
    if (response.success) {
      notification.success('已通过评论');
      fetchComments();
    } else {
      notification.error('操作失败', response.message);
    }
  } catch (error: any) {
    notification.error('操作失败', error.response?.data?.message || '网络错误');
  }
};

const handleReject = async (id: number) => {
  try {
    const response = await apiClient.put<any>(`/comments/${id}`, { status: 'rejected' });
    if (response.success) {
      notification.success('已拒绝评论');
      fetchComments();
    } else {
      notification.error('操作失败', response.message);
    }
  } catch (error: any) {
    notification.error('操作失败', error.response?.data?.message || '网络错误');
  }
};

const handleDelete = async (id: number) => {
  try {
    const response = await apiClient.delete<any>(`/comments/${id}`);
    if (response.success) {
      notification.success('删除评论成功');
      fetchComments();
    } else {
      notification.error('删除评论失败', response.message);
    }
  } catch (error: any) {
    notification.error('删除评论失败', error.response?.data?.message || '网络错误');
  }
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
  fetchComments();
};

const handlePageSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchComments();
};

const handleFilterChange = () => {
  currentPage.value = 1;
  fetchComments();
};

onMounted(() => {
  fetchComments();
});
</script>

<style scoped>
.comments-page {
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
