## 1. 后端 API 实现

- [x] 1.1 创建 AI Chat API 路由文件 `backend/app/api/v1/ai_chat.py`
- [x] 1.2 实现 `POST /api/v1/ai/chat` 端点
- [x] 1.3 添加 MiniMax API 调用逻辑
- [x] 1.4 实现请求验证和错误处理
- [x] 1.5 添加速率限制（复用现有配置）
- [x] 1.6 注册 API 蓝图到 `backend/app/api/v1/__init__.py`

## 2. 前端 API 客户端

- [x] 2.1 创建 API 类型定义 `frontend/src/api/aiChat.ts`
- [x] 2.2 实现 `aiChatApi.chat()` 方法
- [x] 2.3 添加错误处理和类型检查

## 3. 前端 UI 组件

- [x] 3.1 创建 AI Chat 页面 `frontend/src/views/admin/AIChat.vue`
- [x] 3.2 实现消息列表组件
- [x] 3.3 实现输入框和发送按钮
- [x] 3.4 实现复制功能（复制到剪贴板）
- [x] 3.5 添加加载状态和错误提示
- [x] 3.6 实现自动滚动到最新消息

## 4. 管理后台集成

- [x] 4.1 更新管理后台布局 `frontend/src/components/layout/AdminLayout.vue`
- [x] 4.2 添加 AI 聊天菜单项
- [x] 4.3 配置路由 `frontend/src/router/index.ts`

## 5. 测试和验证

- [x] 5.1 测试 API 端点（使用 curl 或 Postman）
- [x] 5.2 测试前端发送消息功能
- [x] 5.3 测试复制功能
- [x] 5.4 测试错误处理场景
- [x] 5.5 验证响应式布局
