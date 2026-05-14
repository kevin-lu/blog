# 自动文章抓取系统 - 快速启动指南

## 🚀 5 分钟快速启动

### 1. 配置环境变量

```bash
cd backend
cp .env.example .env
vim .env
```

**必须配置**:
```bash
# Minimax AI 配置
MINIMAX_API_KEY=your_api_key_here
MINIMAX_API_HOST=https://api.minimaxi.com
MINIMAX_MODEL=abab6.5s

# 数据库配置
DATABASE_URL=mysql://user:password@localhost:3306/blog_db
# 或继续使用 SQLite
DATABASE_URL=sqlite:///blog.db
```

**可选配置**:
```bash
# 告警通知（可选）
DINGTALK_WEBHOOK=https://oapi.dingtalk.com/robot/send?access_token=xxx
WECHAT_WORK_WEBHOOK=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
ALERT_QUEUE_THRESHOLD=10
ENABLE_DAILY_REPORT=false
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库迁移

```bash
# 执行数据库迁移
python scripts/migrate_crawler_tables.py
```

### 4. 创建数据库索引（可选，性能优化）

```bash
python -c "
from app import create_app
from app.utils.db_optimization import IndexManager

app = create_app()
with app.app_context():
    IndexManager.create_recommend_indexes()
    print('✓ 索引创建完成')
"
```

### 5. 启动应用

```bash
# 方式 1: 直接启动
python run.py

# 方式 2: 使用 Flask 命令
export FLASK_APP=run.py
flask run --host=0.0.0.0 --port=5000
```

### 6. 验证系统

```bash
# 检查应用是否启动
curl http://localhost:5000/api/v1/settings

# 查看定时任务状态
curl http://localhost:5000/api/v1/scheduler/jobs \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 查看队列状态
curl http://localhost:5000/api/v1/queue/status \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## 📋 使用方式

### 方式 1: 等待定时任务自动执行

系统已配置每天凌晨 2:00 自动抓取：
- 2:00 - RSS 抓取任务
- 2:30 - AI 队列处理任务
- 周日 3:00 - 历史数据清理

### 方式 2: 手动触发抓取

```bash
# 抓取所有启用的 RSS 源
curl -X POST http://localhost:5000/api/v1/crawler/fetch \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sources": ["cnblogs", "v2ex", "solidot"], "limit": 20}'

# 查看抓取历史
curl http://localhost:5000/api/v1/crawler/history \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 方式 3: 手动处理 AI 队列

```bash
# 查看队列状态
curl http://localhost:5000/api/v1/queue/status \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 手动处理队列（处理 50 篇）
curl -X POST http://localhost:5000/api/v1/queue/process \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"count": 50}'

# 查看队列项列表
curl http://localhost:5000/api/v1/queue/items?status=pending \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 重试失败任务
curl -X POST http://localhost:5000/api/v1/queue/retry/QUEUE_ID \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 方式 4: 管理定时任务

```bash
# 获取定时任务列表
curl http://localhost:5000/api/v1/scheduler/jobs \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 手动触发抓取任务
curl -X POST http://localhost:5000/api/v1/scheduler/trigger/daily_article_fetch \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 手动触发 AI 队列处理
curl -X POST http://localhost:5000/api/v1/scheduler/trigger/ai_queue_processor \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# 禁用/启用定时任务
curl -X POST http://localhost:5000/api/v1/scheduler/toggle/daily_article_fetch \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

---

## 🔍 监控与告警

### 查看系统状态

```bash
# 队列统计
curl http://localhost:5000/api/v1/queue/status

# 定时任务执行日志
curl http://localhost:5000/api/v1/scheduler/logs?job_id=daily_article_fetch \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 告警配置

**钉钉机器人配置**:
1. 钉钉群 → 群设置 → 智能群助手 → 添加机器人
2. 选择"自定义"机器人
3. 复制 Webhook 地址
4. 添加到 `.env` 文件：`DINGTALK_WEBHOOK=xxx`

**企业微信机器人配置**:
1. 企业微信群 → 群设置 → 添加群机器人
2. 新建机器人
3. 复制 Webhook 地址
4. 添加到 `.env` 文件：`WECHAT_WORK_WEBHOOK=xxx`

### 告警类型

系统会在以下情况发送告警：
- RSS 抓取失败
- AI 改写失败（达到最大重试次数）
- 队列积压超过阈值（默认 10 篇）
- 每日执行报告（如启用）

---

## 🛠️ 故障排查

### 问题 1: 应用启动失败

```bash
# 检查依赖
pip install -r requirements.txt

# 检查数据库连接
python -c "from app import create_app; app = create_app(); print('OK')"

# 查看详细错误日志
tail -f logs/app.log
```

### 问题 2: RSS 抓取失败

```bash
# 测试 RSS 源连接
curl -I https://www.cnblogs.com/cmt/rss

# 手动测试抓取
python scripts/test_rss_crawler.py

# 查看抓取日志
grep "rss_crawler" logs/app.log | tail -50
```

### 问题 3: AI 改写失败

