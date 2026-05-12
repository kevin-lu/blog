<template>
  <div class="article-list-page">
    <div class="page-header">
      <div class="header-left">
        <h1>文章管理</h1>
        <p>管理所有文章</p>
      </div>
      <div class="header-right">
        <n-button type="primary" @click="goToCreate">
          <template #icon>
            <n-icon :component="CreateOutline" />
          </template>
          新建文章
        </n-button>
      </div>
    </div>

    <n-card>
      <!-- Filters -->
      <div class="filters">
        <n-space>
          <n-input
            v-model:value="filters.search"
            placeholder="搜索文章标题..."
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <n-icon :component="SearchOutline" />
            </template>
          </n-input>

          <n-select
            v-model:value="filters.status"
            :options="statusOptions"
            placeholder="状态"
            clearable
            style="width: 120px"
          />

          <n-select
            v-model:value="filters.category"
            :options="categoryOptions"
            placeholder="分类"
            clearable
            style="width: 150px"
          />

          <n-button type="primary" @click="handleSearch">
            搜索
          </n-button>
        </n-space>
      </div>

      <!-- Table -->
      <n-data-table
        :columns="columns"
        :data="articles"
        :loading="loading"
        :pagination="pagination"
        :row-key="rowKey"
        @update:checked-row-keys="handleCheck"
      />
    </n-card>

    <!-- Delete Dialog -->
    <n-modal
      v-model:show="showDeleteModal"
      preset="dialog"
      title="删除文章"
      :content="`确定要删除文章「${deleteArticle?.title}」吗？此操作不可恢复。`"
      positive-text="确定"
      negative-text="取消"
      @positive-click="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, NButton, NTag, NIcon } from 'naive-ui'
import type { DataTableColumns, DataTableRowKey } from 'naive-ui'
import {
  CreateOutline,
  SearchOutline,
  PencilOutline,
  TrashOutline,
  EyeOutline,
} from '@vicons/ionicons5'
import type { Article } from '@/types'
import { adminArticleApi, adminCategoryApi } from '@/api'
import { formatDateTime, getArticleDate } from '@/utils/date'

interface ArticleWithMeta extends Article {
  categories?: any[]
  tags?: any[]
}

const router = useRouter()
const message = useMessage()

const loading = ref(false)
const articles = ref<ArticleWithMeta[]>([])
const showDeleteModal = ref(false)
const deleteArticle = ref<ArticleWithMeta | null>(null)

const filters = reactive({
  search: '',
  status: '',
  category: '',
})

const statusOptions = [
  { label: '已发布', value: 'published' },
  { label: '草稿', value: 'draft' },
  { label: '已归档', value: 'archived' },
]

const categoryOptions = ref<any[]>([])

const pagination = reactive({
  page: 1,
  pageSize: 20,
  showSizePicker: true,
  pageSizes: [10, 20, 50],
  onChange: (page: number) => {
    pagination.page = page
    loadArticles()
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    loadArticles()
  },
})

const rowKey = (row: Article) => row.id

const columns: DataTableColumns = [
  {
    type: 'selection',
  },
  {
    title: 'ID',
    key: 'id',
    width: 60,
  },
  {
    title: '标题',
    key: 'title',
    ellipsis: {
      tooltip: true,
    },
    render(row) {
      return h('div', { style: 'display: flex; flex-direction: column; gap: 4px;' }, [
        h('span', { style: 'font-weight: 500;' }, row.title),
        h('span', { style: 'font-size: 12px; color: #999;' }, row.slug),
      ])
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render(row) {
      const typeMap: any = {
        published: 'success',
        draft: 'warning',
        archived: 'info',
      }
      const labelMap: any = {
        published: '已发布',
        draft: '草稿',
        archived: '已归档',
      }
      return h(NTag, {
        type: typeMap[row.status] || 'default',
        bordered: false,
        size: 'small',
      }, {
        default: () => labelMap[row.status] || row.status,
      })
    },
  },
  {
    title: '分类',
    key: 'categories',
    width: 150,
    render(row) {
      if (!row.categories || row.categories.length === 0) return null
      return h('div', { style: 'display: flex; gap: 4px; flex-wrap: wrap;' }, [
        row.categories.map((cat: any) =>
          h(NTag, {
            key: cat.id,
            type: 'info',
            bordered: false,
            size: 'small',
          }, {
            default: () => cat.name,
          })
        ),
      ])
    },
  },
  {
    title: '发布时间',
    key: 'published_at',
    width: 160,
    render(row) {
      return h('span', { style: 'font-size: 13px; color: #666;' }, [
        formatDateTime(getArticleDate(row)),
      ])
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    fixed: 'right',
    render(row) {
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        h(NButton, {
          size: 'small',
          type: 'tertiary',
          onClick: () => goToView(row.slug),
        }, {
          default: () => '查看',
          icon: () => h(NIcon, { component: EyeOutline }),
        }),
        h(NButton, {
          size: 'small',
          type: 'primary',
          onClick: () => goToEdit(row.slug),
        }, {
          default: () => '编辑',
          icon: () => h(NIcon, { component: PencilOutline }),
        }),
        h(NButton, {
          size: 'small',
          type: 'error',
          onClick: () => handleDelete(row),
        }, {
          default: () => '删除',
          icon: () => h(NIcon, { component: TrashOutline }),
        }),
      ])
    },
  },
]

const handleCheck = (checkedRowKeys: DataTableRowKey[]) => {
  console.log('checkedRowKeys', checkedRowKeys)
}

const goToCreate = () => {
  router.push('/admin/articles/create')
}

const goToView = (slug: string) => {
  window.open(`/posts/${slug}`, '_blank')
}

const goToEdit = (slug: string) => {
  router.push(`/admin/articles/edit/${slug}`)
}

const handleSearch = () => {
  loadArticles()
}

const handleDelete = (article: ArticleWithMeta) => {
  deleteArticle.value = article
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  if (!deleteArticle.value) return

  try {
    await adminArticleApi.delete(deleteArticle.value.slug)
    message.success('删除成功')
    loadArticles()
  } catch (error) {
    console.error('Delete failed:', error)
    message.error('删除失败')
  } finally {
    showDeleteModal.value = false
    deleteArticle.value = null
  }
}

const loadArticles = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      pageSize: pagination.pageSize,
    }
    if (filters.search) params.search = filters.search
    if (filters.status) params.status = filters.status
    if (filters.category) params.category = filters.category

    const response = await adminArticleApi.getList(params)
    if (response.data) {
      articles.value = response.data.data
      pagination.page = response.data.page || 1
      pagination.pageSize = response.data.pageSize || 20
    }
  } catch (error) {
    console.error('Failed to load articles:', error)
    message.error('加载文章失败')
  } finally {
    loading.value = false
  }
}

const loadCategories = async () => {
  try {
    const response = await adminCategoryApi.getList()
    categoryOptions.value = response.data.map((cat: any) => ({
      label: cat.name,
      value: cat.slug,
    }))
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

onMounted(() => {
  loadArticles()
  loadCategories()
})
</script>

<style scoped>
.article-list-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-left p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.filters {
  margin-bottom: 20px;
}
</style>
