# AI Chat API Specification

## Overview

后端 AI 聊天 API，调用 MiniMax 接口处理用户消息。

## Endpoint

```
POST /api/v1/ai/chat
```

## Authentication

需要 JWT 认证（`Authorization: Bearer <token>`）

## Request

### Headers

```
Content-Type: application/json
Authorization: Bearer <JWT token>
```

### Body

```json
{
  "message": "用户输入的问题或对话内容",
  "conversation_history": [
    {
      "role": "user",
      "content": "之前的问题"
    },
    {
      "role": "assistant",
      "content": "之前的回答"
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message` | string | 是 | 用户当前输入的消息 |
| `conversation_history` | array | 否 | 对话历史，用于上下文理解 |

## Response

### Success (200)

```json
{
  "reply": "AI 助手的回复内容",
  "model": "MiniMax-M2.7",
  "usage": {
    "total_tokens": 150
  }
}
```

### Error Responses

#### 400 - Bad Request

```json
{
  "error": "Message is required"
}
```

#### 401 - Unauthorized

```json
{
  "error": "Missing or invalid token"
}
```

#### 500 - Internal Server Error

```json
{
  "error": "Failed to get AI response"
}
```

## Rate Limiting

- 默认：`30 per minute`（开发环境）
- 默认：`5 per hour`（生产环境）
- 复用现有 `RATELIMIT_DEFAULT` 配置

## Implementation Details

### MiniMax API 调用

使用环境变量配置：
- `MINIMAX_API_KEY`
- `MINIMAX_MODEL`（默认：`MiniMax-M2.7`）
- `MINIMAX_API_HOST`（默认：`https://api.minimaxi.com/v1/chat/completions`）
- `MINIMAX_REQUEST_TIMEOUT`（默认：300 秒）

### 请求格式

调用 MiniMax API 时的消息格式：

```python
messages = [
    {
        "role": "user",
        "content": "用户消息"
    }
]

# 如果有对话历史
if conversation_history:
    messages = conversation_history + [{"role": "user", "content": message}]
```

### 错误处理

- MiniMax API 调用失败时返回友好的错误信息
- 记录详细的错误日志（后端）
- 不暴露 API Key 等敏感信息
