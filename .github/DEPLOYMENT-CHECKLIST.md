# AI 代码审查自动化 - 部署清单

## ✅ 已完成的工作

### 1. GitHub Actions 工作流

**文件**: `.github/workflows/ai-code-review.yml`

**功能**:
- ✅ 静态分析（Flake8 + Black + Mypy）
- ✅ 前端检查（Lint + Build + Type Check）
- ✅ AI 深度审查（集成 gstack-review skill）
- ✅ 自动评论（综合报告 + 行内评论）
- ✅ 自动修复（Critical 问题）

**触发条件**:
- PR 创建/更新时自动触发
- 支持手动触发（workflow_dispatch）

---

### 2. Python 脚本

#### 2.1 AI 代码审查脚本
**文件**: `.github/scripts/ai_code_review.py`

**功能**:
- 读取 PR diff
- 读取静态分析结果
- 调用 LLM API 进行深度审查
- 生成结构化审查报告（JSON 格式）
- 审查重点：N+1 查询、竞态条件、信任边界等

#### 2.2 评论发布脚本
**文件**: `.github/scripts/post_review_comments.py`

**功能**:
- 发布综合审查报告到 PR
- 创建行内评论（针对具体问题）
- 格式化问题和修复建议

#### 2.3 自动修复脚本
**文件**: `.github/scripts/ai_auto_fix.py`

**功能**:
- 识别 Critical/High 问题
- 自动应用修复代码
- 创建修复分支
- 提交修复代码

#### 2.4 修复 PR 创建脚本
**文件**: `.github/scripts/create_fix_pr.py`

**功能**:
- 创建修复 PR
- 关联原始 PR
- 添加标签和评论

---

### 3. 文档

#### 3.1 快速入门
**文件**: `.github/AI-CODE-REVIEW.md`

**内容**:
- 快速开始指南
- 工作流程图
- 审查重点说明
- 输出示例
- 最佳实践

#### 3.2 详细配置指南
**文件**: `.github/AI-CODE-REVIEW-GUIDE.md`

**内容**:
- 系统架构
- 配置步骤详解
- 故障排查
- 效果评估指标
- 扩展方向

#### 3.3 测试脚本
**文件**: `.github/test-ai-review.sh`

**功能**:
- 自动创建测试分支
- 生成测试代码（包含 N+1 查询、信任边界问题）
- 创建测试 PR
- 提供监控命令

---

## 🚀 部署步骤

### 步骤 1: 配置 GitHub Secrets

```
Settings → Secrets and variables → Actions → New repository secret

添加以下 Secrets:
```

| Secret 名称 | 说明 | 必填 |
|------------|------|------|
| `LLM_API_KEY` | LLM API 密钥 | ✅ |
| `LLM_API_URL` | LLM API 地址 | ❌ (默认 OpenAI) |
| `OPENAI_API_KEY` | OpenAI API 密钥 | ❌ (如用 OpenAI) |

### 步骤 2: 安装 Python 依赖

```bash
cd backend
pip install PyGithub requests
```

或添加到 `requirements.txt`:

```txt
PyGithub>=1.57
requests>=2.28
```

### 步骤 3: 测试部署

**方法 1: 自动测试脚本**

```bash
.github/test-ai-review.sh
```

**方法 2: 手动测试**

```bash
# 1. 创建测试分支
git checkout -b test/ai-review

# 2. 做一些修改
echo "# Test" >> README.md
git add README.md
git commit -m "Test AI review"

# 3. 推送
git push origin test/ai-review

# 4. 在 GitHub 创建 PR
```

### 步骤 4: 验证工作流

```
1. 打开 GitHub Actions
2. 找到 "AI Code Review" 工作流
3. 查看最新运行
4. 检查所有步骤是否成功：
   ✓ Static Analysis
   ✓ Frontend Analysis
   ✓ AI Deep Review
   ✓ Post Review Comments
```

---

## 📊 预期效果

### 审查报告示例

当 PR 触发后，你会看到：

```markdown
## 🤖 AI 代码审查报告

**审查时间**: 2026-05-29T10:30:00
**审查文件数**: 5
**置信度**: 85%

### 📊 总体评价

**结论**: ⚠️ Needs Work

**总结**: 发现 2 个 Critical 问题

### 🚨 Critical 问题 (2 个)

#### 1. N+1 查询
- **文件**: `backend/app/api/articles.py`:45
- **描述**: 循环中查询数据库
- **建议**: 使用批量查询

#### 2. 信任边界违规
- **文件**: `backend/app/api/comments.py`:78
- **描述**: 未验证用户输入
- **建议**: 添加输入验证
```

### 自动修复流程

如果开启自动修复：

```
1. AI 发现 Critical 问题
2. 自动创建分支：ai-fix/pr-123
3. 应用修复代码
4. 提交并推送
5. 创建修复 PR #124
6. 在原 PR #123 中评论通知
```

---

## 🔍 故障排查

### 问题 1: 工作流未触发

**检查**:
- 文件是否在正确位置：`.github/workflows/ai-code-review.yml`
- YAML 语法是否正确
- PR 是否 targeting 正确分支

### 问题 2: AI 审查失败

**检查**:
```bash
# 查看 Secret 配置
echo $LLM_API_KEY

# 测试 API 连通性
curl -X POST $LLM_API_URL \
  -H "Authorization: Bearer $LLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4","messages":[{"role":"user","content":"test"}]}'
```

### 问题 3: 无法创建评论

**检查**:
- GITHUB_TOKEN 权限是否足够
- 文件路径是否匹配
- commit SHA 是否有效

### 查看详细日志

```
Actions → AI Code Review → 最新运行 → 查看日志
```

---

## 📈 效果指标

建议跟踪以下指标：

| 指标 | 目标值 | 计算方式 |
|------|--------|---------|
| 审查覆盖率 | >90% | AI 审查 PR 数 / 总 PR 数 |
| Critical 问题发现数 | 持续下降 | 每周发现数 |
| 自动修复成功率 | >60% | 成功修复数 / 总 Critical 数 |
| 平均审查时间 | <10 分钟 | PR 创建到审查完成 |
| 人类审核时间 | <24 小时 | 审查完成到合并 |

---

## 🎯 下一步扩展

### 短期（1-2 周）

- [ ] 集成 SonarQube
- [ ] 添加安全扫描（Snyk）
- [ ] 自定义审查规则
- [ ] 周报自动生成

### 中期（1 个月）

- [ ] 集成 ELK 日志分析
- [ ] 性能问题自动检测
- [ ] 数据库查询优化建议
- [ ] 并发问题检测

### 长期（2-3 个月）

- [ ] 完整开发流程自动化
- [ ] AI 需求对齐
- [ ] AI 技术方案生成
- [ ] AI 自动测试
- [ ] AI 自动部署

---

## 📚 参考资源

- [gstack-review skill](../.trae/skills/gstack-review/SKILL.md)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [PyGithub 文档](https://pygithub.readthedocs.io/)
- [OpenAI API 文档](https://platform.openai.com/docs)

---

## 👥 维护信息

**创建时间**: 2026-05-29
**维护者**: AI SRE Team
**版本**: v1.0

**更新日志**:
- v1.0 (2026-05-29): 初始版本
  - AI 深度审查
  - 自动评论
  - 自动修复
  - 完整文档

---

*基于 gstack-review skill 构建 | 寻找生产级 bug*
