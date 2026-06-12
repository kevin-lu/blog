# 性能测试实战示例

本文档展示如何使用性能测试 Agent 发现和解决真实性能问题。

---

## 🎯 场景 1：大促前性能验证

### 背景
双 11 大促即将到来，预计流量是平时的 5 倍。需要对核心接口进行性能验证。

### 测试目标
- 文章列表接口：目标 2000 TPS
- 文章详情接口：目标 5000 TPS
- 评论接口：目标 500 TPS
- P99 延迟 < 500ms
- 错误率 < 1%

### 执行步骤

#### 1. 准备测试数据
```bash
# 创建测试数据脚本
cd backend
python scripts/create_test_data.py --articles 10000 --comments 50000
```

#### 2. 运行压测
```bash
cd perf_tests

# 设置环境变量
export TARGET_HOST=http://prod-server:5000
export DURATION=300  # 每阶梯 5 分钟
export USERS=20
export STAGES=5

# 执行压测
./run_perf_test.sh
```

#### 3. 查看报告
```bash
# 打开 HTML 报告
open results/reports/perf_report_*.html
```

### 实际案例

**发现的问题**:
```
🔴 瓶颈 #1: slow_query
- 接口：GET /api/v1/articles
- 证据：慢查询数量 5，最慢 1200ms
- 根因：category_id 字段无索引

🔴 瓶颈 #2: database_connection_pool  
- 接口：Database
- 证据：连接池使用率 98%
- 根因：pool_size=10 太小
```

**优化方案**:
```sql
-- 1. 添加索引
CREATE INDEX idx_category_id ON articles(category_id);
CREATE INDEX idx_tag_id ON article_tags(tag_id);

-- 2. 增加连接池
# app/config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 50,  # 从 10 增加到 50
    'max_overflow': 100
}
```

**优化后验证**:
```bash
# 用相同压力重新压测
./run_perf_test.sh

# 对比结果
优化前：TPS 800, P99 1200ms
优化后：TPS 2500, P99 180ms  ✅ 达标
```

---

## 🔍 场景 2：性能问题排查

### 背景
用户反馈文章列表页加载很慢，有时超过 5 秒。

### 排查步骤

#### 1. 复现问题
```bash
# 对可疑接口进行压测
python perf_test_agent.py \
  --target http://localhost:5000 \
  --duration 60 \
  --users 5 \
  --stages 3
```

#### 2. 采集监控
```bash
# 启动监控采集器
python metrics_collector.py \
  --interval 2 \
  --duration 120
```

#### 3. 分析数据
```bash
# 生成分析报告
python report_generator.py
```

### 实际案例

**监控数据显示**:
```
阶梯 2 (40% 压力):
- TPS: 600 → 突然下降到 200
- P99: 300ms → 飙升到 5200ms
- 错误率：0% → 暴涨到 15%
- 数据库连接池：45% → 100%
- Redis 命中率：92% → 18%
```

**关联分析**:
```
1. TPS 下降时刻 = P99 飙升时刻 = 缓存命中率暴跌时刻
2. 根因：缓存 key 设计问题
   - 缓存 key: article_list:page=1:limit=10
   - 问题：limit 参数变化导致 key 碎片化
   - 结果：缓存命中率低，大量请求穿透到 DB
```

**修复方案**:
```python
# 修改前
cache_key = f"article_list:page={page}:limit={limit}"

# 修改后
cache_key = f"article_list:page={page}"  # 固定 limit=20
# 或者在应用层做分页
```

---

## 📊 场景 3：容量规划

### 背景
老板问：当前系统能承载多少并发？需要扩容吗？

### 评估方法

#### 1. 阶梯压测找拐点
```bash
# 逐步加压直到系统崩溃
python perf_test_agent.py \
  --stages 10 \
  --users 10 \
  --duration 180
```

#### 2. 记录拐点数据
```
阶梯 1 (100 用户): TPS 500, P99 120ms ✅
阶梯 2 (200 用户): TPS 1000, P99 150ms ✅
阶梯 3 (300 用户): TPS 1500, P99 200ms ✅
阶梯 4 (400 用户): TPS 1800, P99 350ms ⚠️
阶梯 5 (500 用户): TPS 1900, P99 800ms ❌ 超 SLA
阶梯 6 (600 用户): TPS 1850, P99 1500ms ❌ 系统开始拒绝服务
```

#### 3. 确定容量
```
拐点：500 用户
最大 TPS: 1900
P99 延迟：800ms (超过 SLA 500ms)

结论：
- 当前系统最大安全承载：400 并发用户
- 对应 TPS: 1800
- 大促预估 500 用户 → 需要优化
```

