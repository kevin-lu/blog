## 1. 数据库模型与迁移

- [x] 1.1 创建 CrawledURL 模型（记录已抓取的 URL）
- [x] 1.2 创建 CrawledTitle 模型（记录已抓取的文章标题 MD5）
- [x] 1.3 创建 CrawlerTask 模型（抓取任务记录）
- [x] 1.4 创建 AIQueue 模型（AI 改写队列）
- [x] 1.5 创建 ScheduledJobLog 模型（定时任务执行日志）
- [x] 1.6 创建数据库迁移脚本并执行迁移

## 2. RSS 抓取模块实现

- [x] 2.1 安装 feedparser 依赖
- [x] 2.2 创建 `app/services/rss_crawler.py` 模块
- [x] 2.3 实现 RSS Feed 解析功能（支持 RSS 2.0 和 Atom）
- [x] 2.4 实现内容清洗功能（移除脚本标签、转换路径等）
- [x] 2.5 实现去重检测逻辑（URL + 标题 MD5 双重检测）
- [x] 2.6 实现文章数据转换（转换为标准格式）
- [x] 2.7 配置优化的 RSS 源（添加更多稳定源）

## 3. AI 改写队列实现

- [x] 3.1 创建 `app/services/ai_queue.py` 模块
- [x] 3.2 实现队列入队功能（enqueue_article）
- [x] 3.3 实现队列出队功能（获取待处理任务）
- [x] 3.4 实现串行队列处理器（process_queue）
- [x] 3.5 集成 MiniMax AI 调用（添加延迟和重试机制）
- [x] 3.6 实现文章创建与发布功能
- [x] 3.7 实现失败任务重试逻辑

## 4. 定时任务调度实现

- [x] 4.1 安装 APScheduler 依赖
- [x] 4.2 创建 `app/services/scheduler.py` 模块
- [x] 4.3 初始化 BackgroundScheduler
- [x] 4.4 实现每日文章抓取任务（每天 2:00 执行）
- [x] 4.5 实现 AI 队列处理任务（每天 2:30 执行）
- [x] 4.6 实现历史数据清理任务（每周日 3:00 执行）
- [x] 4.7 在 `app/__init__.py` 中集成调度器启动
- [x] 4.8 实现任务错误处理和日志记录

## 5. API 接口实现

- [x] 5.1 创建 `app/api/v1/crawler.py` 路由模块
- [x] 5.2 实现手动触发抓取接口 `POST /api/v1/crawler/fetch`
- [x] 5.3 实现抓取历史查询接口 `GET /api/v1/crawler/history`
- [x] 5.4 实现队列状态查询接口 `GET /api/v1/queue/status`
- [x] 5.5 实现队列列表接口 `GET /api/v1/queue/items`
- [x] 5.6 实现手动处理队列接口 `POST /api/v1/queue/process`
- [x] 5.7 实现失败任务重试接口 `POST /api/v1/queue/retry/{queue_id}`
- [x] 5.8 实现定时任务管理接口（获取列表、手动触发、启用/禁用）

## 6. 配置与依赖

- [x] 6.1 在 `requirements.txt` 中添加新依赖
- [x] 6.2 在 `app/config.py` 中添加 RSS 源配置
- [x] 6.3 在 `app/config.py` 中添加 AI 队列配置
- [x] 6.4 在 `app/config.py` 中添加调度器配置
- [x] 6.5 更新 `.env.example` 添加相关配置项

## 7. 测试与验证

- [x] 7.1 测试 RSS 抓取功能（手动触发）
- [x] 7.2 测试去重检测逻辑
- [x] 7.3 测试 AI 队列入队和出队
- [x] 7.4 测试 MiniMax AI 串行调用
- [x] 7.5 测试定时任务调度（可临时修改时间测试）
- [x] 7.6 测试 API 接口功能
- [x] 7.7 验证完整流程：抓取 → 入队 → AI 改写 → 发布

## 8. 监控与优化

- [x] 8.1 添加关键日志记录（抓取、队列、AI 调用）
- [x] 8.2 实现监控指标统计（队列长度、处理速度、成功率）
- [x] 8.3 添加异常情况告警机制（钉钉/企业微信 webhook）
- [x] 8.4 性能优化（数据库查询优化、批量操作）
- [x] 8.5 编写运维文档和故障排查指南