```bash
# 检查 Minimax API 配置
echo $MINIMAX_API_KEY

# 测试 API 连接
python -c "
from app.services.ai_rewrite import MiniMaxClient
from app.config import Config

client = MiniMaxClient(
    api_key=Config.MINIMAX_API_KEY,
    model=Config.MINIMAX_MODEL,
    base_url=Config.MINIMAX_API_HOST,
)

result = client.rewrite_article(
    title='测试文章',
    content='这是一篇测试文章的内容...',
    strategy='standard'
)
print(result)
"

# 查看失败队列
curl http://localhost:5000/api/v1/queue/items?status=failed
```

### 问题 4: 定时任务未执行

```bash
# 检查调度器状态
curl http://localhost:5000/api/v1/scheduler/jobs

# 查看调度器日志
grep "scheduler" logs/app.log | tail -50

# 手动触发任务
curl -X POST http://localhost:5000/api/v1/scheduler/trigger/daily_article_fetch
```

### 问题 5: 数据库性能问题

```bash
# 分析表大小
python -c "
from app import create_app
from app.utils.db_optimization import IndexManager

app = create_app()
with app.app_context():
    IndexManager.analyze_table_sizes()
"

# 检查索引
python -c "
from app import create_app
from app.utils.db_optimization import IndexManager

app = create_app()
with app.app_context():
    IndexManager.check_missing_indexes()
"

# 创建索引
python -c "
from app import create_app
from app.utils.db_optimization import IndexManager

app = create_app()
with app.app_context():
    IndexManager.create_recommend_indexes()
"

# 清理旧数据
python -c "
from app import create_app
from app.utils.db_optimization import CleanupManager

app = create_app()
with app.app_context():
    CleanupManager.cleanup_old_records(days=30)
    CleanupManager.vacuum_database()
"
```

---

## 📊 API 接口文档

### 抓取管理

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/api/v1/crawler/fetch` | POST | 手动触发抓取 | Admin |
| `/api/v1/crawler/history` | GET | 查看抓取历史 | Admin |
| `/api/v1/crawler/tasks` | GET | 查看抓取任务列表 | Admin |

### 队列管理

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/api/v1/queue/status` | GET | 查看队列状态 | Admin |
| `/api/v1/queue/items` | GET | 查看队列项列表 | Admin |
| `/api/v1/queue/process` | POST | 手动处理队列 | Admin |
| `/api/v1/queue/retry/{id}` | POST | 重试失败任务 | Admin |

### 定时任务

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/api/v1/scheduler/jobs` | GET | 查看定时任务列表 | Admin |
| `/api/v1/scheduler/trigger/{job_id}` | POST | 手动触发任务 | Admin |
| `/api/v1/scheduler/toggle/{job_id}` | POST | 启用/禁用任务 | Admin |
| `/api/v1/scheduler/logs` | GET | 查看任务执行日志 | Admin |

---

## 📝 配置说明

### RSS 源配置

编辑 `app/config.py`:

```python
RSS_SOURCES = [
    {
        'name': 'cnblogs',
        'url': 'https://www.cnblogs.com/cmt/rss',
        'enabled': True,  # 是否启用
        'fetch_limit': 20,  # 每次抓取数量
        'category': '技术社区',  # 分类
    },
    # ... 更多源
]
```

### AI 队列配置

```python
AI_QUEUE_CONFIG = {
    'batch_size': 1,  # 批次大小（串行处理）
    'delay_between_tasks': 5,  # 任务间隔（秒）
    'max_retries': 2,  # 最大重试次数
    'timeout': 60,  # 超时时间（分钟）
}
```

### 告警配置

```python
ALERT_QUEUE_THRESHOLD = 10  # 队列积压告警阈值
ENABLE_DAILY_REPORT = False  # 是否启用每日报告
```

---

## 🎯 最佳实践

### 1. 性能优化

- ✅ 使用批量操作（已实现）
- ✅ 创建数据库索引（已实现）
- ✅ 定期清理旧数据（自动执行）
- ✅ 监控队列长度

### 2. 稳定性保障

- ✅ 配置告警通知
- ✅ 定期检查日志
- ✅ 监控 API 调用成功率
- ✅ 合理设置重试次数

### 3. 资源管理

- ✅ 串行调用 AI（避免并发限制）
- ✅ 设置合理的抓取数量
- ✅ 定期清理数据库
- ✅ 监控资源使用

### 4. 安全建议

- ✅ 保护 API Token
- ✅ 限制 API 访问频率
- ✅ 使用 HTTPS
- ✅ 定期备份数据库

---

## 📞 获取帮助

### 查看日志

```bash
# 实时查看应用日志
tail -f logs/app.log

# 查看错误日志
grep "ERROR" logs/app.log | tail -50

# 查看特定模块日志
grep "rss_crawler" logs/app.log | tail -50
```

### 查看文档

- [CRAWLER_GUIDE.md](CRAWLER_GUIDE.md) - 完整使用指南
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - 实现总结
- [TEST_REPORT.md](TEST_REPORT.md) - 测试报告
- [FINAL_REPORT.md](FINAL_REPORT.md) - 最终报告

---

**🎊 系统已就绪，祝您使用愉快！**
