<template>
  <div class="tag-manage-page">
    <div class="page-header">
      <div class="header-left">
        <h1>标签管理</h1>
        <p>管理文章标签</p>
      </div>
      <div class="header-right">
        <n-button type="primary" @click="handleCreate">
          <template #icon>
            <n-icon :component="CreateOutline" />
          </template>
          新建标签
        </n-button>
      </div>
    </div>

    <n-card>
      <n-data-table
        :columns="columns"
        :data="tags"
        :loading="loading"
        :row-key="rowKey"
      />
    </n-card>

    <!-- Create/Edit Modal -->
    <n-modal
      v-model:show="showModal"
      preset="dialog"
      :title="isEdit ? '编辑标签' : '新建标签'"
      :positive-text="saving ? '保存中...' : '确定'"
      :negative-text="cancelText"
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
          <n-input v-model:value="formData.name" placeholder="请输入标签名称" />
        </n-form-item>

        <n-form-item label="别名" path="slug">
          <n-input v-model:value="formData.slug" placeholder="请输入标签别名" />
        </n-form-item>

        <n-form-item label="颜色" path="color">
          <n-color-picker v-model:value="formData.color" />
        </n-form-item>
      </n-form>
    </n-modal>

    <!-- Delete Dialog -->
    <n-modal
      v-model:show="showDeleteModal"
      preset="dialog"
      title="删除标签"
      :content="`确定要删除标签「${deleteTag?.name}」吗？删除后该标签下的文章将失去此标签。`"
      positive-text="确定"
      negative-text="取消"
      @positive-click="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, h, onMounted } from 'vue'
import { useMessage, useDialog, NButton, NTag, NIcon } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { CreateOutline, PencilOutline, TrashOutline } from '@vicons/ionicons5'
import { adminTagApi } from '@/api'

const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const tags = ref<any[]>([])
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const deleteTag = ref<any>(null)

const formRef = ref(null)
const formData = reactive({
  id: null,
  name: '',
  slug: '',
  color: '#18a058',
})

const formRules = {
  name: { required: true, message: '请输入标签名称', trigger: 'blur' },
  slug: { required: true, message: '请输入标签别名', trigger: 'blur' },
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
      return h(NTag, {
        type: 'default',
        bordered: false,
        style: {
          backgroundColor: row.color || '#18a058',
          color: '#fff',
        },
      }, {
        default: () => row.name,
      })
    },
  },
  {
    title: '别名',
    key: 'slug',
    width: 150,
  },
  {
    title: '颜色',
    key: 'color',
    width: 100,
    render(row) {
      return h('div', {
        style: {
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        },
      }, [
        h('div', {
          style: {
            width: '20px',
            height: '20px',
            borderRadius: '4px',
            backgroundColor: row.color || '#18a058',
          },
        }),
        h('span', { style: 'font-size: 13px; color: #666;' }, row.color || '#18a058'),
      ])
    },
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
    color: '#18a058',
  })
  showModal.value = true
}

const handleEdit = (tag: any) => {
  isEdit.value = true
  Object.assign(formData, {
    id: tag.id,
    name: tag.name,
    slug: tag.slug,
    color: tag.color,
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
      color: formData.color,
    }

    if (isEdit.value) {
      await adminTagApi.update(formData.id!, data)
      message.success('更新成功')
    } else {
      await adminTagApi.create(data)
      message.success('创建成功')
    }

    showModal.value = false
    loadTags()
    return true
  } catch (error) {
    message.error(isEdit.value ? '更新失败' : '创建失败')
    return false
  } finally {
    saving.value = false
  }
}

const handleDelete = (tag: any) => {
  deleteTag.value = tag
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  if (!deleteTag.value) return

  try {
    await adminTagApi.delete(deleteTag.value.id)
    message.success('删除成功')
    loadTags()
  } catch (error) {
    message.error('删除失败')
  } finally {
    showDeleteModal.value = false
    deleteTag.value = null
  }
}

const loadTags = async () => {
  loading.value = true
  try {
    const response = await adminTagApi.getList()
    tags.value = response.data
  } catch (error) {
    message.error('加载标签失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.tag-manage-page {
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
