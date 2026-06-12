# 性能测试 Agent - 自动化压测 + 瓶颈分析

基于 `perf-test-agent` 理念实现的自动化性能测试框架，为你的博客项目提供完整的性能测试解决方案。

## 🎯 核心功能

### 1. 自动压测
- ✅ 基于 Locust 的分布式压测引擎
- ✅ 阶梯式加压策略（10% → 30% → 50% → 80% → 100%）
- ✅ 模拟真实用户行为（访客、登录用户、管理员）
- ✅ 自动熔断（错误率 > 5% 或 RT > SLA 3 倍）

### 2. 监控采集
- ✅ **应用层**: TPS、RT(P50/P90/P99)、错误率、线程池、队列深度
- ✅ **数据库**: 慢查询 Top10、连接池使用率、锁等待
- ✅ **系统层**: CPU、内存、磁盘 IO、网络 IO
- ✅ **中间件**: Redis 命中率、MQ 堆积深度

### 3. 瓶颈分析
- ✅ 自动识别性能拐点
- ✅ 多维数据关联分析
- ✅ 链路追踪（需要 APM 集成）
- ✅ 根因定位

### 4. 报告生成
- ✅ Markdown 格式报告
- ✅ HTML 可视化报告
- ✅ 瓶颈 Top3 排行
- ✅ 优化建议（按优先级排序）

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend/perf_tests
pip install -r requirements.txt
```

### 2. 运行压测

#### 方式一：使用 Agent 自动化执行（推荐）

```bash
# 基本用法
python perf_test_agent.py --target http://localhost:5000

# 完整参数
python perf_test_agent.py \
  --target http://localhost:5000 \
  --duration 180 \
  --users 10 \
  --stages 5 \
  --sla-p99 500 \
  --sla-error 1.0
```

**参数说明**:
- `--target`: 目标主机地址
- `--duration`: 每阶梯持续时间（秒）
- `--users`: 每阶梯增加的用户数
- `--stages`: 阶梯数量
- `--sla-p99`: P99 延迟 SLA（毫秒）
- `--sla-error`: 错误率 SLA（百分比）

#### 方式二：直接使用 Locust

```bash
# 启动 Locust Web UI
locust -f locustfile.py --host http://localhost:5000

# 浏览器打开 http://localhost:8089
# 设置用户数和 spawn rate 开始压测
```

### 3. 采集监控数据

```bash
# 独立运行监控采集器
python metrics_collector.py \
  --interval 5 \
  --duration 300 \
  --output ./results/metrics
```

### 4. 生成报告

```bash
# 生成 Markdown + HTML 报告
python report_generator.py \
  --results-dir ./results \
  --output ./reports/my_test_report.md
```

---

## 📁 目录结构

```
perf_tests/
├── locustfile.py           # Locust 压测脚本
├── perf_test_agent.py      # 性能测试 Agent（自动化执行）
├── metrics_collector.py    # 监控指标采集器
├── report_generator.py     # 报告生成器
├── requirements.txt        # Python 依赖
├── README.md              # 本文档
└── results/               # 测试结果输出目录
    ├── stage_1.csv        # 阶梯 1 压测结果
    ├── stage_2.csv        # 阶梯 2 压测结果
    ├── metrics_*.json     # 监控指标
    └── reports/           # 生成的报告
        ├── perf_report_*.md
        └── perf_report_*.html
```

---

## 📊 压测场景

### 模拟用户类型

#### 1. BlogUser（博客访客）
- 浏览文章列表（权重 3）
- 查看文章详情（权重 2）
- 查看分类/标签（权重 1）

#### 2. AuthenticatedUser（登录用户）
- 登录获取 Token
- 发表评论（权重 3）
- 点赞文章（权重 2）
- 查看管理后台（权重 1）

#### 3. AdminUser（管理员）
- 登录
- 创建文章（权重 2）
- AI 改写文章（权重 1）

### 压测接口清单

| 接口 | 方法 | 说明 | 优先级 |
|------|------|------|--------|
| `/api/v1/articles` | GET | 文章列表 | P0 |
| `/api/v1/articles/{id}` | GET | 文章详情 | P0 |
| `/api/v1/auth/login` | POST | 登录接口 | P0 |
| `/api/v1/articles/{id}/comments` | POST | 发表评论 | P1 |
| `/api/v1/articles/{id}/like` | POST | 点赞文章 | P2 |
| `/api/v1/articles` | POST | 创建文章 | P1 |
| `/api/v1/articles/{id}/ai-rewrite` | POST | AI 改写 | P2 |

---

## 🔍 瓶颈分析示例

### 案例 1：数据库慢查询

**现象**:
- 阶梯 3（60% 压力）时，`/api/v1/articles` P99 从 200ms 飙升到 1200ms
- 同一时刻数据库连接池使用率达到 95%

**Agent 分析**:
```
1. 拐点确认：600 TPS 时 RT 开始飙升
2. 关联发现：DB 连接池使用率 95%，出现排队
3. 慢查询定位：SELECT * FROM articles WHERE category_id=? 未命中索引
4. 根因：category_id 字段缺少索引，全表扫描（扫描行数 5 万+）
```

**优化建议**:
```sql
-- P0 必须修
CREATE INDEX idx_category_id ON articles(category_id);

