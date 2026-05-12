<template>
  <div class="ai-chat-floating">
    <!-- 悬浮按钮 -->
    <div
      v-if="!isOpen"
      class="floating-button"
      @click="toggleChat"
    >
      <n-badge :value="unreadCount" :show="unreadCount > 0">
        <n-button circle size="large" type="primary">
          <template #icon>
            <n-icon :component="SparklesOutline" size="24" />
          </template>
        </n-button>
      </n-badge>
    </div>

    <!-- 聊天窗口 -->
    <div v-else class="chat-window">
      <!-- 窗口头部 -->
      <div class="window-header">
        <div class="header-left">
          <n-icon :component="SparklesOutline" size="20" class="header-icon" />
          <span class="title">AI 助手</span>
        </div>
        <div class="header-right">
          <n-button text @click="clearConversation" title="清空对话">
            <template #icon>
              <n-icon :component="RefreshOutline" size="18" />
            </template>
          </n-button>
          <n-button text @click="toggleChat" title="关闭">
            <template #icon>
              <n-icon :component="CloseOutline" size="20" />
            </template>
          </n-button>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-avatar">
            <n-icon v-if="msg.role === 'assistant'" size="20">
              <SparklesOutline />
            </n-icon>
            <n-icon v-else size="20">
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
                  <n-icon size="14">
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
            <n-icon size="20">
              <SparklesOutline />
            </n-icon>
          </div>
          <div class="message-content">
            <n-spin size="small" description="AI 思考中..." />
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="messages.length === 0 && !loading" class="empty-state">
          <n-icon size="48" color="#ccc">
            <ChatbubblesOutline />
          </n-icon>
          <p>开始与 AI 助手对话吧！</p>
          <p class="hint">输入问题，按 Ctrl+Enter 发送</p>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <n-input
          v-model:value="inputMessage"
          type="textarea"
          placeholder="输入你的问题...（按 Ctrl+Enter 发送）"
          :rows="2"
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useMessage } from 'naive-ui'
import {
  SparklesOutline,
  PersonOutline,
  CopyOutline,
  ChatbubblesOutline,
  PaperPlaneOutline,
  CloseOutline,
  RefreshOutline,
} from '@vicons/ionicons5'
import { aiChatApi, type ChatMessage } from '@/api/aiChat'

const message = useMessage()

const isOpen = ref(false)
const unreadCount = ref(0)
const messages = ref<ChatMessage[]>([])
const inputMessage = ref('')
const sending = ref(false)
const loading = ref(false)
const messageListRef = ref<HTMLElement | null>(null)

// 切换聊天窗口开关
const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    unreadCount.value = 0
    nextTick(() => {
      scrollToBottom()
    })
  }
}

// 清空对话
const clearConversation = () => {
  messages.value = []
  message.success('已清空对话')
}

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
    
    // 增加未读数（如果窗口关闭）
    if (!isOpen.value) {
      unreadCount.value += 1
    }
    
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
.ai-chat-floating {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
}

.floating-button {
  cursor: pointer;
  transition: transform 0.2s;
  
  &:hover {
    transform: scale(1.1);
  }
  
  :deep(.n-button) {
    width: 56px;
    height: 56px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}

.chat-window {
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.window-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .header-icon {
      opacity: 0.9;
    }
    
    .title {
      font-weight: 600;
      font-size: 16px;
    }
  }
  
  .header-right {
    display: flex;
    gap: 4px;
    
    :deep(.n-button) {
      color: white;
      
      &:hover {
        background: rgba(255, 255, 255, 0.2);
      }
    }
  }
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f9f9f9;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #ddd;
    border-radius: 3px;
    
    &:hover {
      background: #ccc;
    }
  }
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  
  &.user {
    flex-direction: row-reverse;
    
    .message-content {
      align-items: flex-end;
    }
    
    .message-text {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border-radius: 12px 12px 0 12px;
    }
  }
  
  &.assistant {
    .message-text {
      background: white;
      color: #333;
      border-radius: 12px 12px 12px 0;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
  }
}

.message-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
  
  .user & {
    background: linear-gradient(135deg, #18a058 0%, #0d7a4a 100%);
    color: white;
  }
  
  .assistant & {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
}

.message-content {
  display: flex;
  flex-direction: column;
  max-width: 75%;
}

.message-text {
  padding: 10px 14px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

.message-actions {
  margin-top: 6px;
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
  text-align: center;
  
  p {
    margin-top: 16px;
    font-size: 14px;
    
    &.hint {
      font-size: 12px;
      color: #bbb;
      margin-top: 8px;
    }
  }
}

.input-area {
  padding: 12px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 8px;
  background: white;
  
  :deep(.n-input) {
    flex: 1;
    
    .n-input__textarea {
      resize: none;
      font-size: 14px;
    }
  }
  
  :deep(.n-button) {
    min-width: 80px;
  }
}
</style>
