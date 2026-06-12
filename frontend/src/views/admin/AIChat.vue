<template>
  <div class="ai-chat-page">
    <div class="page-header">
      <h1>AI 聊天助手</h1>
      <p class="page-description">与 AI 助手对话，获取灵感和建议</p>
    </div>

    <n-card class="chat-container">
      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-avatar">
            <n-icon v-if="msg.role === 'assistant'" size="24">
              <SparklesOutline />
            </n-icon>
            <n-icon v-else size="24">
              <PersonOutline />
            </n-icon>
          </div>
          
          <div class="message-content">
            <div class="message-text">{{ msg.content }}</div>
            
            <!-- AI 消息的复制按钮 -->
            <div v-if="msg.role === 'assistant'" class="message-actions">
              <n-button
                text
                type="primary"
                size="small"
                @click="copyMessage(msg.content)"
              >
                <template #icon>
                  <n-icon size="16">
                    <CopyOutline />
                  </n-icon>
                </template>
                复制
              </n-button>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="message assistant">
          <div class="message-avatar">
            <n-icon size="24">
              <SparklesOutline />
            </n-icon>
          </div>
          <div class="message-content">
            <n-spin size="small" description="AI 思考中..." />
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="messages.length === 0 && !loading" class="empty-state">
          <n-icon size="64" color="#ccc">
            <ChatbubblesOutline />
          </n-icon>
          <p>开始与 AI 助手对话吧！</p>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <n-input
          v-model:value="inputMessage"
          type="textarea"
          placeholder="输入你的问题...（按 Ctrl+Enter 发送）"
          :rows="3"
          :disabled="sending"
          @keydown="handleKeyDown"
        />
        <n-button
          type="primary"
          :loading="sending"
          :disabled="!inputMessage.trim()"
          @click="sendMessage"
        >
          <template #icon>
            <n-icon>
              <PaperPlaneOutline />
            </n-icon>
          </template>
          发送
        </n-button>
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useMessage } from 'naive-ui'
import {
  PersonOutline,
  CopyOutline,
  ChatbubblesOutline,
  PaperPlaneOutline,
  SparklesOutline,
} from '@vicons/ionicons5'
import { aiChatApi, type ChatMessage } from '@/api/aiChat'

const message = useMessage()

const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const sending = ref(false)
const loading = ref(false)
const messageListRef = ref<HTMLElement | null>(null)

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

// 复制消息
const copyMessage = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    message.success('已复制到剪贴板')
  } catch (error) {
    message.error('复制失败')
  }
}

// 处理键盘事件
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    sendMessage()
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim() || sending.value) return

  sending.value = true
  const messageText = inputMessage.value
  
  try {
    // 添加用户消息
    const userMessage: ChatMessage = {
      role: 'user',
      content: messageText,
    }
    messages.value.push(userMessage)
    
    inputMessage.value = ''
    
    await scrollToBottom()
    
    // 调用 API
    loading.value = true
    const response = await aiChatApi.chat(messageText)
    
    // 添加 AI 回复
    messages.value.push({
      role: 'assistant',
      content: response.reply,
    })
    
    await scrollToBottom()
  } catch (error: any) {
    message.error(error.response?.data?.error || '发送失败，请重试')
    // 发送失败时恢复输入
    inputMessage.value = messageText
  } finally {
    sending.value = false
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.ai-chat-page {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
  
  h1 {
    margin: 0 0 8px 0;
    font-size: 24px;
    font-weight: 600;
  }
  
  .page-description {
    margin: 0;
    color: #666;
    font-size: 14px;
  }
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
  min-height: 500px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  
  &.user {
    flex-direction: row-reverse;
    
    .message-content {
      align-items: flex-end;
    }
    
    .message-text {
      background-color: #18a058;
      color: white;
      border-radius: 12px 12px 0 12px;
    }
  }
  
  &.assistant {
    .message-text {
      background-color: white;
      color: #333;
      border-radius: 12px 12px 12px 0;
    }
  }
}

.message-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e0e0e0;
  flex-shrink: 0;
  
  .user & {
    background-color: #18a058;
    color: white;
  }
  
  .assistant & {
    background-color: #2080f0;
    color: white;
  }
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-text {
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

.message-actions {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  
  p {
    margin-top: 16px;
    font-size: 16px;
  }
}

.input-area {
  display: flex;
  gap: 12px;
  
  :deep(.n-input) {
    flex: 1;
  }
  
  :deep(.n-button) {
    min-width: 100px;
  }
}
</style>
