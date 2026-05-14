# Scheduled Jobs 规格

## 能力描述

系统应支持定时任务调度，每天凌晨 2 点自动执行文章抓取任务，并触发 AI 改写队列处理。

## 调度器设计

### 技术选型

使用 **APScheduler** (Advanced Python Scheduler) 作为定时任务调度库。

**理由：**
- 轻量级，不需要额外服务
- 支持 cron 表达式
- 与 Flask 集成良好
- 支持持久化任务存储

### 调度器类型

使用 `BackgroundScheduler`，在后台线程运行，不阻塞 Flask Web 请求。

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()
```

## 任务配置

### 任务 1: 文章抓取任务

**触发时间：** 每天凌晨 2:00

**Cron 表达式：** `0 2 * * *`

**任务内容：**
1. 遍历所有启用的 RSS 源
2. 抓取每个源的最新文章
3. 去重检测
4. 将新文章加入 AI 改写队列
5. 记录抓取结果

```python
@scheduler.scheduled_job('cron', hour=2, minute=0, id='daily_article_fetch')
def daily_article_fetch():
    """每日文章抓取任务"""
    logger.info("开始执行每日文章抓取任务")
    
    sources = get_enabled_rss_sources()
    total_found = 0
    total_new = 0
    
    for source in sources:
        try:
            result = fetch_rss_source(source)
            total_found += result['found']
            total_new += result['new']
        except Exception as e:
            logger.error(f"抓取源 {source['name']} 失败：{e}")
    
    logger.info(f"抓取完成，共发现 {total_found} 篇文章，新增 {total_new} 篇")
```

### 任务 2: AI 队列处理任务

**触发时间：** 每天凌晨 2:30（抓取完成后）

**Cron 表达式：** `30 2 * * *`

**任务内容：**
1. 检查 AI 改写队列
2. 串行处理队列中的任务
3. 调用 MiniMax AI 进行改写
4. 创建并发布文章

```python
@scheduler.scheduled_job('cron', hour=2, minute=30, id='ai_queue_processor')
def ai_queue_processor():
    """AI 队列处理任务"""
    logger.info("开始处理 AI 改写队列")
    
    processed = 0
    success = 0
    failed = 0
    
    while True:
        task = get_next_queue_task()
        if not task:
            break
        
        try:
            process_ai_task(task)
            success += 1
        except Exception as e:
            logger.error(f"处理 AI 任务 {task.queue_id} 失败：{e}")
            failed += 1
        
        processed += 1
    
    logger.info(f"队列处理完成，共处理 {processed} 个，成功 {success} 个，失败 {failed} 个")
```

### 任务 3: 清理历史数据

**触发时间：** 每周日凌晨 3:00

**Cron 表达式：** `0 3 * * 0`

**任务内容：**
1. 清理 30 天前的已抓取 URL 记录
2. 清理 30 天前的已完成 AI 队列任务
3. 释放数据库空间

```python
@scheduler.scheduled_job('cron', hour=3, minute=0, day_of_week='sun', id='cleanup_history')
def cleanup_history():
    """清理历史数据"""
    logger.info("开始清理历史数据")
    
    # 清理 30 天前的抓取记录
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    deleted = CrawledURL.query.filter(CrawledURL.crawled_at < cutoff_date).delete()
    
    logger.info(f"清理完成，删除 {deleted} 条历史记录")
```

## 数据模型

### ScheduledJobLog 表

记录定时任务执行日志：

```python
class ScheduledJobLog(db.Model):
    __tablename__ = 'scheduled_job_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(50), nullable=False, index=True)  # 任务 ID
    job_name = db.Column(db.String(100))  # 任务名称
    status = db.Column(db.String(20))  # success, failed, timeout
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)  # 执行时长
    result = db.Column(db.Text)  # 执行结果摘要
    error_message = db.Column(db.Text)  # 错误信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## 初始化与启动

### 初始化调度器

```python
def init_scheduler(app):
    """初始化定时任务调度器"""
    
    scheduler.init_app(app)
    scheduler.start()
    
    logger.info("定时任务调度器已启动")
```

### 任务注册

```python
def register_scheduled_jobs():
    """注册所有定时任务"""
    
    # 每日文章抓取
    scheduler.add_job(
        func=daily_article_fetch,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_article_fetch',
        name='每日文章抓取',
        replace_existing=True,
    )
    
    # AI 队列处理
    scheduler.add_job(
        func=ai_queue_processor,
        trigger=CronTrigger(hour=2, minute=30),
        id='ai_queue_processor',
        name='AI 队列处理',
        replace_existing=True,
    )
    
    # 清理历史数据
    scheduler.add_job(
        func=cleanup_history,
        trigger=CronTrigger(hour=3, minute=0, day_of_week='sun'),
        id='cleanup_history',
        name='清理历史数据',
        replace_existing=True,
    )
```

## API 接口

### 获取任务列表

```
GET /api/v1/scheduler/jobs
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

### 手动触发任务

```
POST /api/v1/scheduler/jobs/{job_id}/trigger
```

**响应：**
```json
{
  "job_id": "daily_article_fetch",
  "status": "started",
  "message": "任务已手动触发"
}
```

### 启用/禁用任务

```
POST /api/v1/scheduler/jobs/{job_id}/enable
POST /api/v1/scheduler/jobs/{job_id}/disable
```

**响应：**
```json
{
  "job_id": "daily_article_fetch",
  "enabled": true,
  "message": "任务已启用"
}
```

### 获取执行历史

```
GET /api/v1/scheduler/logs?job_id=daily_article_fetch&page=1&limit=20
```

**响应：**
```json
{
  "total": 50,
  "items": [
    {
      "id": 1,
      "job_id": "daily_article_fetch",
      "job_name": "每日文章抓取",
      "status": "success",
      "started_at": "2026-05-13T02:00:00Z",
      "completed_at": "2026-05-13T02:05:30Z",
      "duration_seconds": 330,
      "result": "抓取 40 篇文章，新增 35 篇"
    }
  ]
}
```

## 配置项

```python
# app/config.py

# 调度器配置
SCHEDULER_CONFIG = {
    'timezone': 'Asia/Shanghai',  # 时区
    'job_defaults': {
        'coalesce': True,  # 合并错过的执行
        'max_instances': 1,  # 每个任务最多 1 个实例
        'misfire_grace_time': 3600,  # 错过执行的容忍时间 (秒)
    },
}

# 任务开关
ENABLED_JOBS = {
    'daily_article_fetch': True,
    'ai_queue_processor': True,
    'cleanup_history': True,
}
```

## 错误处理

### 任务执行超时

```python
from apscheduler.executors.pool import ThreadPoolExecutor

# 配置执行器，设置超时
executor = ThreadPoolExecutor(max_workers=10)
scheduler.add_executor(executor)

# 任务添加超时配置
scheduler.add_job(
    func=daily_article_fetch,
    trigger='cron',
    hour=2,
    minute=0,
    max_execution_time=3600,  # 最大执行时间 1 小时
)
```

### 任务失败告警

```python
def job_error_handler(event):
    """任务错误处理"""
    if event.exception:
        logger.error(f"任务 {event.job_id} 执行失败：{event.traceback}")
        # 发送告警通知
        send_alert(f"定时任务失败：{event.job_id}")

scheduler.add_listener(job_error_handler, EVENT_JOB_ERROR)
```

## 监控指标

1. **任务执行状态**: 成功/失败/超时
2. **任务执行时长**: 每次任务的执行时间
3. **下次执行时间**: 每个任务的下次计划执行时间
4. **任务队列长度**: 待执行任务数量
5. **历史执行记录**: 保留最近 100 次执行记录
