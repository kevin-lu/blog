<template>
  <div class="article-edit-page">
    <div class="page-header">
      <div class="header-left">
        <h1>{{ isEdit ? '编辑文章' : '新建文章' }}</h1>
        <p>{{ isEdit ? '修改文章内容' : '创建一篇新文章' }}</p>
      </div>
      <div class="header-right">
        <n-button type="warning" @click="showAIRewriteModal = true" :disabled="isEdit">
          <template #icon>
            <n-icon :component="SparklesOutline" />
          </template>
          AI 改写
        </n-button>
        <n-button @click="handleSaveDraft" :loading="saving">
          保存草稿
        </n-button>
        <n-button type="primary" @click="handlePublish" :loading="saving">
          发布文章
        </n-button>
      </div>
    </div>

    <!-- AI Rewrite Modal -->
    <n-modal v-model:show="showAIRewriteModal" preset="card" title="🤖 AI 智能改写" style="width: 500px;">
      <n-space vertical>
        <n-alert type="info">
          输入微信公众号文章链接，AI 将自动抓取并改写内容
        </n-alert>
        
        <n-input
          v-model:value="aiSourceUrl"
          placeholder="请输入微信公众号文章链接"
        />
        
        <n-space>
          <n-select
            v-model:value="aiRewriteStrategy"
            :options="rewriteStrategyOptions"
            style="width: 150px"
          />
          <n-select
            v-model:value="aiTemplateType"
            :options="templateTypeOptions"
            style="width: 150px"
          />
        </n-space>
        
        <n-button
          type="primary"
          block
          :loading="aiLoading"
          @click="handleAIRewrite"
        >
          开始 AI 改写
        </n-button>
      </n-space>
    </n-modal>

    <n-space vertical size="large">
      <!-- Title -->
      <n-card>
        <n-input
          v-model:value="formData.title"
          placeholder="请输入文章标题"
          size="large"
          clearable
        />
      </n-card>

      <!-- Editor -->
      <n-card>
        <RichTextEditor
          :model-value="formData.content || ''"
          @update:model-value="formData.content = $event"
          placeholder="请输入文章内容..."
        />
      </n-card>

      <!-- Settings -->
      <n-grid :cols="2" :x-gap="24">
        <!-- Right Column -->
        <n-gi>
          <n-space vertical size="large">
            <!-- Categories -->
            <n-card title="分类">
              <n-select
                v-model:value="categoryIds"
                :options="categoryOptions"
                multiple
                placeholder="选择分类"
              />
            </n-card>

            <!-- Tags -->
            <n-card title="标签">
              <n-select
                v-model:value="tagIds"
                :options="tagOptions"
                multiple
                placeholder="选择标签"
                tag
              />
            </n-card>

            <!-- Cover Image -->
            <n-card title="封面图片">
              <div class="cover-upload">
                <n-upload
                  :action="uploadUrl"
                  :headers="uploadHeaders"
                  :show-file-list="false"
                  @finish="handleCoverUpload"
                >
                  <n-button block>
                    <template #icon>
                      <n-icon :component="CloudUploadOutline" />
                    </template>
                    上传封面
                  </n-button>
                </n-upload>

                <div v-if="formData.cover_image" class="cover-preview">
                  <img :src="formData.cover_image" alt="封面" />
                  <n-button
                    size="small"
                    type="error"
                    @click="formData.cover_image = ''"
                  >
                    移除
                  </n-button>
                </div>
              </div>
            </n-card>
          </n-space>
        </n-gi>

        <!-- Left Column -->
        <n-gi>
          <n-space vertical size="large">
            <!-- Description -->
            <n-card title="文章摘要">
              <n-input
                v-model:value="formData.description"
                type="textarea"
                placeholder="请输入文章摘要"
                :rows="4"
                maxlength="200"
                show-count
              />
            </n-card>

            <!-- Slug -->
            <n-card title="文章别名">
              <n-input
                v-model:value="formData.slug"
                placeholder="自定义文章别名（用于 URL）"
                clearable
              />
            </n-card>

            <!-- Status -->
            <n-card title="发布设置">
              <n-space vertical>
                <n-radio-group v-model:value="formData.status">
                  <n-space>
                    <n-radio value="draft">草稿</n-radio>
                    <n-radio value="published">立即发布</n-radio>
                    <n-radio value="archived">归档</n-radio>
                  </n-space>
                </n-radio-group>

                <n-date-picker
                  v-model:value="formData.published_at"
                  type="datetime"
                  placeholder="选择发布时间"
                  style="width: 100%"
                />
              </n-space>
            </n-card>
          </n-space>
        </n-gi>
      </n-grid>
    </n-space>

    <!-- Image Upload Modal -->
    <n-modal v-model:show="showImageModal" preset="dialog" title="上传图片">
      <n-upload
        :action="uploadUrl"
        :headers="uploadHeaders"
        :show-file-list="false"
        @finish="handleImageUploadFinish"
      >
        <div class="upload-area">
          <n-icon :component="CloudUploadOutline" size="48" />
          <p>点击或拖拽图片到此处上传</p>
        </div>
      </n-upload>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  CloudUploadOutline,
  SparklesOutline,
} from '@vicons/ionicons5'
import { adminArticleApi, adminCategoryApi, adminTagApi, uploadApi } from '@/api'
import type { Article } from '@/types'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import { renderArticleContent } from '@/utils/markdown'

const router = useRouter()
const route = useRoute()
const message = useMessage()

const isEdit = computed(() => !!route.params.slug)
const saving = ref(false)
const showImageModal = ref(false)

