# 使用 Kimi（月之暗面）进行代码审查

本文档介绍如何配置使用 Kimi AI 进行代码审查。

---

## 🌙 Kimi 介绍

Kimi 是月之暗面（Moonshot AI）开发的大语言模型，支持：

- ✅ OpenAI 兼容的 API 格式
- ✅ 长上下文支持（最高 128K）
- ✅ 优秀的代码理解能力
- ✅ 相对较低的价格

---

## 📋 配置步骤

### 步骤 1: 注册 Kimi 开放平台

1. 访问：https://platform.moonshot.cn/
2. 点击 **注册**（支持手机号/邮箱注册）
3. 完成实名认证（需要，根据中国法规）
4. 登录控制台

---

### 步骤 2: 获取 API Key

1. 登录后进入 **控制台**
2. 左侧菜单选择 **API Keys**
3. 点击 **创建 API Key**
4. 输入名称（如：`github-code-review`）
5. 复制并保存密钥

**密钥格式**：
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **重要**：密钥只显示一次，请立即保存！

---

### 步骤 3: 配置 GitHub Secrets

打开 GitHub 仓库设置：

```
Settings → Secrets and variables → Actions → New repository secret
```

添加以下 Secrets：

| Secret 名称 | 值 | 必填 |
|------------|---|------|
| `LLM_API_KEY` | 你的 Kimi API 密钥 | ✅ |
| `LLM_API_URL` | `https://api.moonshot.cn/v1/chat/completions` | ✅ |
| `LLM_MODEL` | `moonshot-v1-8k` | ❌（可选） |

**截图说明**：

```
┌─────────────────────────────────────────────────────────┐
│ New repository secret                                    │
├─────────────────────────────────────────────────────────┤
│ Name:  LLM_API_KEY                                      │
│ Value: sk-moonshot-xxxxxxxxxxxxxxxx                     │
│                                                         │
│ [Add secret]                                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Kimi 模型选择

### 可用模型

| 模型 | 上下文 | 价格 | 适用场景 |
|------|--------|------|---------|
| `moonshot-v1-8k` | 8K tokens | ¥0.012/1K tokens | 小型 PR、快速审查 |
| `moonshot-v1-32k` | 32K tokens | ¥0.024/1K tokens | 中型 PR、复杂审查 |
| `moonshot-v1-128k` | 128K tokens | ¥0.060/1K tokens | 大型 PR、完整项目审查 |

### 推荐配置

**日常使用**：
```yaml
LLM_MODEL: moonshot-v1-8k
```

**大型 PR**：
```yaml
LLM_MODEL: moonshot-v1-32k
```

---

## 💰 费用说明

### 计费方式

- 按 tokens 计费（输入 + 输出）
- 1000 tokens ≈ 750 个英文单词 ≈ 500 个汉字

### 价格示例

**审查一个中等 PR**（约 5000 行代码变更）：

```
输入：约 10K tokens
输出：约 2K tokens
总计：12K tokens

费用：12 × ¥0.024 = ¥0.288（32k 模型）
```

**每月预算估算**：

| 使用频率 | 预估费用 |
|---------|---------|
| 每天 5 个 PR | ¥40-60/月 |
| 每天 10 个 PR | ¥80-120/月 |
| 每天 20 个 PR | ¥160-240/月 |

### 充值

1. 控制台 → **充值**
2. 支持支付宝/微信支付
3. 建议首次充值 ¥50-100 测试

---

## 🔧 代码修改说明

已自动修改以下文件以支持 Kimi：

### 1. `.github/scripts/ai_code_review.py`

```python
# 修改前
self.llm_api_url = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
self.llm_model = "gpt-4"

# 修改后
self.llm_api_url = os.getenv("LLM_API_URL", "https://api.moonshot.cn/v1/chat/completions")
self.llm_model = os.getenv("LLM_MODEL", "moonshot-v1-8k")
```

---

## 🧪 测试配置

### 创建测试工作流

```yaml
# .github/workflows/test-kimi.yml
name: Test Kimi Configuration

on:
  workflow_dispatch:

