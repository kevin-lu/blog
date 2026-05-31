# 分层代码审查体系使用指南

## 概述

本项目的代码审查分为三层，层层递进，确保代码质量：

```
┌─────────────────────────────────────┐
│  第一层：OpenCodeReview（5 分钟）      │
│  - 代码规范检查（Flake8/Black/isort） │
│  - 快速失败，及早发现问题             │
└──────────────┬──────────────────────┘
               │
               ▼
─────────────────────────────────────┐
│  第二层：SonarQube（15 分钟）         │
│  - 3000+ 规则全面扫描                 │
│  - 质量门禁评估                       │
│  - 技术债务量化                       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  第三层：AI 深度审查（20 分钟）         │
│  - 业务逻辑理解                       │
│  - 结构性 bug 检测                    │
│  - 综合分析和建议                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  统一评论报告                         │
└─────────────────────────────────────┘
```

## 工作流程

### 自动触发

当你创建或更新 PR 时，自动触发三层审查：

```yaml
on:
  pull_request:
    branches: [main, master, develop]
```

### 手动触发

也可以通过 GitHub Actions 手动触发：

1. 进入 Actions 标签
2. 选择 "Layered Code Review"
3. 输入 PR 编号
4. 点击 "Run workflow"

## 审查结果解读

### 第一层：OpenCodeReview

**通过标准：**
- ✅ 符合代码规范（Flake8/Black/isort）
- ️ 发现规范问题

**失败处理：**
- 查看具体问题列表
- 运行 `black .` 和 `isort .` 自动修复
- 重新提交 PR

### 第二层：SonarQube

**通过标准：**
- ✅ 质量门禁通过
- Bug: 0
- 漏洞：0
- 异味：< 10

**失败处理：**
- 访问 SonarCloud 查看详细信息
- 优先修复 Bug 和漏洞
- 逐步减少技术债务

### 第三层：AI 深度审查

**通过标准：**
- ✅ LGTM - Looks Good To Me
- ⚠️ Needs Work - 需要改进
- ❌ Has Critical Issues - 存在严重问题

**重点关注：**
- N+1 查询
- 竞态条件
- 信任边界违规
- 逃逸 bug

## 配置说明

### GitHub Secrets

需要配置以下 Secrets：

| 名称 | 说明 | 获取方式 |
|------|------|----------|
| SONAR_TOKEN | SonarCloud Token | SonarCloud → My Account → Security |
| SONAR_HOST_URL | SonarCloud URL | https://sonarcloud.io |
| SONAR_PROJECT_KEY | Sonar 项目 Key | SonarCloud 项目页面 |
| LLM_API_KEY | Kimi API Key | Moonshot AI 控制台 |
| LLM_API_URL | Kimi API URL | https://api.moonshot.cn/v1/chat/completions |
| LLM_MODEL | Kimi 模型 | moonshot-v1-8k |

### 本地运行

虽然审查在 GitHub Actions 运行，但你可以本地预览：

```bash
# 安装依赖
pip install flake8 black isort

# 运行 OpenCodeReview
python .github/scripts/run_open_code_review.py
```

## 最佳实践

### 1. 及早运行

不要等到 PR 完成才运行审查。建议：
- 本地开发时运行 OpenCodeReview
- 提交前运行 SonarQube 扫描
- 创建 PR 后等待 AI 审查

### 2. 分层修复

发现问题时，按优先级修复：
1. **Critical Issues**（AI 发现）- 立即修复
2. **规范问题**（OpenCodeReview）- 必须修复
3. **技术债务**（SonarQube）- 逐步修复

### 3. 持续改进

- 每次审查后阅读 AI 建议
- 定期查看 SonarQube 趋势
- 团队分享常见问题

## 故障排查

### 工作流失败

**症状：** 工作流显示红色 X

**排查步骤：**
1. 点击失败的步骤查看详情
2. 查看错误日志
3. 常见问题：
   - 网络超时 → 重试
   - API 限流 → 等待后重试
   - 配置错误 → 检查 Secrets

### AI 审查失败

**症状：** AI 审查步骤失败

**可能原因：**
- Kimi API 超载 → 自动重试 3 次
- Token 超限 → 自动截断 diff
- 配置错误 → 检查环境变量

### SonarQube 失败

**症状：** 质量门禁失败

**排查步骤：**
1. 访问 SonarCloud 项目页面
2. 查看质量门禁详情
3. 修复不达标的项目

## 常见问题

### Q: 三层审查需要多长时间？
A: 总共约 40 分钟（5 + 15 + 20），但并行运行，实际等待时间约 20 分钟。

### Q: 可以跳过某层审查吗？
A: 不建议。每层有不同的侧重点，缺一不可。

### Q: AI 审查准确吗？
A: AI 审查基于 Kimi 大模型，能发现结构性 bug，但仍需人工复核。

### Q: 如何查看历史审查记录？
A: 在 GitHub Actions 页面查看所有运行记录。

## 相关文档

- [SonarCloud 配置指南](SONARQUBE-SETUP.md)
- [OpenCodeReview 配置指南](OPEN-CODEREVIEW-SETUP.md)
- [代码审查最佳实践](BEST-PRACTICES.md)
