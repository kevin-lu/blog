# AI 批量改写使用指南

## 功能概述

支持微信公众号文章合集批量抓取和 AI 改写，自动并发控制（2 个任务同时处理），改写后保存到草稿箱。

## 快速开始

### 1. 配置 API Key

复制 `.env.example` 为 `.env`，并配置 MiniMax API Key:

```bash
# 后端/.env
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_MODEL=MiniMax-M2.7

# AI 队列配置
AI_CONCURRENT_LIMIT=2          # 最大并发数
AI_REQUEST_DELAY=2             # 请求间隔 (秒)
AI_MAX_RETRIES=2               # 最大重试次数
AI_TIMEOUT=300                 # 超时时间 (秒)
```

获取 API Key：访问 https://platform.minimaxi.com/ 注册并创建

### 2. 启动服务

```bash
# 后端
cd backend
source venv/bin/activate
python run.py

# 前端
cd frontend
npm run dev
```

访问 `http://localhost:5173/admin/articles/ai-generator` 开始使用

### 3. 使用流程

#### 单篇改写

1. 在"单篇改写"标签页输入微信文章链接
2. 选择改写策略和模板类型
3. 点击"开始改写"
4. 实时查看进度，完成后自动跳转到编辑页面

#### 批量改写

1. 切换到"批量改写"标签页
2. 输入微信合集链接，例如:
   ```
   https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkzMDI1NjcyOQ==&action=getalbum&album_id=3022691668057276419
   ```
3. 点击"抓取文章列表"
4. 选择需要改写的文章（支持全选）
5. 选择改写策略和模板类型
6. 点击"开始批量改写"
7. 系统自动处理，保存到草稿箱

## API 接口

### 批量改写接口

**POST** `/api/v1/articles/ai-batch`

**请求体:**
```json
{
  "albumUrl": "https://mp.weixin.qq.com/mp/appmsgalbum?...",
  "rewriteStrategy": "standard",
  "templateType": "tutorial",
  "autoPublish": false
}
```

或指定文章列表:
```json
{
  "sourceUrls": [
    "https://mp.weixin.qq.com/s/xxx",
    "https://mp.weixin.qq.com/s/yyy"
  ],
  "rewriteStrategy": "standard",
  "templateType": "tutorial",
  "autoPublish": false
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "total": 10,
    "tasks": [
      {
        "queueId": "ai_abc123",
        "title": "文章标题",
        "url": "https://...",
        "status": "pending"
      }
    ],
    "concurrentLimit": 2
  }
}
```

### 获取合集文章列表

**GET** `/api/v1/articles/album/articles?url=<合集链接>`

**响应:**
```json
{
  "success": true,
  "data": {
    "album": {
      "name": "AI",
      "total_count": 32,
      "description": "...",
      "cover_image": "..."
    },
    "articles": [
      {
        "index": 1,
        "title": "文章标题",
        "url": "https://...",
        "msgid": "2247507305"
      }
    ]
  }
}
```

## 并发控制

### 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `AI_CONCURRENT_LIMIT` | 2 | 最大并发处理数 |
| `AI_REQUEST_DELAY` | 2 | 请求间隔 (秒) |
| `AI_MAX_RETRIES` | 2 | 失败重试次数 |
| `AI_TIMEOUT` | 300 | 超时时间 (秒) |

### 工作原理

1. **队列管理**: 所有改写任务加入数据库队列
2. **并发限制**: 最多 2 个任务同时处理
3. **请求延迟**: 每个任务调用 AI 前延迟 2 秒，避免触发 API 限流
4. **失败重试**: 失败任务自动重试 2 次
5. **草稿保存**: 所有改写结果保存到草稿箱，需人工审核

### 优势

- ✅ 避免触发 MiniMax API 限流
- ✅ 稳定的改写质量
- ✅ 失败自动重试
- ✅ 人工审核确保质量

## 成本估算

### MiniMax API 定价

- 输入：$0.3 / 百万 tokens
- 输出：$1.2 / 百万 tokens

### 单篇成本

- 3000 字文章：约 ¥0.016
- 5000 字文章：约 ¥0.027

### 批量成本

| 文章数 | 预估成本 |
|--------|---------|
| 10 篇 | ¥0.16 |
| 20 篇 | ¥0.32 |
| 50 篇 | ¥0.80 |

## 改写策略

### 标准改写 (standard)
- 保留核心观点，完全重写表达
- 语言风格自然，像朋友讲技术
- 适合大多数技术文章

### 深度改写 (deep)
- 添加案例分析和对比
- 强调原理、优缺点和落地建议
- 增加"最佳实践"、"避坑指南"章节

### 创意改写 (creative)
- 只保留主题，完全独立创作
- 文风轻松，有个人观点
- 适合灵感类文章

## 最佳实践

### 1. 分批处理
- 建议每批 10-20 篇
- 避免大量任务积压
- 可根据并发数调整批次

### 2. 人工审核
- 所有改写保存到草稿箱
- 人工审核技术准确性
- 添加个人见解和案例
- 检查代码示例正确性

### 3. 发布频率
- 建议每天 3-5 篇
- 避免短时间大量发布
- 保持稳定的更新节奏

### 4. SEO 优化
- 优化标题和描述
- 添加合适的标签和分类
- 添加原创内容比例 (建议 30% 以上)

## 常见问题

### Q: 抓取失败怎么办？

**A:** 检查以下几点:
1. 链接是否有效 (在浏览器中打开测试)
2. 文章是否需要权限访问
3. 网络连接是否正常
4. 稍后重试

### Q: 任务卡住不动？

**A:** 
1. 查看后端日志确认错误信息
2. 可能是 API 调用超时
3. 系统会自动重试 (最多 2 次)
4. 检查 MiniMax API Key 是否有效

### Q: 如何调整并发数？

**A:** 
修改 `.env` 文件:
```bash
AI_CONCURRENT_LIMIT=3  # 改为 3 个并发
```
重启后端服务生效。

### Q: 改写质量不满意？

**A:** 
1. 尝试更换改写策略 (标准/深度/创意)
2. 手动编辑优化
3. 调整 Prompt 模板 (需修改代码)
4. 添加更多个人见解

### Q: 批量改写能否直接发布？

**A:** 
当前设计全部保存到草稿箱，如需自动发布:
1. 修改前端 `autoPublish: true`
2. 后端会直接发布文章
3. **不建议**，建议人工审核

## 版权说明

本系统采用"保留核心观点 + 完全重写表达"的方式，确保:

- ✅ 只提取技术要点和核心思路
- ✅ 完全使用自己的表达方式
- ✅ 添加原创案例和代码示例
- ✅ 改变文章结构和叙述逻辑

**注意:** 
- 尊重原作者知识产权
- 建议添加原文引用
- 不要用于商业侵权

## 技术支持

如有问题，请查看:
- 后端日志：`backend/logs/`
- 前端控制台：浏览器开发者工具
- API 文档：`http://localhost:5000/apidocs/`
