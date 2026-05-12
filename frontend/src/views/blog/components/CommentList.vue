<template>
  <div class="comment-list">
    <div v-if="loading" class="loading">
      <n-spin size="small" />
    </div>

    <div v-else-if="comments.length === 0" class="empty">
      <n-empty description="暂无评论，快来抢沙发吧" />
    </div>

    <div v-else class="comments">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        @reply-success="$emit('refresh')"
      />
    </div>

    <div v-if="total > pageSize" class="pagination">
      <n-pagination
        v-model:page="currentPage"
        :item-count="total"
        :page-size="pageSize"
        @update-page="loadComments"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { commentApi } from '@/api'
import type { Comment } from '@/types'
import CommentItem from './CommentItem.vue'

interface Props {
  articleSlug: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const message = useMessage()

const loading = ref(false)
const comments = ref<Comment[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const loadComments = async (page: number = currentPage.value) => {
  loading.value = true
  try {
    const result = await commentApi.getArticleComments(props.articleSlug, {
      page,
      limit: pageSize.value,
    })
    comments.value = result.comments
    total.value = result.total
    currentPage.value = page
  } catch (error) {
    console.error('Failed to load comments:', error)
    message.error('加载评论失败')
  } finally {
    loading.value = false
  }
}

const refresh = () => {
  loadComments(currentPage.value)
  emit('refresh')
}

onMounted(() => {
  loadComments()
})

defineExpose({ refresh })
</script>

<style scoped>
.comment-list {
  margin-top: 24px;
}

.loading,
.empty {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}

.comments {
  margin-top: 16px;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
