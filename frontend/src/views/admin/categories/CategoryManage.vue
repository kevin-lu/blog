<template>
  <div class="category-manage-page">
    <div class="page-header">
      <div class="header-left">
        <h1>分类管理</h1>
        <p>管理文章分类</p>
      </div>
      <div class="header-right">
        <n-button type="primary" @click="handleCreate">
          <template #icon>
            <n-icon :component="CreateOutline" />
          </template>
          新建分类
        </n-button>
      </div>
    </div>

    <n-card>
      <n-data-table
        :columns="columns"
        :data="categories"
        :loading="loading"
        :row-key="rowKey"
      />
    </n-card>

    <!-- Create/Edit Modal -->
    <n-modal
      v-model:show="showModal"
      preset="dialog"
      :title="isEdit ? '编辑分类' : '新建分类'"
      :positive-text="saving ? '保存中...' : '确定'"
      negative-text="取消"
      @positive-click="handleSave"
    >
      <n-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="80px"
      >
        <n-form-item label="名称" path="name">
          <n-input v-model:value="formData.name" placeholder="请输入分类名称" />
        </n-form-item>

        <n-form-item label="别名" path="slug">
          <n-input v-model:value="formData.slug" placeholder="请输入分类别名" />
        </n-form-item>

        <n-form-item label="描述" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="请输入分类描述"
            :rows="3"
          />
        </n-form-item>

        <n-form-item label="排序" path="sortOrder">
          <n-input-number
            v-model:value="formData.sortOrder"
            :min="0"
            placeholder="数字越小越靠前"
            style="width: 100%"
          />
        </n-form-item>
      </n-form>
    </n-modal>

    <!-- Delete Dialog -->
    <n-modal
      v-model:show="showDeleteModal"
      preset="dialog"
      title="删除分类"
      :content="`确定要删除分类「${deleteCategory?.name}」吗？删除后该分类下的文章将失去分类。`"
      positive-text="确定"
      negative-text="取消"
      @positive-click="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted } from 'vue'
import { useMessage, NButton, NTag, NIcon, NInputNumber } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { CreateOutline, PencilOutline, TrashOutline } from '@vicons/ionicons5'
import { adminCategoryApi } from '@/api'

const message = useMessage()

const loading = ref(false)
const categories = ref<any[]>([])
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const deleteCategory = ref<any>(null)

const formRef = ref(null)
const formData = reactive({
  id: null,
  name: '',
  slug: '',
  description: '',
  sortOrder: 0,
})

const formRules = {
  name: { required: true, message: '请输入分类名称', trigger: 'blur' },
  slug: { required: true, message: '请输入分类别名', trigger: 'blur' },
}

const rowKey = (row: any) => row.id

const columns: DataTableColumns = [
  {
    title: 'ID',
    key: 'id',
    width: 60,
  },
  {
    title: '名称',
    key: 'name',
    width: 200,
    render(row) {
      return h('div', { style: 'display: flex; flex-direction: column; gap: 4px;' }, [
        h('span', { style: 'font-weight: 500;' }, row.name),
        h('span', { style: 'font-size: 12px; color: #999;' }, row.slug),
      ])
    },
  },
  {
    title: '描述',
    key: 'description',
    ellipsis: {
      tooltip: true,
    },
  },
  {
    title: '排序',
    key: 'sort_order',
    width: 80,
  },
  {
    title: '文章数',
    key: 'article_count',
    width: 80,
    render(row) {
      return h(NTag, {
        type: 'info',
        bordered: false,
        size: 'small',
      }, {
        default: () => row.article_count || 0,
      })
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 180,
    fixed: 'right',
    render(row) {
      return h('div', { style: 'display: flex; gap: 8px;' }, [
        h(NButton, {
          size: 'small',
          type: 'primary',
          onClick: () => handleEdit(row),
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

const handleCreate = () => {
  isEdit.value = false
  Object.assign(formData, {
    id: null,
    name: '',
    slug: '',
    description: '',
    sortOrder: 0,
  })
  showModal.value = true
}

const handleEdit = (category: any) => {
  isEdit.value = true
  Object.assign(formData, {
    id: category.id,
    name: category.name,
    slug: category.slug,
    description: category.description,
    sortOrder: category.sort_order || 0,
  })
  showModal.value = true
}

const handleSave = async () => {
  let hasError = false
  try {
    ;(formRef.value as any)?.validate((errors: any) => {
      if (errors) hasError = true
    })
    if (hasError) return false

    saving.value = true
    const data = {
      name: formData.name,
      slug: formData.slug,
      description: formData.description,
      sort_order: formData.sortOrder,
    }

    if (isEdit.value) {
      await adminCategoryApi.update(formData.id!, data)
      message.success('更新成功')
    } else {
      await adminCategoryApi.create(data)
      message.success('创建成功')
    }

    showModal.value = false
    loadCategories()
    return true
  } catch (error) {
    message.error(isEdit.value ? '更新失败' : '创建失败')
    return false
  } finally {
    saving.value = false
  }
}

const handleDelete = (category: any) => {
  deleteCategory.value = category
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  if (!deleteCategory.value) return

  try {
    await adminCategoryApi.delete(deleteCategory.value.id)
    message.success('删除成功')
    loadCategories()
  } catch (error) {
    message.error('删除失败')
  } finally {
    showDeleteModal.value = false
    deleteCategory.value = null
  }
}

const loadCategories = async () => {
  loading.value = true
  try {
    const response = await adminCategoryApi.getList()
    categories.value = response.data
  } catch (error) {
    message.error('加载分类失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.category-manage-page {
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
</style>
