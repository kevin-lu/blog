# Gitee AI 代码审查配置指南

本文档介绍如何在 Gitee 配置 AI 代码审查系统。

---

## 📋 配置步骤

### 步骤 1: 获取 Gitee 私人令牌

1. 访问：https://gitee.com/profile/personal_access_tokens
2. 点击 "生成新的令牌"
3. 勾选权限：
   - ✅ `pull_requests` - 读取 PR 信息
   - ✅ `projects` - 访问项目
   - ✅ `issues` - 发布评论
4. 生成并复制令牌

**令牌格式**：
```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### 步骤 2: 配置 Gitee Go Secrets

Gitee 的 Secrets 配置位置：

```
仓库 → 设置 → 密钥管理 → 添加密钥
```

或者访问：
```
https://gitee.com/kevin_lu/blog/settings/secrets
```

**添加以下密钥**：

| 密钥名称 | 值 | 必填 |
|---------|---|------|
| `GITEE_TOKEN` | 你的 Gitee 私人令牌 | ✅ |
| `LLM_API_KEY` | Kimi API 密钥 | ✅ |
| `LLM_API_URL` | `https://api.moonshot.cn/v1/chat/completions` | ✅ |
| `LLM_MODEL` | `moonshot-v1-8k` | （可选） |

---

### 步骤 3: 启用 Gitee Go

1. 访问：https://gitee.com/kevin_lu/blog/gitee_go
2. 点击 "启用 Gitee Go"
3. 同意授权

---

### 步骤 4: 验证配置

#### 方式 1: 手动触发工作流

1. 访问：https://gitee.com/kevin_lu/blog/gitee_go/workflows
2. 找到 "AI Code Review (Gitee)"
3. 点击 "运行工作流"
4. 选择分支 `test/ai-code-review`
5. 点击 "运行"

#### 方式 2: 创建 PR 自动触发

1. 在 Gitee 创建 PR
2. 工作流自动触发
3. 查看运行状态

---

## 🔄 GitHub vs Gitee 对比

| 特性 | GitHub | Gitee |
|------|--------|-------|
| **访问速度** | 慢（需要代理） | 快（国内） |
| **工作流名称** | GitHub Actions | Gitee Go |
| **Secrets 位置** | Settings → Secrets | 设置 → 密钥管理 |
| **API Base URL** | https://api.github.com | https://gitee.com/api/v5 |
| **令牌名称** | GITHUB_TOKEN | GITEE_TOKEN |
| **触发条件** | `pull_request` | `pull_request` |

---

## 📝 工作流文件

Gitee 工作流文件位置：
```
.gitee/workflows/ai-code-review.yml
```

GitHub 工作流文件位置：
```
.github/workflows/ai-code-review.yml
```

**主要区别**：

```yaml
# GitHub
uses: actions/checkout@v4
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

# Gitee
uses: actions/checkout@v4
env:
  GITEE_TOKEN: ${{ secrets.GITEE_TOKEN }}
```

---

## 🧪 测试流程

### 1. 推送到 Gitee

```bash
git push gitee test/ai-code-review
```

### 2. 在 Gitee 创建 PR

访问：
```
https://gitee.com/kevin_lu/blog/pulls
```

点击 "新建 Pull Request"

- 源分支：`test/ai-code-review`
- 目标分支：`dev_lzb_v4.0`
- 标题：`🧪 测试 AI 代码审查`
- 描述：测试 AI 代码审查系统

### 3. 查看运行状态

访问：
```
https://gitee.com/kevin_lu/blog/gitee_go
```

查看工作流运行状态和日志

### 4. 查看 AI 评论

PR 页面会显示 AI 审查报告：
- 综合审查报告
- 行内评论
- 修复建议

---

## ⚠️ 注意事项

### 1. Gitee Go 限制

- 免费额度：每月 2000 分钟
- 并发限制：最多 5 个并发任务
- 超时限制：最长 6 小时

### 2. API 调用限制

- Gitee API 速率限制：5000 次/小时
- 建议添加重试逻辑

### 3. Secrets 安全

- 不要将密钥提交到代码库
- 定期轮换密钥
- 限制密钥权限

---

## 🔍 故障排查

### 问题 1: 工作流未触发

**检查**：
- 工作流文件是否在 `.gitee/workflows/` 目录
- YAML 语法是否正确
- Gitee Go 是否已启用

### 问题 2: Secrets 未生效

**检查**：
- 密钥名称是否正确（区分大小写）
- 密钥值是否正确
- 是否需要重新运行工作流

### 问题 3: API 调用失败

**检查**：
- GITEE_TOKEN 是否有效
- 令牌权限是否足够
- API 速率限制

---

##  参考资源

- [Gitee Go 文档](https://gitee.com/help/articles/406)
- [Gitee API 文档](https://gitee.com/api/v5/swagger)
- [Gitee 密钥管理](https://gitee.com/help/articles/416)

---

## ✅ 配置检查清单

- [ ] 已获取 Gitee 私人令牌
- [ ] 已启用 Gitee Go
- [ ] 已添加 `GITEE_TOKEN` Secret
- [ ] 已添加 `LLM_API_KEY` Secret
- [ ] 已添加 `LLM_API_URL` Secret
- [ ] 工作流文件在 `.gitee/workflows/` 目录
- [ ] 已推送测试分支到 Gitee
- [ ] 已创建测试 PR
- [ ] 工作流成功运行
- [ ] AI 审查报告已发布

---

*最后更新：2026-05-30 | 适用于 Gitee Go*
