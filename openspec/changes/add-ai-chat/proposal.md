## Why

用户在管理后台需要一个 AI 聊天功能，可以直接调用 MiniMax API 进行智能对话。这个功能可以让博主在管理博客时快速获取 AI 辅助，比如获取写作灵感、技术建议或内容优化建议。

## What Changes

- **新增**: 管理后台左侧菜单增加"AI 聊天"菜单项
- **新增**: AI 聊天页面，包含对话输入框和消息展示区域
- **新增**: 后端 API 端点用于调用 MiniMax AI 接口
- **新增**: 消息复制功能，方便用户复制 AI 回复内容
- **新增**: 对话历史展示（当前会话）

## Capabilities

### New Capabilities
- `ai-chat-api`: 后端 AI 聊天 API，调用 MiniMax 接口处理用户消息
- `ai-chat-ui`: 前端 AI 聊天界面，包含输入框、消息列表和复制功能

### Modified Capabilities
- `admin-navigation`: 管理后台导航菜单需要增加 AI 聊天入口

## Impact

- **后端**: 
  - 新增 `/api/v1/ai/chat` 端点
  - 复用现有的 MiniMax API 配置
  - 需要处理流式响应（可选优化）
  
- **前端**:
  - 新增 Admin 布局的菜单项
  - 新增 AI 聊天页面组件
  - 使用 Naive UI 的对话框和消息组件
  
- **配置**:
  - 复用 `.env` 中的 `MINIMAX_API_KEY` 配置
  - 无需新增环境变量

- **依赖**:
  - 后端：使用已有的 `minimax` 相关配置
  - 前端：Naive UI 组件库