// AI 改写相关
const showAIRewriteModal = ref(false)
const aiSourceUrl = ref('')
const aiRewriteStrategy = ref('standard')
const aiTemplateType = ref('tutorial')
const aiLoading = ref(false)

const rewriteStrategyOptions = [
  { label: '标准改写', value: 'standard' },
  { label: '深度改写', value: 'deep' },
  { label: '创意改写', value: 'creative' },
]

const templateTypeOptions = [
  { label: '教程类', value: 'tutorial' },
  { label: '概念类', value: 'concept' },
  { label: '对比类', value: 'comparison' },
  { label: '实战类', value: 'practice' },
]

const formData = reactive<Partial<Article>>({
  title: '',
  slug: '',
  description: '',
  content: '',
  cover_image: '',
  status: 'draft',
  categories: [],
  tags: [],
  published_at: undefined,
})

// 本地使用的分类 ID 列表
const categoryIds = ref<number[]>([])
// 本地使用的标签 ID 列表
const tagIds = ref<number[]>([])

const categoryOptions = ref<any[]>([])
const tagOptions = ref<any[]>([])

const uploadUrl = '/api/v1/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`,
}))

const handleUploadImage = () => {
  showImageModal.value = true
}

const handleImageUploadFinish = ({ event }: any) => {
  const response = JSON.parse(event.target.response)
  const imageUrl = response.url
  message.success('图片上传成功')
  showImageModal.value = false
}

const handleCoverUpload = ({ event }: any) => {
  const response = JSON.parse(event.target.response)
  formData.cover_image = response.url
  message.success('封面上传成功')
}

// 准备保存的数据
const prepareSaveData = () => {
  const saveData: any = {
    title: formData.title,
    slug: formData.slug,
    description: formData.description,
    content: formData.content,
    cover_image: formData.cover_image,
    status: formData.status,
    published_at: formData.published_at,
    categoryIds: categoryIds.value,
    tagIds: tagIds.value,
  }
  return saveData
}

const handleSaveDraft = async () => {
  saving.value = true
  try {
    const saveData = prepareSaveData()
    saveData.status = 'draft'
    if (isEdit.value) {
      await adminArticleApi.update(route.params.slug as string, saveData)
    } else {
      await adminArticleApi.create(saveData)
    }
    message.success('草稿保存成功')
  } catch (error) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handlePublish = async () => {
  if (!formData.title) {
    message.warning('请输入文章标题')
    return
  }

  saving.value = true
  try {
    const saveData = prepareSaveData()
    saveData.status = 'published'
    saveData.published_at = new Date().toISOString()
    if (isEdit.value) {
      await adminArticleApi.update(route.params.slug as string, saveData)
    } else {
      await adminArticleApi.create(saveData)
    }
    message.success('文章发布成功')
    router.push('/admin/articles')
  } catch (error) {
    message.error('发布失败')
  } finally {
    saving.value = false
  }
}

const handleAIRewrite = async () => {
  if (!aiSourceUrl.value) {
    message.warning('请输入文章链接')
    return
  }
  
  aiLoading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch('/api/admin/articles/ai-rewrite', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        sourceUrl: aiSourceUrl.value,
        rewriteStrategy: aiRewriteStrategy.value,
        templateType: aiTemplateType.value,
        autoPublish: false,
      }),
    })
    
    const result = await response.json()
    
    if (result.success) {
      message.success('AI 改写任务已创建，请在 AI 改写页面查看进度')
      showAIRewriteModal.value = false
      router.push('/admin/ai-generator')
    } else {
      message.error(result.message || 'AI 改写失败')
    }
  } catch (error) {
    message.error('AI 改写请求失败')
  } finally {
    aiLoading.value = false
  }
}

const loadArticle = async () => {
  if (!isEdit.value) return
  try {
    const response = await adminArticleApi.getDetail(route.params.slug as string)
    const article = response.data
    Object.assign(formData, {
      title: article.title,
      slug: article.slug,
      description: article.description,
      content: renderArticleContent(article.content || ''),
      cover_image: article.cover_image,
      status: article.status,
      published_at: article.published_at,
    })
    // 转换分类和标签为 ID 列表
    categoryIds.value = article.categories?.map((c: any) => c.id) || []
    tagIds.value = article.tags?.map((t: any) => t.id) || []
  } catch (error) {
    message.error('加载文章失败')
  }
}

const loadCategories = async () => {
  try {
    const response = await adminCategoryApi.getList()
    categoryOptions.value = response.data.map((c: any) => ({
      label: c.name,
      value: c.id,
    }))
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const loadTags = async () => {
  try {
    const response = await adminTagApi.getList()
    tagOptions.value = response.data.map((t: any) => ({
      label: t.name,
      value: t.id,
    }))
  } catch (error) {
    console.error('Failed to load tags:', error)
  }
}

onMounted(() => {
  loadArticle()
  loadCategories()
  loadTags()
})
</script>

<style scoped>
.article-edit-page {
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

.header-right {
  display: flex;
  gap: 12px;
}

.editor-container {
  position: relative;
}

.editor-toolbar {
  margin-bottom: 16px;
}

.preview {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 16px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow-y: auto;
  max-height: 600px;
}

.cover-upload {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cover-preview {
  position: relative;
}

.cover-preview img {
  width: 100%;
  border-radius: 8px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.upload-area:hover {
  border-color: #18a058;
}

.upload-area p {
  margin: 16px 0 0 0;
  color: #666;
}
</style>
