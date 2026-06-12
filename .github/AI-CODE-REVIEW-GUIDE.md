# AI 代码审查自动化配置指南

本文档介绍如何配置和使用 AI 代码审查自动化系统。

---

## 📋 系统架构

```
PR 创建 → 静态分析 → AI 深度审查 → 自动评论 → (可选) 自动修复 → 人类审核
```

### 工作流程

1. **阶段 1: 静态分析** (快速失败)
   - Flake8 代码检查
   - Black 格式检查
   - Mypy 类型检查

2. **阶段 2: AI 深度审查** (核心)
   - 集成 gstack-review skill
   - 寻找生产级 bug（N+1 查询、竞态条件等）
   - 生成结构化审查报告

3. **阶段 3: 自动评论**
   - 发布综合审查报告
   - 创建行内评论（针对具体问题）

4. **阶段 4: 自动修复** (可选)
   - 检测 Critical 问题
   - AI 自动生成修复
   - 创建修复 PR

---

## 🔧 配置步骤

### 1. GitHub Secrets 配置

在 GitHub 仓库中添加以下 Secrets：

```
Settings → Secrets and variables → Actions → New repository secret
```

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `LLM_API_KEY` | LLM API 密钥 | `sk-xxx` |
| `LLM_API_URL` | LLM API 地址 | `https://api.openai.com/v1/chat/completions` |
| `GITHUB_TOKEN` | GitHub Token（自动创建） | 自动生成 |

**可选**（如果使用其他 LLM）：
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `QWEN_API_KEY`

### 2. 安装 Python 依赖

脚本需要的依赖：

```bash
cd backend
pip install PyGithub requests pyyaml
```

或在 requirements.txt 中添加：

```txt
PyGithub>=1.57
requests>=2.28
pyyaml>=6.0
```

### 3. 测试配置

#### 测试 1: 手动触发工作流

```bash
# 1. 创建一个测试分支
git checkout -b test/ai-review

# 2. 做一些修改
echo "# Test change" >> README.md
git add README.md
git commit -m "Test: 触发 AI 审查"

# 3. 推送到 GitHub
git push origin test/ai-review

# 4. 创建 PR
# 在 GitHub 上创建 PR，查看 Actions 是否触发
```

#### 测试 2: 查看工作流日志

```
Actions → AI Code Review → 最新运行

检查点：
✓ Static Analysis 完成
✓ AI Deep Review 完成
✓ Post Review Comments 完成
```

---

## 📊 审查报告示例

### 综合评论格式

```markdown
## 🤖 AI 代码审查报告

**审查时间**: 2026-05-29T10:30:00
**审查文件数**: 5
**置信度**: 85%

### 📊 总体评价

**结论**: ⚠️ Needs Work

**总结**: 发现 2 个 Critical 问题，需要修复后重新审查

### 🚨 Critical 问题 (2 个)

#### 1. N+1 查询
- **文件**: `backend/app/api/articles.py`:45
- **描述**: 循环中查询数据库，会导致性能问题
- **建议**: 使用批量查询优化

#### 2. 信任边界违规
- **文件**: `backend/app/api/comments.py`:78
- **描述**: 未验证用户输入直接使用
- **建议**: 添加输入验证

### ✅ 优点

- 代码结构清晰
- 异常处理完善

### 💡 改进建议

- 添加更多单元测试
- 优化数据库查询
```

### 行内评论格式

```markdown
**🔴 N+1 查询**

循环中查询数据库，会导致性能问题

**建议**: 使用批量查询优化

```python
# 优化后
user_ids = [u.id for u in users]
posts = db.query(Post).filter(Post.user_id.in_(user_ids)).all()
```
```

---

## 🤖 自动修复功能

### 何时触发

当 AI 审查发现 **Critical** 或 **High** 级别问题时，会自动触发修复流程：

1. AI 尝试自动应用修复
2. 创建修复分支 `ai-fix/pr-{number}`
3. 提交修复代码
4. 创建新的修复 PR
5. 在原 PR 中评论通知

### 修复 PR 示例