#### 4. 扩容建议
```
方案 1（垂直扩容）:
- 升级服务器：4 核 8G → 8 核 16G
- 成本：+¥500/月
- 预期提升：+50% 容量

方案 2（水平扩容）:
- 增加应用实例：1 台 → 2 台
- 添加负载均衡
- 成本：+¥1000/月
- 预期提升：+80% 容量

方案 3（优化优先）:
- 添加 Redis 缓存
- 数据库索引优化
- 成本：0 元（开发时间）
- 预期提升：+100% 容量

推荐：先执行方案 3，再根据效果选择方案 1 或 2
```

---

## 🎯 场景 4：代码变更性能回归

### 背景
开发提交了新的缓存优化代码，需要验证性能提升效果。

### 测试流程

#### 1. 优化前基线
```bash
# 在 main 分支运行压测
git checkout main
./run_perf_test.sh

# 保存结果
mv results results_before_optimization
```

#### 2. 优化后测试
```bash
# 切换到优化分支
git checkout feature/cache-optimization

# 运行相同压力的压测
./run_perf_test.sh

# 保存结果
mv results results_after_optimization
```

#### 3. 对比结果
```bash
# 使用对比脚本
python compare_results.py \
  --before results_before_optimization \
  --after results_after_optimization
```

### 实际案例

**对比报告**:
```
┌─────────────────────┬──────────┬──────────┬────────────┐
│ 指标                │ 优化前   │ 优化后   │ 提升       │
├─────────────────────┼──────────┼──────────┼────────────┤
│ 最大 TPS            │ 1,200    │ 2,800    │ +133% ✅   │
│ P99 延迟 (ms)       │ 850      │ 180      │ -79% ✅    │
│ 平均 RT (ms)        │ 320      │ 65       │ -80% ✅    │
│ 错误率 (%)          │ 2.3      │ 0.1      │ -96% ✅    │
│ DB QPS              │ 450      │ 120      │ -73% ✅    │
└─────────────────────┴──────────┴──────────┴────────────┘

结论：缓存优化效果显著，建议合并 ✅
```

---

## ⚠️ 场景 5：AI 接口专项测试

### 背景
AI 改写接口响应慢，需要评估是否限流合理。

### 测试配置
```python
# locustfile.py 中的 AdminUser 类

@task(1)
def ai_rewrite_article(self):
    """AI 改写文章 - 慢操作"""
    # 设置较长的超时时间
    self.client.post(
        f"/api/v1/articles/{article_id}/ai-rewrite",
        headers={"Authorization": f"Bearer {self.access_token}"},
        name="/api/v1/articles/{id}/ai-rewrite [POST]",
        catch_response=True,
        timeout=30000  # 30 秒超时
    )
```

### 执行测试
```bash
# 针对 AI 接口的专项压测
python perf_test_agent.py \
  --target http://localhost:5000 \
  --duration 300 \
  --users 5 \
  --stages 3 \
  --sla-p99 5000  # AI 接口放宽到 5 秒
```

### 结果分析
```
AI 接口性能分析:

阶梯 1 (5 用户):
- 平均 RT: 2800ms
- P99: 4200ms
- 成功率：100%

阶梯 2 (10 用户):
- 平均 RT: 5600ms
- P99: 8900ms
- 成功率：95% (5% 超时)

阶梯 3 (15 用户):
- 平均 RT: 9200ms
- P99: 15000ms
- 成功率：78% (22% 超时)

结论:
1. AI 接口在 10 并发时开始超时
2. 当前限流 30 per minute 合理
3. 建议：增加异步处理，不要阻塞请求
```

**优化建议**:
```python
# 修改为异步任务
@bp.route('/articles/<int:id>/ai-rewrite', methods=['POST'])
@jwt_required()
def rewrite_article(id):
    # 创建异步任务
    task = create_task('ai_rewrite', {'article_id': id})
    
    # 立即返回任务 ID
    return jsonify({
        'task_id': task.id,
        'status': 'queued'
    }), 202  # 不要等待 AI 处理完成
```

---

## 📈 性能测试检查清单

### 测试前
- [ ] 压测环境配置与生产一致
- [ ] 测试数据充足（至少 10 万级）
- [ ] 监控告警已配置
- [ ] 备份生产数据（如果需要）
- [ ] 通知相关人员（避免误报）

### 测试中
- [ ] 实时观察 TPS、RT、错误率
- [ ] 记录每个阶梯的稳态数据
- [ ] 发现异常立即暂停
- [ ] 保存原始数据

### 测试后
- [ ] 生成分析报告
- [ ] 识别性能瓶颈
- [ ] 提出优化建议
- [ ] 安排优化排期
- [ ] 计划回归测试

### 优化后
- [ ] 用相同压力重新压测
- [ ] 对比优化前后指标
- [ ] 确认瓶颈已解决
- [ ] 更新性能基线
- [ ] 归档测试报告

---

## 🎓 学习资源

- [Locust 官方文档](https://docs.locust.io/)
- [性能测试最佳实践](https://www.perfma.com/blog)
- [数据库优化指南](https://use-the-index-luke.com/)
- [Redis 性能优化](https://redis.io/topics/benchmarks)

---

**最后更新**: 2026-05-23
