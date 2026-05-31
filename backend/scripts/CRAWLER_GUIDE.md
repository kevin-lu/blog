# 自动文章抓取系统使用指南

## 功能概述

本系统支持从 RSS 源自动抓取技术文章，通过 AI 改写后自动发布到博客系统。

### 核心功能

- ✅ **RSS 抓取**: 支持掘金、博客园等 RSS 源
- ✅ **智能去重**: URL + 标题 MD5 双重去重
- ✅ **AI 改写**: MiniMax AI 串行改写，避免并发限制
- ✅ **定时任务**: 每天凌晨 2 点自动执行
- ✅ **队列管理**: 持久化队列，失败自动重试
- ✅ **API 管理**: 完整的 REST API 接口

---

## 快速开始

### 1. 手动触发抓取

```bash
# 使用 curl 测试
curl -X POST http://localhost:5000/api/v1/crawler/fetch \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source": "juejin", "limit": 10}'
```

**响应：**
```json
{
  "task_id": "fetch_20260513_203000_abc123",
  "status": "completed",
  "message": "抓取完成：发现 20 篇，新增 15 篇，入队 15 篇",
  "stats": {
    "found": 20,
    "new": 15,
    "queued": 15
  }
}
```

### 2. 查看队列状态

```bash
curl http://localhost:5000/api/v1/queue/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**响应：**
```json
{
  "pending": 15,
  "processing": 1,
  "completed": 120,
  "failed": 2,
  "estimated_time_minutes": 75.0
}
```

### 3. 查看队列列表

```bash
curl "http://localhost:5000/api/v1/queue/items?status=pending&page=1&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4. 手动处理队列

```bash
curl -X POST http://localhost:5000/api/v1/queue/process \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"count": 10}'
```

### 5. 查看定时任务状态

```bash
curl http://localhost:5000/api/v1/scheduler/jobs \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**响应：**
```json
{
  "jobs": [
    {
      "id": "daily_article_fetch",
      "name": "每日文章抓取",
      "next_run": "2026-05-14T02:00:00Z",
      "enabled": true
    },
    {
      "id": "ai_queue_processor",
      "name": "AI 队列处理",
      "next_run": "2026-05-14T02:30:00Z",
      "enabled": true
    }
  ]
}
```

---

## API 接口完整列表

### 抓取管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/crawler/fetch` | POST | 手动触发抓取 |
| `/api/v1/crawler/history` | GET | 查看抓取历史 |
| `/api/v1/crawler/stats` | GET | 查看抓取统计 |

### 队列管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/queue/status` | GET | 查看队列状态 |
| `/api/v1/queue/items` | GET | 查看队列列表 |
| `/api/v1/queue/process` | POST | 手动处理队列 |
| `/api/v1/queue/retry/{id}` | POST | 重试失败任务 |
| `/api/v1/queue/{id}` | GET | 查看队列项详情 |

### 定时任务管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/scheduler/jobs` | GET | 获取任务列表 |
| `/api/v1/scheduler/jobs/{id}` | GET | 获取任务详情 |
| `/api/v1/scheduler/jobs/{id}/trigger` | POST | 手动触发任务 |
| `/api/v1/scheduler/jobs/{id}/enable` | POST | 启用任务 |
| `/api/v1/scheduler/jobs/{id}/disable` | POST | 禁用任务 |
| `/api/v1/scheduler/logs` | GET | 查看执行历史 |

---

## 定时任务说明

### 每日文章抓取
- **时间**: 每天凌晨 2:00
- **内容**: 从所有启用的 RSS 源抓取最新文章
- **执行**: 并发抓取，串行入队

### AI 队列处理
- **时间**: 每天凌晨 2:30（抓取完成后）
- **内容**: 处理 AI 改写队列中的所有任务
- **执行**: 串行处理，每篇间隔 5 秒

### 清理历史数据
- **时间**: 每周日凌晨 3:00
- **内容**: 清理 30 天前的历史记录
- **执行**: 释放数据库空间

---

## 配置说明

### RSS 源配置

在 `app/config.py` 中配置：

```python
RSS_SOURCES = [
    {
        'name': 'juejin',
        'url': 'https://juejin.cn/tag/6824710202281967624/feed',
        'enabled': True,
        'fetch_limit': 20,
    },
    {
        'name': 'cnblogs',
        'url': 'https://www.cnblogs.com/cmt/rss',
        'enabled': True,
        'fetch_limit': 20,
    },
]
```

### AI 队列配置

```python
AI_QUEUE_CONFIG = {
    'batch_size': 1,          # 每次处理 1 个 (串行)
    'delay_between_tasks': 5, # 任务间隔 (秒)
    'max_retries': 2,         # 最大重试次数
    'timeout': 60,            # 单个任务超时时间 (秒)
}
```

---

## 测试脚本

### 测试 RSS 抓取

```bash
cd backend
python scripts/test_rss_crawler.py
```

---

## 故障排查

### 问题 1: 抓取失败

**症状**: API 返回错误或日志显示连接超时

**解决**:
1. 检查网络连接
2. 验证 RSS URL 是否可访问
3. 增加超时时间：`CRAWLER_CONFIG['timeout'] = 60`

### 问题 2: AI 改写失败

**症状**: 队列任务状态为 failed

**解决**:
1. 检查 `MINIMAX_API_KEY` 是否配置
2. 查看错误信息：`GET /api/v1/queue/{queue_id}`
3. 重试失败任务：`POST /api/v1/queue/retry/{queue_id}`

### 问题 3: 定时任务未执行

**症状**: 到时间没有自动抓取

**解决**:
1. 检查应用是否运行（定时任务在应用进程中）
2. 查看日志确认调度器已启动
3. 检查任务是否被禁用：`GET /api/v1/scheduler/jobs`

---

## 监控指标

### 关键指标

- **队列长度**: 待处理任务数
- **处理速度**: 每分钟处理任务数
- **成功率**: 成功/失败比例
- **平均处理时间**: 单个任务耗时

### 查看方式

```bash
# 队列状态
curl http://localhost:5000/api/v1/queue/status

# 抓取统计
curl http://localhost:5000/api/v1/crawler/stats

# 执行历史
curl http://localhost:5000/api/v1/scheduler/logs
```

---

## 最佳实践

1. **定期监控**: 每天检查队列状态和任务执行情况
2. **限流保护**: AI 改写间隔设置为 5 秒，避免触发 API 限流
3. **错误处理**: 失败任务自动重试 2 次，仍失败则人工介入
4. **数据清理**: 每周自动清理 30 天前的历史记录
5. **备份策略**: 定期备份数据库，防止数据丢失

---

## 下一步

- [ ] 添加更多 RSS 源（知乎、Medium 等）
- [ ] 实现监控告警（钉钉、企业微信）
- [ ] 优化 AI 改写质量
- [ ] 添加文章质量评分
- [ ] 支持自定义改写策略

---

## 技术支持

如有问题，请查看应用日志或联系开发团队。