-- 预期效果：查询从 800ms 降到 5ms
```

### 案例 2：缓存穿透

**现象**:
- 阶梯 2（40% 压力）时，Redis 命中率从 92% 暴跌到 15%
- 数据库 QPS 激增 5 倍

**Agent 分析**:
```
1. 缓存命中率骤降 → 大量请求穿透到 DB
2. 根因：缓存 key 设计问题，含分页参数导致碎片化
3. 缓存淘汰：key 数量超过 maxmemory 触发 LRU 淘汰
```

**优化建议**:
```python
# P1 强烈建议
# 修改前：cache_key = f"article_list:{page}:{limit}"
# 修改后：cache_key = f"article_list:{page}"  # 去掉 limit
```

---

## 📈 报告示例

### 性能基线

| 接口 | 最大 TPS | 目标 TPS | 差距 | 状态 |
|------|---------|---------|------|------|
| `POST /orders/create` | 280 | 500 | -44% | ❌ |
| `GET /products/{id}` | 2100 | 2000 | +5% | ✅ |
| `POST /payments/pay` | 310 | 300 | +3% | ✅ |

### 瓶颈 Top3

| 排名 | 接口 | 瓶颈 | 证据 | 影响 |
|------|------|------|------|------|
| 1 | orders/create | DB 慢查询 | 无索引，扫描 12 万行 | 拖垮连接池 |
| 2 | orders/create | 连接池过小 | 高峰排队 15+ | 放大 RT |
| 3 | orders/create | 无本地缓存 | 每次都查 DB | 增加 DB 压力 |

### 优化建议（按优先级）

1. **P0 - 必须修**: orders 表加 user_id 索引  
   预期效果：查询从 120ms 降到 5ms

2. **P0 - 必须修**: DB 连接池从 20 调到 50  
   预期效果：高峰不再排队

3. **P2 - 建议优化**: 热门商品信息加 Redis 缓存  
   预期效果：DB QPS 降低 40%

---

## ⚠️ 常见坑点

### 1. 阶梯加压不当
❌ **错误做法**: 上来就 100% 压力 → 系统直接崩溃，找不到拐点  
✅ **正确做法**: 10% → 30% → 50% → 80% → 100% 逐步加压

### 2. 只看平均值
❌ **错误**: 平均 RT 100ms 看着没问题  
✅ **正确**: 看 P99（3 秒），1% 的用户体验极差

### 3. 压测环境与生产不一致
❌ **错误**: 压测 4 核 8G，生产 16 核 32G  
✅ **正确**: 数据库配置、连接池、缓存大小至少对齐

### 4. 不做回归验证
❌ **错误**: 加了索引就觉得好了，不再压测  
✅ **正确**: 每次优化后用相同压力重新验证

---

## 🎯 最佳实践

### 1. 压测前准备
- ✅ 确保压测环境配置与生产一致
- ✅ 准备足够的测试数据（至少 10 万级）
- ✅ 配置监控告警（CPU > 80%、内存 > 85%、错误率 > 5%）

### 2. 压测中观察
- ✅ 实时关注 TPS、RT、错误率曲线
- ✅ 发现异常立即暂停，避免系统崩溃
- ✅ 记录每个阶梯的稳态数据

### 3. 压测后分析
- ✅ 找到 TPS 拐点对应的压力水位
- ✅ 关联分析 RT 飙高时刻的监控指标
- ✅ 输出可执行的优化建议

### 4. 优化验证
- ✅ 每次只优化一个变量，便于评估效果
- ✅ 用相同压力重新压测
- ✅ 对比优化前后的性能指标

---

## 🔧 高级用法

### 自定义压测场景

编辑 `locustfile.py`，添加自定义用户行为：

```python
class CustomUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(5)
    def custom_scenario(self):
        # 你的自定义场景
        self.client.get("/api/v1/custom")
```

### 集成到 CI/CD

```yaml
# .github/workflows/perf-test.yml
name: Performance Test

on:
  push:
    branches: [main]

jobs:
  perf-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd backend/perf_tests
          pip install -r requirements.txt
      
      - name: Run performance test
        run: |
          python perf_test_agent.py \
            --target http://localhost:5000 \
            --duration 180 \
            --users 10 \
            --stages 3
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: perf-report
          path: backend/perf_tests/results/reports/
```

### 与 APM 集成

集成 SkyWalking、Jaeger 等 APM 工具，实现链路追踪：

```python
# 在 perf_test_agent.py 中添加
def collect_trace_data(self, request_id: str):
    """采集链路追踪数据"""
    # 调用 APM API 获取完整调用链
    # 分析每个 Span 的耗时
    # 定位耗时最长的节点
```

---

## 📚 参考资源

- [Locust 官方文档](https://docs.locust.io/)
- [perf-test-agent 设计理念](https://mp.weixin.qq.com/s/7-WWWklVg-qp4rSW6dJtsA)
- [性能测试最佳实践](https://www.perfma.com/blog)

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个性能测试框架！

---

**最后更新**: 2026-05-23  
**维护者**: AI Assistant
