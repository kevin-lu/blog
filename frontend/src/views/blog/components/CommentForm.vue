<template>
  <div class="comment-form">
    <n-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-placement="top"
    >
      <n-form-item label="昵称" path="author_name">
        <n-input
          v-model:value="formData.author_name"
          placeholder="请输入昵称"
          clearable
        />
      </n-form-item>

      <n-form-item label="邮箱（选填）" path="author_email">
        <n-input
          v-model:value="formData.author_email"
          placeholder="用于显示 Gravatar 头像"
          clearable
        />
      </n-form-item>

      <n-form-item label="评论内容" path="content">
        <n-input
          v-model:value="formData.content"
          type="textarea"
          placeholder="写下你的评论..."
          :rows="4"
          show-count
          maxlength="1000"
        />
      </n-form-item>

      <n-form-item>
        <n-space>
          <n-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isReply ? '回复' : '发表评论' }}
          </n-button>
          <n-button v-if="isReply" @click="handleCancel">取消</n-button>
        </n-space>
      </n-form-item>
    </n-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useMessage } from 'naive-ui'
import type { FormRules } from 'naive-ui'
import { commentApi } from '@/api'

interface Props {
  articleSlug: string
  parentId?: number | null
  replyTo?: string | null
  isReply?: boolean
  onSuccess?: () => void
  onCancel?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  parentId: null,
  replyTo: null,
  isReply: false,
})

const emit = defineEmits<{
  (e: 'success'): void
  (e: 'cancel'): void
}>()

const message = useMessage()

const formData = reactive({
  author_name: '',
  author_email: '',
  content: '',
})

const formRules: FormRules = {
  author_name: {
    required: true,
    message: '请输入昵称',
    trigger: 'blur',
  },
  content: {
    required: true,
    message: '请输入评论内容',
    trigger: 'blur',
  },
}

const formRef = ref(null)
const submitting = ref(false)

const handleSubmit = async () => {
  try {
    submitting.value = true
    
    await commentApi.create({
      article_slug: props.articleSlug,
      content: formData.content,
      author_name: formData.author_name,
      author_email: formData.author_email || undefined,
      parent_id: props.parentId || undefined,
      reply_to: props.replyTo || undefined,
    })
    
    message.success(props.isReply ? '回复成功' : '评论成功')
    
    // 清空表单
    formData.content = ''
    if (!props.isReply) {
      formData.author_name = ''
      formData.author_email = ''
    }
    
    emit('success')
  } catch (error) {
    console.error('Failed to submit comment:', error)
    message.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  formData.content = ''
  emit('cancel')
}
</script>

<style scoped>
.comment-form {
  margin-bottom: 24px;
}
</style>
