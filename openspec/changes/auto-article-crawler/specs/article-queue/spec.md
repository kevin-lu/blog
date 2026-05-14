# Article Queue 规格

## 能力描述

系统应支持 AI 改写任务队列，将抓取的文章加入队列，串行调用 MiniMax AI 进行改写，改写完成后自动发布。

## 队列设计

### 队列特性

1. **持久化**: 任务存储在数据库中，应用重启后不丢失
2. **串行处理**: 每次只处理一个任务，避免 MiniMax API 并发限制
3. **状态追踪**: 每个任务都有明确的状态和进度
4. **失败重试**: 失败任务可自动重试
5. **优先级**: 支持任务优先级排序

### 任务状态机

```
┌─────────────┐
│  pending    │ 等待处理
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ processing  │ 正在处理
└──────┬──────┘
       │
       ├─────────────┬─────────────┐
       ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ completed   │ │   failed    │ │  cancelled  │
└─────────────┘ └─────────────┘ └─────────────┘
```

## 数据模型

### CrawlerTask 表

抓取任务主表：

```python
class CrawlerTask(db.Model):
    __tablename__ = 'crawler_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    source = db.Column(db.String(50))  # 来源：juejin, cnblogs
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    articles_found = db.Column(db.Integer, default=0)
    articles_new = db.Column(db.Integer, default=0)
    articles_queued = db.Column(db.Integer, default=0)  # 加入 AI 队列的数量
    articles_processed = db.Column(db.Integer, default=0)  # AI 处理完成的数量
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### AIQueue 表

AI 改写队列：

```python
class AIQueue(db.Model):
    __tablename__ = 'ai_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    queue_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article_meta.id'))
    
    # 文章原始数据
    title = db.Column(db.String(200), nullable=False)
    original_content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.Text)
    author = db.Column(db.String(100))
    published_at = db.Column(db.DateTime)
    
    # 队列状态
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    priority = db.Column(db.Integer, default=0)  # 优先级，数字越大优先级越高
    retry_count = db.Column(db.Integer, default=0)  # 重试次数
    max_retries = db.Column(db.Integer, default=2)  # 最大重试次数
    
    # AI 改写结果
    rewritten_content = db.Column(db.Text)
    ai_model = db.Column(db.String(100))
    rewrite_strategy = db.Column(db.String(20))
    
    # 时间戳
    queued_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
```

## 队列处理流程

### 1. 任务入队

```python
def enqueue_article(article_data: dict) -> AIQueue:
    """将文章加入 AI 改写队列"""
    queue_item = AIQueue(
        queue_id=f"ai_{uuid4().hex[:12]}",
        title=article_data['title'],
        original_content=article_data['content'],
        source_url=article_data['link'],
        author=article_data.get('author'),
        published_at=article_data.get('published'),
        status='pending',
        priority=0,
    )
    db.session.add(queue_item)
    db.session.commit()
    return queue_item
```

### 2. 串行处理

```python
def process_queue():
    """串行处理 AI 改写队列"""
    while True:
        # 获取优先级最高的待处理任务
        task = AIQueue.query.filter_by(status='pending')\
            .order_by(AIQueue.priority.desc(), AIQueue.queued_at.asc())\
            .first()
        
        if not task:
            break  # 队列为空
        
        try:
            # 更新状态
            task.status = 'processing'
            task.started_at = datetime.utcnow()
            db.session.commit()
            
            # 调用 MiniMax AI 改写
            rewritten = call_minimax_ai(
                title=task.title,
                content=task.original_content,
                strategy='standard'
            )
            
            # 创建文章并发布
            article = create_and_publish_article(
                title=task.title,
                content=rewritten,
                source_url=task.source_url,
                author=task.author,
            )
            
            # 更新队列状态
            task.status = 'completed'
            task.article_id = article.id
            task.rewritten_content = rewritten
            task.completed_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            # 失败重试逻辑
            task.retry_count += 1
            if task.retry_count >= task.max_retries:
                task.status = 'failed'
                task.error_message = str(e)
            else:
                task.status = 'pending'  # 重新加入队列
            
            db.session.commit()
```

### 3. MiniMax AI 调用

```python
def call_minimax_ai(title: str, content: str, strategy: str = 'standard') -> str:
    """串行调用 MiniMax AI 进行文章改写"""
    
    # 添加延迟，避免触发限流
    time.sleep(5)
    
    prompt = f"""
请将以下技术文章进行改写，保持原意但改变表达方式：

原文标题：{title}

原文内容：
{content}

改写要求：
1. 保持技术准确性
2. 改变句式和段落结构
3. 使用更通俗易懂的表达
4. 保留代码示例
5. 字数控制在原文的 80%-120%
"""
    
    response = minimax_client.generate(
        model='abab6.5',
        prompt=prompt,
        max_tokens=4000,
    )
    
    return response.content
```

### 4. 文章创建与发布

```python
def create_and_publish_article(title: str, content: str, source_url: str, author: str) -> Article:
    """创建文章并直接发布"""
    
    # 生成 slug
    slug = generate_slug(title)
    
    # 创建文章
    article = Article(
        slug=slug,
        title=title,
        content=content,
        source_url=source_url,
        ai_generated=1,
        ai_model='minimax-abab6.5',
        rewrite_strategy='standard',
        template_type='tutorial',
        word_count=len(content),
        status='published',  # 直接发布
        published_at=datetime.utcnow(),
    )
    
    db.session.add(article)
    db.session.commit()
    
    return article
```

## API 接口

### 获取队列状态

```
GET /api/v1/queue/status
```

**响应：**
```json
{
  "pending": 15,
  "processing": 1,
  "completed": 120,
  "failed": 3,
  "estimated_time_minutes": 75
}
```

### 获取队列列表

```
GET /api/v1/queue/items?page=1&limit=20&status=pending
```

**响应：**
```json
{
  "total": 15,
  "items": [
    {
      "queue_id": "ai_abc123",
      "title": "文章标题",
      "source_url": "https://...",
      "status": "pending",
      "priority": 0,
      "retry_count": 0,
      "queued_at": "2026-05-13T02:00:00Z"
    }
  ]
}
```

### 手动处理队列

```
POST /api/v1/queue/process
```

**请求体：**
```json
{
  "count": 10  // 处理多少个任务，不传则处理完所有
}
```

**响应：**
```json
{
  "processed": 10,
  "success": 9,
  "failed": 1
}
```

### 重试失败任务

```
POST /api/v1/queue/retry/{queue_id}
```

**响应：**
```json
{
  "queue_id": "ai_abc123",
  "status": "pending",
  "message": "任务已重新加入队列"
}
```

## 配置项

```python
# app/config.py

# AI 队列配置
AI_QUEUE_CONFIG = {
    'batch_size': 1,          # 每次处理 1 个 (串行)
    'delay_between_tasks': 5, # 任务间隔 (秒)，避免 API 限流
    'max_retries': 2,         # 最大重试次数
    'timeout': 60,            # 单个任务超时时间 (秒)
}

# MiniMax AI 配置
MINIMAX_CONFIG = {
    'api_key': '...',
    'model': 'abab6.5',
    'max_tokens': 4000,
    'temperature': 0.7,
}
```

## 监控指标

系统应记录以下指标：

1. **队列长度**: 待处理任务数量
2. **处理速度**: 每分钟处理任务数
3. **成功率**: 成功/失败任务比例
4. **平均处理时间**: 单个任务平均耗时
5. **API 调用次数**: MiniMax API 调用次数统计
