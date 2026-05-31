# AI Chat UI Specification

## Overview

前端 AI 聊天界面，提供对话输入框、消息展示和复制功能。

## Location

- 路由：`/admin/ai-chat`
- 组件：`frontend/src/views/admin/AIChat.vue`
- 菜单：管理后台左侧菜单新增"AI 聊天"项

## Layout

```
┌─────────────────────────────────────┐
│  AI 聊天助手                         │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 🤖 你好！我是你的 AI 助手      │   │
│  │    有什么可以帮你的吗？       │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ 用户问题                     │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ AI 回复内容                  │   │
│  │ [复制按钮] 📋                │   │
│  └─────────────────────────────┘   │
│                                     │
├─────────────────────────────────────┤
│  ┌───────────────────────────┐     │
│  │ 输入你的问题...    [发送] │     │
│  └───────────────────────────┘     │
└─────────────────────────────────────┘
```

## Components

### 1. 消息列表区

**组件：** `n-card` + 自定义消息气泡

**样式：**
- 用户消息：右对齐，蓝色背景
- AI 消息：左对齐，灰色背景

**功能：**
- 显示对话历史
- 自动滚动到最新消息
- 加载时显示 loading 状态

### 2. 输入框

**组件：** `n-input` (Naive UI)

**属性：**
- `type: "textarea"`
- `rows: 3`
- `placeholder: "输入你的问题..."`
- `disabled: sending || loading`

**快捷键：**
- `Ctrl/Cmd + Enter`：发送消息

### 3. 发送按钮

**组件：** `n-button`

**属性：**
- `type: "primary"`
- `disabled: !message.trim() || sending`
- `loading: sending`

**图标：** `PaperPlaneOutline` (Ionicons)

### 4. 复制按钮

**组件：** `n-button` (text 类型)

**位置：** 每条 AI 消息右下角

**功能：**
- 点击复制消息内容到剪贴板
- 复制成功后显示提示 "已复制"
- 使用 `navigator.clipboard.writeText()`

**图标：** `CopyOutline` (Ionicons)

## State Management

```typescript
interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

const messages = ref<Message[]>([])
const inputMessage = ref('')
const sending = ref(false)
const loading = ref(false)
```

## API Integration

### 调用方式

```typescript
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  sending.value = true
  try {
    // 添加用户消息到列表
    messages.value.push({
      role: 'user',
      content: inputMessage.value,
      timestamp: Date.now()
    })
    
    // 调用 API
    const response = await aiChatApi.chat(inputMessage.value)
    
    // 添加 AI 回复到列表
    messages.value.push({
      role: 'assistant',
      content: response.reply,
      timestamp: Date.now()
    })
    
    // 清空输入框
    inputMessage.value = ''
  } catch (error) {
    message.error('发送失败，请重试')
  } finally {
    sending.value = false
  }
}
```

## Error Handling

### API 错误

- **401**: 跳转登录页
- **400/500**: 显示错误提示 `message.error()`
- **网络错误**: 显示 "网络连接失败"

### 加载状态

- 发送中：禁用输入框和发送按钮，显示 loading 动画
- 等待回复：显示 "AI 思考中..." 提示

## Copy Functionality

```typescript
const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    message.success('已复制到剪贴板')
  } catch (error) {
    message.error('复制失败')
  }
}
```

## Responsive Design

- **桌面端**: 完整布局
- **移动端**: 调整内边距和字体大小
- 最小宽度：320px

## Accessibility

- 输入框有清晰的 label
- 按钮有 aria-label
- 支持键盘导航
- 错误信息可读

## Theme

复用现有 Naive UI 主题配置：
- 主色调：`primary`
- 成功色：`success`
- 错误色：`error`