```markdown
## 🤖 AI Fix: 自动修复 PR #123 的 Critical 问题

此 PR 自动修复 PR #123 中发现的 Critical 问题。

### 修复内容

- N+1 查询问题 (backend/app/api/articles.py)
- 信任边界违规 (backend/app/api/comments.py)

### 原始 PR

- 原始 PR: #123
- 触发原因：代码审查发现 Critical 问题
- 修复分支：ai-fix/pr-123

### 审核清单

- [ ] 修复正确，未引入新问题
- [ ] 代码逻辑符合预期
- [ ] 测试通过
```

---

## 🎯 最佳实践

### 1. 早审查，勤审查

- 每个 PR 都触发 AI 审查
- 不要等到大 PR 才审查
- 小步快跑，快速迭代

### 2. 正确处理审查结果

**Critical 问题**：
- 立即修复
- 或接受 AI 自动修复

**High 问题**：
- 在合并前修复
- 记录技术债务

**Medium/Low 问题**：
- 可以稍后修复
- 记录到 Issue 跟踪

### 3. 人类审核不可替代

AI 审查是辅助，人类审核是关键：

- AI 可能误报
- AI 可能漏报
- 业务逻辑需要人类判断

### 4. 持续优化

- 根据误报调整 prompt
- 根据漏报补充审查规则
- 定期回顾审查质量

---

## 🔍 故障排查

### 问题 1: AI 审查失败

**症状**: `AI Deep Review` 步骤失败

**检查**:
1. LLM_API_KEY 是否正确
2. LLM_API_URL 是否可达
3. Diff 是否过大（超过 token 限制）

**解决**:
```bash
# 检查 Secret
echo $LLM_API_KEY

# 测试 API
curl -X POST $LLM_API_URL \
  -H "Authorization: Bearer $LLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4","messages":[{"role":"user","content":"test"}]}'
```

### 问题 2: 无法创建行内评论

**症状**: 只有综合评论，没有行内评论

**原因**: 可能是文件路径不匹配或 commit SHA 过期

**解决**: 检查脚本中的文件路径解析逻辑

### 问题 3: 自动修复未触发

**症状**: 有 Critical 问题但没有自动修复

**检查**:
1. `has_critical` 输出是否正确
2. `auto-fix-critical` job 是否跳过

**解决**: 查看工作流日志中的条件判断

---

## 📈 效果评估

### 指标跟踪

建议跟踪以下指标：

| 指标 | 计算方式 | 目标值 |
|------|---------|--------|
| 审查覆盖率 | AI 审查 PR 数 / 总 PR 数 | >90% |
| Critical 问题发现数 | 每周发现的 Critical 问题数 | 持续下降 |
| 自动修复成功率 | 自动修复成功数 / 总 Critical 数 | >60% |
| 审查时间 | PR 创建到审查完成的时间 | <10 分钟 |
| 人类审核时间 | 审查完成到合并的时间 | <24 小时 |

### 周报生成

可以用以下脚本生成周报：

```python
# .github/scripts/generate_weekly_report.py
def generate_report():
    report = """
# AI 代码审查周报

## 本周统计
- 审查 PR 数：X
- 发现 Critical 问题：Y
- 自动修复成功：Z
- 平均审查时间：T 分钟
    """
    return report
```

---

## 🚀 扩展方向

### 1. 集成更多审查规则

- SQL 注入检测
- XSS 漏洞检测
- 敏感信息泄露检测
- 性能反模式检测

### 2. 集成更多工具

- SonarQube
- CodeClimate
- Snyk（安全扫描）
- Semgrep（静态分析）

### 3. 自定义审查规则

根据项目特点定制：

```python
# .github/scripts/custom_checks.py
def check_n_plus_one(diff):
    """检测 N+1 查询"""
    # 自定义逻辑
    
def check_race_condition(diff):
    """检测竞态条件"""
    # 自定义逻辑
```

---

## 📚 参考资源

- [gstack-review skill](../../.trae/skills/gstack-review/SKILL.md)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [PyGithub 文档](https://pygithub.readthedocs.io/)

---

*最后更新：2026-05-29 | 维护者：AI SRE Team*
