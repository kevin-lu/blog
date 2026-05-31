## Context

当前博客系统文章数量有限，需要自动化从外部技术社区获取优质内容。已有 MiniMax AI 改写服务，但并发能力有限。系统采用 Flask + SQLAlchemy 架构，数据库使用 MySQL。

**约束条件：**
- MiniMax AI 并发调用能力低，需要串行处理
- 需要避免重复抓取相同文章
- 抓取后直接发布，不需要人工审核环节
- 定时任务需要在应用进程内运行（不引入 Celery 等复杂架构）

## Goals / Non-Goals

**Goals:**
- 实现 RSS 方式从掘金、博客园抓取技术文章
- 每天凌晨 2 点自动执行抓取任务
- AI 改写任务队列化，串行处理避免并发限制
- 抓取后自动发布，无需人工干预
- 完善的去重机制和错误处理

**Non-Goals:**
- 不支持微信公众号抓取（需要特殊授权）
- 不提供人工审核流程
- 不支持实时抓取（仅定时任务）
- 不实现复杂的分布式任务调度

## Decisions

### 1. 定时任务方案：APScheduler 内置调度

**选择：** 使用 APScheduler 作为 Flask 应用内定时任务调度器

**替代方案：**
- ❌ Celery 分布式任务：架构复杂，需要 Redis broker，过度设计
- ❌ 系统 Cron + 独立脚本：无法利用 Flask 应用上下文，数据库连接管理复杂
- ✅ APScheduler：轻量级，与 Flask 集成好，支持 cron 表达式

**理由：**
- 项目本身不复杂，不需要分布式任务队列
- Flask 应用已有数据库连接池，APScheduler 可直接复用
- 部署简单，不需要额外服务

### 2. 任务队列实现：数据库持久化队列

**选择：** 使用数据库表实现任务队列，通过状态字段控制处理顺序

**替代方案：**
- ❌ Redis List：需要额外 Redis 服务，增加依赖
- ❌ 内存队列：应用重启丢失任务，不可靠
- ✅ 数据库队列：持久化，与现有架构一致，可追踪状态

**实现：**
```python
class CrawlerTask(Base):
    status = Column(String)  # pending, processing, completed, failed
    priority = Column(Integer, default=0)
    created_at = Column(DateTime)
    processed_at = Column(DateTime)
```

### 3. AI 改写串行处理：队列轮询模式

**选择：** 使用后台线程轮询队列，串行调用 MiniMax API

**实现：**
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  抓取任务    │───▶│  队列管理    │───▶│ MiniMax AI   │
│  (并发)      │    │  (串行)      │    │  (串行)      │
└──────────────┘    └──────────────┘    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  文章发布    │
                    └──────────────┘
```

**理由：**
- 避免 MiniMax API 并发限制导致的失败
- 队列持久化，应用重启后可继续处理
- 可追踪每个任务的进度和状态

### 4. 去重策略：URL + 标题 MD5 双重检测

**选择：** 同时使用 URL 和标题 MD5 进行去重判断

**实现：**
```python
# URL 去重
if url in crawled_urls:
    return True

# 标题去重
title_md5 = md5(title)
if title_md5 in crawled_titles:
    return True
```

**理由：**
- URL 去重：防止重复抓取同一篇文章
- 标题去重：防止不同源抓取相同文章
- 简单高效，不需要复杂的内容指纹算法

### 5. RSS 解析：feedparser 库

**选择：** 使用 feedparser 解析 RSS/Atom feed

**理由：**
- Python 标准 RSS 解析库，成熟稳定
- 支持 RSS 1.0/2.0 和 Atom 格式
- 自动处理编码和字符集问题

### 6. 错误处理：重试 + 降级策略

**选择：** 网络请求失败自动重试 3 次，AI 服务失败标记任务失败

**策略：**
- RSS 抓取失败：重试 3 次，记录日志，跳过该源
- AI 改写失败：重试 2 次，仍失败则标记任务失败，人工介入
- 数据库写入失败：立即回滚，告警通知

## Risks / Trade-offs

### 风险 1: MiniMax API 限流
**风险：** 即使串行调用，也可能触发 API 限流

**缓解：**
- 在队列处理中加入延迟（每篇文章间隔 5 秒）
- 监控 API 响应，检测到限流时暂停队列
- 配置告警，通知人工介入

### 风险 2: 内容版权问题
**风险：** 抓取他人文章可能涉及版权风险

**缓解：**
- 仅抓取允许转载的内容（查看 RSS 许可）
- 在文章中注明原文出处和作者
- 提供侵权删除通道

### 风险 3: 定时任务阻塞
**风险：** APScheduler 在 Flask 主线程运行，长任务可能阻塞 Web 请求

**缓解：**
- 使用 BackgroundScheduler 在后台线程运行
- 抓取和 AI 改写任务异步执行，不阻塞调度器
- 监控任务执行时间，超时自动终止

### 风险 4: 数据库连接竞争
**风险：** 定时任务和 Web 请求竞争数据库连接

**缓解：**
- 使用 SQLAlchemy 连接池管理
- 配置合理的连接池大小（max_overflow=20）
- 任务中使用独立会话，避免长事务

### 风险 5: 文章内容质量
**风险：** AI 改写后文章质量不稳定

**缓解：**
- 优化 AI 改写 prompt，确保改写质量
- 记录每次改写效果，持续优化
- 提供人工审核开关，可随时切换为草稿模式

## Migration Plan

### 部署步骤

1. **安装依赖**
   ```bash
   pip install feedparser APScheduler
   ```

2. **数据库迁移**
   ```bash
   python scripts/migrate_crawler_tables.py
   ```

3. **配置数据源**
   ```python
   # app/config.py
   RSS_SOURCES = [
       {'name': '掘金', 'url': '...'},
       {'name': '博客园', 'url': '...'}
   ]
   ```

4. **启动定时任务**
   ```python
   # app/__init__.py
   from app.services.crawler_scheduler import init_scheduler
   init_scheduler(app)
   ```

### 回滚策略

1. 停止定时任务：`scheduler.shutdown()`
2. 删除新增的数据库表
3. 回滚代码到上一版本

## Open Questions

1. **掘金和博客园的具体 RSS 地址？**
   - 需要用户提供或调研获取
   
2. **每次抓取多少篇文章？**
   - 建议：每个源 10-20 篇，避免单次任务过重

3. **AI 改写延迟设置？**
   - 建议：5 秒/篇，平衡速度和 API 限流

4. **是否需要监控告警集成？**
   - 第一阶段：仅日志记录
   - 第二阶段：集成钉钉/企业微信通知
