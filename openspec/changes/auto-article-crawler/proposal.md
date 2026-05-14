## Why

当前博客系统文章数量较少，需要自动化从外部优质技术源（掘金、博客园）获取文章并进行 AI 改写，以丰富内容库。通过 RSS 方式定时抓取，结合 MiniMax AI 进行内容改写，实现文章生产的自动化流程。

## What Changes

- 新增 RSS 抓取模块，支持掘金和博客园两个数据源
- 新增定时任务调度系统，每天凌晨 2 点自动执行
- 新增 AI 改写任务队列，串行处理改写请求（避免 MiniMax 并发限制）
- 新增文章去重机制，基于 URL 和标题 MD5 判断
- 文章抓取后自动进入 AI 改写队列，改写完成后直接发布
- 新增抓取任务管理 API，支持查看任务状态和历史记录

## Capabilities

### New Capabilities

- `rss-crawler`: RSS 文章抓取能力，支持配置数据源、解析 RSS  feed、提取文章内容
- `article-queue`: AI 改写任务队列管理，支持任务创建、排队、状态跟踪、串行处理
- `scheduled-jobs`: 定时任务调度能力，支持 cron 表达式配置、任务触发、错误重试
- `duplicate-detection`: 文章去重检测能力，基于 URL 和标题指纹判断重复

### Modified Capabilities

- `article-management`: 文章管理流程变更，增加 AI 改写后自动发布的流程

## Impact

- **后端**: 新增 RSS 抓取服务、任务队列服务、定时任务调度器
- **数据库**: 新增抓取任务表、队列任务表、已抓取 URL 记录表
- **依赖**: 需要添加 feedparser (RSS 解析)、APScheduler (定时任务)
- **AI 服务**: MiniMax AI 调用改为串行队列模式，避免并发限制
- **配置**: 需要配置 RSS 数据源、抓取频率、AI 改写参数
