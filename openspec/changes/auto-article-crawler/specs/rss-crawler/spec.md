# RSS Crawler 规格

## 能力描述

系统应支持从配置的 RSS 源自动抓取技术文章，解析文章内容并转换为系统标准格式。

## 数据源配置

### 掘金 RSS
- **名称**: 掘金 - 推荐
- **URL**: `https://juejin.cn/tag/6824710202281967624/feed`
- **频率**: 每天 1 次
- **每次抓取**: 最新 20 篇

### 博客园 RSS
- **名称**: 博客园 - 首页新闻
- **URL**: `https://www.cnblogs.com/cmt/rss`
- **频率**: 每天 1 次
- **每次抓取**: 最新 20 篇

## 功能需求

### 1. RSS Feed 解析

系统应能解析标准 RSS 2.0 和 Atom 格式：

```python
class RSSFeed:
    title: str          # Feed 标题
    link: str           # Feed 链接
    description: str    # Feed 描述
    entries: List[RSSEntry]
```

### 2. 文章条目提取

每个 RSS Entry 应提取以下字段：

```python
class RSSEntry:
    title: str          # 文章标题
    link: str           # 原文链接 (用于去重)
    summary: str        # 摘要
    content: str        # 正文内容 (可能为 HTML)
    author: str         # 作者
    published: datetime # 发布时间
    tags: List[str]     # 标签
```

### 3. 内容清洗

系统应对抓取的 HTML 内容进行清洗：

- 移除脚本标签 (`<script>`, `<style>`)
- 转换相对路径为绝对路径
- 提取纯文本用于 AI 改写
- 保留基本格式标签 (`<p>`, `<code>`, `<pre>`)

### 4. 去重检测

系统应在抓取前检测文章是否已存在：

**检测维度：**
1. **URL 去重**: 检查 `link` 是否已存在于 `crawled_urls` 表
2. **标题去重**: 计算标题 MD5，检查是否已存在于 `crawled_titles` 表
3. **文章去重**: 检查 `article_meta` 表中是否已有相同 `source_url`

**去重优先级：**
- URL 重复 → 直接跳过
- 标题重复 → 跳过（避免不同源抓取相同文章）
- 已存在文章 → 跳过

### 5. 错误处理

**网络错误：**
- 连接超时：重试 3 次，每次间隔 5 秒
- HTTP 错误：记录日志，跳过该源
- RSS 解析失败：记录日志，跳过该源

**数据错误：**
- 缺少必要字段（标题/链接）：跳过该条目
- 内容为空：跳过该条目

## 数据模型

### CrawledURL 表

记录已抓取的 URL，防止重复：

```python
class CrawledURL(db.Model):
    __tablename__ = 'crawled_urls'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200))
    source = db.Column(db.String(50))  # 来源：juejin, cnblogs
    crawled_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### CrawledTitle 表

记录已抓取文章的标题 MD5：

```python
class CrawledTitle(db.Model):
    __tablename__ = 'crawled_titles'
    
    id = db.Column(db.Integer, primary_key=True)
    title_md5 = db.Column(db.String(32), unique=True, nullable=False, index=True)
    original_title = db.Column(db.String(200))
    crawled_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## API 接口

### 手动触发抓取

```
POST /api/v1/crawler/fetch
```

**请求体：**
```json
{
  "source": "juejin",  // 可选，不传则抓取所有配置源
  "limit": 20          // 可选，默认 20
}
```

**响应：**
```json
{
  "task_id": "fetch_20260513_020000",
  "status": "pending",
  "message": "抓取任务已创建"
}
```

### 获取抓取历史

```
GET /api/v1/crawler/history?page=1&limit=20
```

**响应：**
```json
{
  "total": 100,
  "items": [
    {
      "id": 1,
      "source": "juejin",
      "fetched_at": "2026-05-13T02:00:00Z",
      "articles_found": 20,
      "articles_new": 15,
      "status": "completed"
    }
  ]
}
```

## 配置项

```python
# app/config.py

# RSS 数据源配置
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
    }
]

# 爬虫配置
CRAWLER_CONFIG = {
    'timeout': 30,           # 请求超时 (秒)
    'retry_times': 3,        # 重试次数
    'retry_delay': 5,        # 重试间隔 (秒)
    'user_agent': 'BlogCrawler/1.0',
}
```
