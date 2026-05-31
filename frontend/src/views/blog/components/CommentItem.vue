<template>
  <div class="comment-item" :class="{ 'is-reply': isReply }">
    <div class="comment-header">
      <n-avatar :size="32" round>
        <template #icon>
          {{ getAvatarText(comment.author_name) }}
        </template>
      </n-avatar>
      <div class="comment-meta">
        <span class="author-name">{{ comment.author_name || '匿名用户' }}</span>
        <span v-if="comment.reply_to" class="reply-to">
          回复 @{{ comment.reply_to }}
        </span>
      </div>
      <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
    </div>

    <div class="comment-content">
      {{ comment.content }}
    </div>

    <div class="comment-actions">
      <n-button text size="small" @click="handleReply">
        回复
      </n-button>
    </div>

    <!-- 回复表单 -->
    <div v-if="showReplyForm" class="reply-form">
      <CommentForm
        :article-slug="comment.article_slug"
        :parent-id="comment.id"
        :reply-to="comment.author_name || '匿名用户'"
        :is-reply="true"
        @success="handleReplySuccess"
        @cancel="showReplyForm = false"
      />
    </div>

    <!-- 回复列表 -->
    <div v-if="comment.replies && comment.replies.length > 0" class="replies">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :is-reply="true"
        @reply-success="handleReplySuccess"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { formatDate } from '@/utils/date'
import type { Comment } from '@/types'
import CommentForm from './CommentForm.vue'

interface Props {
  comment: Comment
  isReply?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isReply: false,
})

const emit = defineEmits<{
  (e: 'reply-success'): void
}>()

const showReplyForm = ref(false)

const getAvatarText = (name: string | undefined) => {
  return name ? name.charAt(0).toUpperCase() : '?'
}

const handleReply = () => {
  showReplyForm.value = true
}

const handleReplySuccess = () => {
  showReplyForm.value = false
  emit('reply-success')
}
</script>

<style scoped>
.comment-item {
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}

.is-reply {
  padding-left: 48px;
  background: #f9f9f9;
  margin: 8px 0;
  border-radius: 8px;
  padding: 12px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.comment-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.author-name {
  font-weight: 600;
  color: #333;
}

.reply-to {
  font-size: 12px;
  color: #999;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-content {
  margin-bottom: 12px;
  line-height: 1.6;
  color: #333;
}

.comment-actions {
  display: flex;
  gap: 8px;
}

.replies {
  margin-top: 12px;
}

.reply-form {
  margin-top: 12px;
}
</style>
