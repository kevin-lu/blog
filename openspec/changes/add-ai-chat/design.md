## Context

**背景：**
- 项目已有 MiniMax AI 配置（`MINIMAX_API_KEY` 等环境变量）
- 管理后台使用 Vue 3 + Naive UI 构建
- 后端使用 Flask + JWT 认证
- 需要一个 AI 聊天界面供博主在管理后台使用

**当前状态：**
- 后端有 AI 相关配置但未暴露聊天 API
- 前端管理后台有完善的布局组件和菜单系统
- 已有 API 调用模式和错误处理机制

**约束：**
- 复用现有 MiniMax 配置，不新增环境变量
- 遵循现有代码风格和架构模式
- 保持与现有管理后台 UI 一致

## Goals / Non-Goals

**Goals:**
- 在管理后台左侧菜单添加"AI 聊天"入口
- 实现完整的对话界面（输入框、发送按钮、消息列表）
- 后端调用 MiniMax API 处理用户消息
- 支持复制 AI 回复内容
- 显示加载状态和错误提示

**Non-Goals:**
- 不支持多轮对话历史持久化（仅当前会话）
- 不支持流式响应（首版使用完整响应）
- 不支持自定义 AI 模型参数（使用默认配置）
- 不支持文件/图片上传

## Decisions

### 1. API 设计：RESTful vs WebSocket

**决策：** 使用 RESTful API（`POST /api/v1/ai/chat`）

**理由：**
- 与现有 API 架构一致
- 实现简单，无需额外依赖
- 对于聊天场景，轮询足够

**替代方案：** WebSocket 实现实时流式响应
- 优点：更好的用户体验
- 缺点：增加复杂度，需要管理连接状态

### 2. 前端状态管理

**决策：** 使用 Vue 3 Composition API + 本地 state

**理由：**
- 聊天状态不需要跨页面共享
- 简单的响应式数据足够
- 与现有代码风格一致

### 3. 消息格式

**决策：** 
```typescript
interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}
```

**理由：**
- 与 MiniMax API 格式兼容
- 简单清晰，易于扩展

### 4. 错误处理

**决策：** 
- 后端：统一错误响应格式 `{ error: string }`
- 前端：使用 Naive UI 的 `message` 组件显示错误

## Risks / Trade-offs

### 风险

1. **API 调用频率限制**
   - → 前端添加发送按钮禁用机制
   - → 后端复用现有的 rate limiting

2. **长响应时间**
   - → 显示加载状态
   - → 设置合理的超时时间

3. **敏感信息泄露**
   - → API Key 存储在环境变量，不暴露给前端
   - → 后端代理所有 AI 请求

### 权衡

- **不支持流式响应**：首版简化实现，后续可优化
- **不持久化对话历史**：减少数据库复杂度，专注核心功能
