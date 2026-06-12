#  Gitee AI 代码审查快速配置指南

## ⚡ 3 分钟快速配置

### 第一步：配置 Secrets（2 分钟）

访问：https://gitee.com/kevin_lu/blog/settings/secrets

**添加以下 4 个密钥**：

```
1. GITEE_TOKEN
   值：你的 Gitee 私人令牌
   获取地址：https://gitee.com/profile/personal_access_tokens

2. LLM_API_KEY
   值：你的 Kimi API 密钥

3. LLM_API_URL
   值：https://api.moonshot.cn/v1/chat/completions

4. LLM_MODEL
   值：moonshot-v1-8k
```

---

### 第二步：在 Gitee 创建 PR（1 分钟）

1. **访问 Gitee 仓库**
   ```
   https://gitee.com/kevin_lu/blog/pulls
   ```

2. **点击 "新建 Pull Request"**

3. **填写信息**
   - 源分支：`test/ai-code-review`
   - 目标分支：`dev_lzb_v4.0`
   - 标题：`🧪 测试 AI 代码审查`
   - 描述：`测试 AI 代码审查系统`

4. **点击 "创建 Pull Request"**

---

### 第三步：查看运行状态

**工作流会自动触发**，访问：
```
https://gitee.com/kevin_lu/blog/gitee_go
```

查看运行日志和 AI 审查结果。

---

## 📋 详细配置说明

### 获取 Gitee 私人令牌

1. 访问：https://gitee.com/profile/personal_access_tokens
2. 点击 "生成新的令牌"
3. **勾选权限**（重要！）：
   - ✅ `pull_requests` - 读取 PR 信息
   - ✅ `projects` - 访问项目
   - ✅ `issues` - 发布评论
4. 点击 "生成"
5. **立即复制令牌**（只显示一次！）

**令牌示例**：
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

### 配置 Secrets 详细步骤

1. **打开密钥管理页面**
   ```
   https://gitee.com/kevin_lu/blog/settings/secrets
   ```

2. **点击 "添加密钥"**

3. **填写密钥信息**

   **第一个密钥**：
   ```
   名称：GITEE_TOKEN
   值：[粘贴你的 Gitee 私人令牌]
   ```

   **第二个密钥**：
   ```
   名称：LLM_API_KEY
   值：[你的 Kimi API 密钥]
   ```

   **第三个密钥**：
   ```
   名称：LLM_API_URL
   值：https://api.moonshot.cn/v1/chat/completions
   ```

   **第四个密钥**：
   ```
   名称：LLM_MODEL
   值：moonshot-v1-8k
   ```

4. **点击 "确定" 保存**

---

## 🧪 测试流程

### 方式 1: 自动触发（推荐）

```bash
# 1. 推送到 Gitee（已完成）
git push gitee test/ai-code-review

# 2. 在 Gitee 创建 PR（手动操作）
# 访问：https://gitee.com/kevin_lu/blog/pulls

# 3. 等待工作流自动运行
# 访问：https://gitee.com/kevin_lu/blog/gitee_go
```

### 方式 2: 手动触发

1. 访问：https://gitee.com/kevin_lu/blog/gitee_go/workflows
2. 找到 "AI Code Review (Gitee)"
3. 点击 "运行工作流"
4. 选择分支 `test/ai-code-review`
5. 点击 "运行"

---

## ✅ 验证配置

### 检查清单

- [ ] 已添加 `GITEE_TOKEN` Secret
- [ ] 已添加 `LLM_API_KEY` Secret
- [ ] 已添加 `LLM_API_URL` Secret
- [ ] 工作流文件存在：`.gitee/workflows/ai-code-review.yml`
- [ ] 已推送分支到 Gitee
- [ ] 已创建 PR
- [ ] 工作流开始运行

### 预期结果

工作流运行成功后，你会看到：

```
✅ AI Code Review (Gitee)
├─ ✅ Static Analysis
─ ✅ Frontend Analysis
├─ ✅ AI Deep Review
├─ ✅ Post Review Comments
└─ ✅ Auto-Fix Critical Issues
```

PR 页面会显示 AI 审查报告。

---

## 🔍 故障排查

### 问题 1: 工作流未触发

**解决方法**：
1. 检查工作流文件是否在 `.gitee/workflows/` 目录
2. 检查 Gitee Go 是否已启用
3. 手动触发工作流

### 问题 2: Secret 未找到

**错误信息**：
```
Error: Secret GITEE_TOKEN is not defined
```

**解决方法**：
1. 检查 Secret 名称是否正确（区分大小写）
2. 重新添加 Secret
3. 重新运行工作流

### 问题 3: API 调用失败

**错误信息**：
```
Error: HTTP 401 Unauthorized
```

**解决方法**：
1. 检查 GITEE_TOKEN 是否正确
2. 检查令牌权限是否足够
3. 重新生成令牌

---

## 📊 GitHub vs Gitee 对比

| 特性 | GitHub | Gitee |
|------|--------|-------|
| 访问速度 | 🐌 慢 | 🚀 快 |
| 工作流 | GitHub Actions | Gitee Go |
| Secrets | Settings → Secrets | 设置 → 密钥管理 |
| API | GitHub API | Gitee API v5 |
| 令牌 | GITHUB_TOKEN | GITEE_TOKEN |
| 免费额度 | 2000 分钟/月 | 2000 分钟/月 |

---

## 🎯 下一步

配置完成后：

1. **在 Gitee 创建 PR**
   ```
   https://gitee.com/kevin_lu/blog/pulls
   ```

2. **查看工作流运行**
   ```
   https://gitee.com/kevin_lu/blog/gitee_go
   ```

3. **查看 AI 审查报告**
   - PR 评论区
   - 行内评论

---

## 📚 参考资源

- [Gitee Go 快速开始](https://gitee.com/help/articles/406)
- [Gitee API 文档](https://gitee.com/api/v5/swagger)
- [Gitee 密钥管理](https://gitee.com/help/articles/416)
- [Kimi API 文档](https://platform.moonshot.cn/docs/api)

---

*配置时间：2026-05-30 | 适用于 Gitee Go*