jobs:
  test-kimi:
    runs-on: ubuntu-latest
    steps:
      - name: Test Kimi API
        env:
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
          LLM_API_URL: ${{ secrets.LLM_API_URL }}
          LLM_MODEL: ${{ secrets.LLM_MODEL }}
        run: |
          echo "Testing Kimi API..."
          
          curl -X POST "$LLM_API_URL" \
            -H "Authorization: Bearer $LLM_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{
              \"model\": \"$LLM_MODEL\",
              \"messages\": [
                {
                  \"role\": \"user\",
                  \"content\": \"Hello Kimi!\"
                }
              ]
            }" \
            -w "\nHTTP Status: %{http_code}\n"
```

### 运行测试

```
Actions → Test Kimi Configuration → Run workflow
```

**预期结果**：
```
✅ HTTP Status: 200
{"choices":[{"message":{"content":"Hello! I'm Kimi..."}}]}
```

---

## 📊 Kimi vs OpenAI 对比

| 特性 | Kimi | OpenAI GPT-4 |
|------|------|-------------|
| API 兼容性 | ✅ OpenAI 兼容 | ✅ 原生 |
| 上下文长度 | 8K-128K | 8K-128K |
| 代码审查能力 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 价格 | ¥0.024/1K tokens | $0.03/1K tokens |
| 网络延迟 | 国内较快 | 需要代理 |
| 支付 | 人民币 | 美元信用卡 |
| 注册难度 | 简单（国内手机号） | 较复杂 |

---

## 🔍 故障排查

### 问题 1: API 调用失败

**错误**：`401 Unauthorized`

**原因**：API Key 无效

**解决**：
1. 检查 Secret 是否正确
2. 确认 API Key 未过期
3. 确认账户有余额

### 问题 2: 模型不存在

**错误**：`400 Bad Request - Model not found`

**解决**：
```yaml
# 检查 LLM_MODEL Secret
LLM_MODEL: moonshot-v1-8k  # 确保模型名称正确
```

### 问题 3: 响应超时

**错误**：`Timeout`

**解决**：
```python
# .github/scripts/ai_code_review.py
response = requests.post(
    self.llm_api_url,
    headers=headers,
    json=payload,
    timeout=120  # 增加超时时间
)
```

---

## 📈 监控使用情况

### 查看用量

1. 登录 Kimi 控制台
2. 进入 **用量统计**
3. 查看每日/每月使用情况

### 设置预算告警

1. 控制台 → **账户设置** → **预算告警**
2. 设置月度预算上限
3. 达到阈值时邮件通知

---

## 🎯 最佳实践

### 1. 优化 Prompt

减少 token 使用：

```python
# 精简 prompt，去除冗余
prompt = f"""审查以下代码变更，重点关注：
1. N+1 查询
2. 竞态条件
3. 信任边界

```diff
{diff_content[:30000]}  # 限制长度
```
"""
```

### 2. 选择合适的模型

- 小 PR（<100 行）：`moonshot-v1-8k`
- 中 PR（100-500 行）：`moonshot-v1-32k`
- 大 PR（>500 行）：`moonshot-v1-128k`

### 3. 缓存结果

避免重复审查相同代码：

```python
# 使用 GitHub Actions cache
- uses: actions/cache@v3
  with:
    path: /tmp/ai-review-cache
    key: ai-review-${{ github.sha }}
```

---

## 📞 获取帮助

### Kimi 官方支持

- 文档：https://platform.moonshot.cn/docs
- API 参考：https://platform.moonshot.cn/docs/api
- 技术支持：support@moonshot.cn

### 社区资源

- GitHub Issues: https://github.com/MoonshotAI
- 开发者社区：https://discord.gg/moonshot

---

## ✅ 配置检查清单

配置 Kimi 后，检查以下项目：

- [ ] 已注册 Kimi 开放平台账户
- [ ] 已完成实名认证
- [ ] 已创建 API Key 并保存
- [ ] 已充值账户余额
- [ ] 已在 GitHub 添加 `LLM_API_KEY` Secret
- [ ] 已在 GitHub 添加 `LLM_API_URL` Secret
- [ ] 已在 GitHub 添加 `LLM_MODEL` Secret（可选）
- [ ] 已运行测试工作流验证
- [ ] 已设置预算告警

---

*最后更新：2026-05-29 | 适用于 Kimi moonshot-v1 系列模型*
