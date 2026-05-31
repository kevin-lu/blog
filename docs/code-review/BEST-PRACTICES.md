# 代码审查最佳实践

## 审查文化

### 1. 建设性反馈

**好的反馈：**
```
这个查询在循环内执行，会导致 N+1 问题。
建议：移到循环外，使用批量查询。
```

**不好的反馈：**
```
这代码太慢了
```

### 2. 及时响应

- 收到审查通知后 24 小时内响应
- 如果无法及时处理，说明原因和时间表
- 紧急 PR 标注优先级

### 3. 分层审查的价值

**OpenCodeReview：**
- 确保团队代码风格一致
- 减少低级错误
- 提高代码可读性

**SonarQube：**
- 量化技术债务
- 发现潜在 bug
- 跟踪质量趋势

**AI 深度审查：**
- 发现人类容易忽略的结构性 bug
- 提供客观的第三方视角
- 学习最佳实践

## 常见问题模式

### N+1 查询

**问题代码：**
```python
for user in users:
    orders = Order.query.filter_by(user_id=user.id).all()
```

**修复：**
```python
orders = Order.query.filter(
    Order.user_id.in_([u.id for u in users])
).all()
```

### 竞态条件

**问题代码：**
```python
if balance >= amount:
    account.balance -= amount
```

**修复：**
```python
with db.transaction():
    account = Account.query.with_for_update().get(account_id)
    if account.balance >= amount:
        account.balance -= amount
```

### 信任边界违规

**问题代码：**
```python
query = f"SELECT * FROM users WHERE id = {user_input}"
```

**修复：**
```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_input,))
```

### 硬编码配置

**问题代码：**
```python
timeout = 30  # 为什么是 30？
max_retries = 3
```

**修复：**
```python
# 配置常量
DEFAULT_TIMEOUT = 30  # 秒
MAX_RETRIES = 3

timeout = DEFAULT_TIMEOUT
```

### 缺少错误处理

**问题代码：**
```python
response = requests.get(url)
data = response.json()
```

**修复：**
```python
try:
    response = requests.get(url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    data = response.json()
except requests.RequestException as e:
    logger.error(f"API 请求失败：{e}")
    raise
```

## 持续改进

### 每周审查

- 查看 SonarQube 趋势图
- 分析 AI 发现的常见问题
- 团队分享和讨论

### 月度回顾

- 审查通过率趋势
- 技术债务变化
- 流程优化建议

### 季度目标

- 减少 50% 技术债务
- 提高审查覆盖率
- 建立问题模式库

## 审查清单

### 代码规范（OpenCodeReview）

- [ ] 代码格式符合 Black 规范
- [ ] 导入顺序符合 isort 规范
- [ ] 没有 Flake8 报告的语法错误
- [ ] 变量命名清晰有意义

### 代码质量（SonarQube）

- [ ] 没有 Bug
- [ ] 没有安全漏洞
- [ ] 代码异味 < 10
- [ ] 重复率 < 3%
- [ ] 测试覆盖率 > 80%

### 结构设计（AI 审查）

- [ ] 没有 N+1 查询
- [ ] 没有竞态条件
- [ ] 没有信任边界违规
- [ ] 错误处理完整
- [ ] 日志记录适当

### 业务逻辑

- [ ] 代码符合业务需求
- [ ] 边界条件处理正确
- [ ] 输入验证完整
- [ ] 输出格式正确

## 工具使用

### 本地开发

```bash
# 安装开发工具
pip install -r requirements-dev.txt

# 运行所有检查
python .github/scripts/run_open_code_review.py

# 自动格式化
black .
isort .
```

### CI/CD

```yaml
- name: Run OpenCodeReview
  run: python .github/scripts/run_open_code_review.py

- name: SonarQube Scan
  uses: sonarsource/sonarqube-scan-action@v3

- name: AI Deep Review
  run: python .github/scripts/ai_comprehensive_review.py
```

## 度量指标

### 质量指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| Bug 数 | 0 | 严重 bug 必须为 0 |
| 漏洞数 | 0 | 安全漏洞必须为 0 |
| 技术债务比 | < 5% | 债务时间/开发时间 |
| 重复率 | < 3% | 重复代码比例 |
| 测试覆盖率 | > 80% | 单元测试覆盖率 |

### 流程指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 审查通过率 | > 90% | 首次审查通过率 |
| 平均修复时间 | < 24h | 发现问题到修复时间 |
| 审查覆盖度 | 100% | 所有 PR 都需审查 |

## 角色职责

### 开发者

- 提交前运行本地检查
- 及时响应审查意见
- 修复发现的问题
- 学习最佳实践

### 审查者（AI + 人工）

- 提供建设性反馈
- 识别结构性问题
- 分享领域知识
- 确保代码质量

### 技术负责人

- 设定质量标准
- 跟踪度量指标
- 优化审查流程
- 组织培训分享

## 持续学习

### 推荐资源

- 《代码大全》
- 《重构：改善既有代码的设计》
- 《Clean Code》
- SonarQube 官方文档
- Kimi AI 使用指南

### 内部知识库

- 常见问题模式库
- 最佳实践案例
- 技术债务追踪
- 审查历史记录
