<template>
  <div class="article-like">
    <button
      :class="['like-button', { liked: isLiked, loading: isLoading }]"
      @click="handleLike"
      :disabled="isLoading"
      type="button"
    >
      <span class="like-icon">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          class="w-6 h-6"
        >
          <path
            d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z"
          />
        </svg>
      </span>
      <span class="like-count">{{ likeCount }}</span>
    </button>
    
    <transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div v-if="showToast" class="toast-notification">
        {{ toastMessage }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { likeArticle, unlikeArticle } from '@/api/like';

interface Props {
  articleId: number;
  initialLikeCount: number;
  initialLiked?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  initialLiked: false,
});

const emit = defineEmits<{
  (e: 'update', liked: boolean, likeCount: number): void;
}>();

const isLiked = ref(props.initialLiked);
const likeCount = ref(props.initialLikeCount);
const isLoading = ref(false);
const showToast = ref(false);
const toastMessage = ref('');

const showSuccessToast = (message: string) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 2000);
};

const showErrorToast = (message: string) => {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 2000);
};

const handleLike = async () => {
  if (isLoading.value) return;
  
  isLoading.value = true;
  
  const previousState = isLiked.value;
  const previousCount = likeCount.value;
  
  if (isLiked.value) {
    isLiked.value = false;
    likeCount.value = Math.max(0, likeCount.value - 1);
  } else {
    isLiked.value = true;
    likeCount.value = likeCount.value + 1;
  }
  
  try {
    let response;
    if (previousState) {
      response = await unlikeArticle(props.articleId);
    } else {
      response = await likeArticle(props.articleId);
    }
    
    isLiked.value = response.liked;
    likeCount.value = response.like_count;
    emit('update', response.liked, response.like_count);
    
    if (response.liked) {
      showSuccessToast('点赞成功');
    } else {
      showSuccessToast('已取消点赞');
    }
  } catch (error: any) {
    isLiked.value = previousState;
    likeCount.value = previousCount;
    
    if (error.response?.status === 409) {
      showErrorToast('您已点赞过这篇文章');
    } else if (error.response?.status === 429) {
      showErrorToast('操作过于频繁，请稍后再试');
    } else {
      showErrorToast('操作失败，请重试');
    }
  } finally {
    isLoading.value = false;
  }
};

watch(
  () => props.initialLikeCount,
  (newVal) => {
    likeCount.value = newVal;
  }
);

watch(
  () => props.initialLiked,
  (newVal) => {
    isLiked.value = newVal;
  }
);
</script>

<style scoped>
.article-like {
  position: relative;
  display: inline-block;
}

.like-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 9999px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.like-button:hover:not(:disabled) {
  border-color: #ef4444;
  background: #fef2f2;
}

.like-button.liked {
  border-color: #ef4444;
  background: #fef2f2;
}

.like-button.liked .like-icon {
  color: #ef4444;
}

.like-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.like-button.loading {
  position: relative;
}

.like-button.loading::after {
  content: '';
  position: absolute;
  width: 1rem;
  height: 1rem;
  border: 2px solid #e5e7eb;
  border-top-color: #ef4444;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  right: 0.75rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.like-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: #9ca3af;
  transition: color 0.2s;
}

.like-count {
  font-weight: 500;
  color: #374151;
}

.toast-notification {
  position: absolute;
  bottom: -3rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.5rem 1rem;
  background: #1f2937;
  color: white;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  white-space: nowrap;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

@media (max-width: 640px) {
  .like-button {
    padding: 0.375rem 0.75rem;
    font-size: 0.813rem;
  }
  
  .like-icon {
    width: 1rem;
    height: 1rem;
  }
}
</style>
