<template>
  <div class="comment-section">
    <div class="section-header">
      <h3>评论</h3>
      <span class="comment-count" v-if="commentCount > 0">
        {{ commentCount }} 条评论
      </span>
    </div>

    <!-- 发表评论 -->
    <div class="post-comment">
      <CommentForm
        :article-slug="articleSlug"
        @success="handleCommentSuccess"
      />
    </div>

    <!-- 评论列表 -->
    <CommentList
      ref="commentListRef"
      :article-slug="articleSlug"
      @refresh="loadCommentCount"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { commentApi } from '@/api'
import CommentForm from './CommentForm.vue'
import CommentList from './CommentList.vue'

interface Props {
  articleSlug: string
}

const props = defineProps<Props>()

const commentCount = ref(0)
const commentListRef = ref<InstanceType<typeof CommentList> | null>(null)

const loadCommentCount = async () => {
  try {
    commentCount.value = await commentApi.getCommentCount(props.articleSlug)
  } catch (error) {
    console.error('Failed to load comment count:', error)
  }
}

const handleCommentSuccess = () => {
  loadCommentCount()
  commentListRef.value?.refresh()
}

onMounted(() => {
  loadCommentCount()
})
</script>

<style scoped>
.comment-section {
  margin-top: 60px;
  padding-top: 40px;
  border-top: 2px solid #f0f0f0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.section-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.comment-count {
  font-size: 14px;
  color: #999;
}

.post-comment {
  margin-bottom: 32px;
}
</style>
