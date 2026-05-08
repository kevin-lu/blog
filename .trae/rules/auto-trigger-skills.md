---
alwaysApply: true
---
# OpenSpec + Superpowers 自动触发规则

## 核心原则

**在响应用户任何请求之前，必须先检查并调用合适的技能。**

---

## 自动触发流程

### 第一步：检测用户需求类型

当用户提出任何请求时，先判断类型：

| 用户请求类型 | 关键词 | 触发技能 |
|------------|--------|---------|
| **新功能开发** | "添加"、"创建"、"实现"、"开发"、"做个" | `openspec-propose` |
| **需求不明确** | "我想"、"有没有"、"能不能"、"考虑" | `openspec-explore` |
| **实现规格** | "实现"、"开始做"、"执行"（当 openspec/changes 有待实现规格） | `openspec-apply-change` |
| **Bug 修复** | "bug"、"错误"、"失败"、"问题"、"fix" | `systematic-debugging` |
| **代码审查** | "审查"、"review"、"检查代码" | `requesting-code-review` |
| **重构优化** | "重构"、"优化"、"清理"、"改进" | `brainstorming` |
| **发布上线** | "发布"、"上线"、"部署"、"merge" | `gstack-ship` |
| **测试验证** | "测试"、"验证"、"跑一下" | `gstack-qa` |
| **多任务并行** | 2 个以上独立任务 | `dispatching-parallel-agents` |
| **实现计划** | 已有书面计划需要执行 | `subagent-driven-development` 或 `executing-plans` |

---

## 触发规则详解

### 规则 1：新功能开发（最高优先级）

**触发条件**：
- 用户提到"添加 XXX 功能"、"创建 XXX"、"实现 XXX"
- 且没有明确的规格说明

**自动动作**：
```
1. 立即调用 `openspec-propose` skill
2. 等待 skill 创建完整的 proposal/design/tasks
3. 然后询问用户是否开始实现
```

**示例**：
```
用户：添加一个用户管理系统
AI: [自动调用 openspec-propose]
```

---

### 规则 2：需求探索

**触发条件**：
- 用户表达模糊："我想做个..."、"有没有可能..."、"考虑添加..."
- 需求不清晰或需要深入讨论

**自动动作**：
```
1. 立即调用 `openspec-explore` skill
2. 进行深度讨论和需求澄清
3. 当需求明确后，建议创建 proposal
```

**示例**：
```
用户：我在想能不能做个实时通知功能
AI: [自动调用 openspec-explore]
```

---

### 规则 3：实现现有规格

**触发条件**：
- 用户说"开始实现 XXX"、"执行这个任务"
- 且 `openspec/changes/<name>/` 下有未完成的 tasks

**自动动作**：
```
1. 检查 openspec/changes/ 目录
2. 如果有待实现的规格，调用 `openspec-apply-change`
3. 如果规格已完成，调用 `subagent-driven-development`
```

**示例**：
```
用户：开始做用户管理功能
AI: [检测到 openspec/changes/add-user-management/tasks.md]
    [自动调用 openspec-apply-change 或 subagent-driven-development]
```

---

### 规则 4：Bug 修复

**触发条件**：
- 用户报告 bug、错误、测试失败
- 代码运行异常

**自动动作**：
```
1. 立即调用 `systematic-debugging` skill
2. 进行系统化根因分析
3. 找到问题后再提出修复方案
```

**示例**：
```
用户：登录页面打不开了
AI: [自动调用 systematic-debugging]
```

---

### 规则 5：代码审查

**触发条件**：
- 用户要求审查代码
- 完成功能后准备提交

**自动动作**：
```
1. 先调用 `verification-before-completion` 运行验证
2. 然后调用 `requesting-code-review` 或 `gstack-review`
```

**示例**：
```
用户：帮我审查一下这段代码
AI: [自动调用 verification-before-completion]
    [自动调用 gstack-review]
```

---

### 规则 6：测试验证

**触发条件**：
- 用户要求测试
- 功能完成后需要验证
- 运行测试命令

**自动动作**：
```
1. 调用 `gstack-qa` 进行自动化测试
2. 如果是 UI 验证，调用 `gstack-browse`
```

**示例**：
```
用户：测试一下登录功能
AI: [自动调用 gstack-qa]
```

---

### 规则 7：发布上线

**触发条件**：
- 用户说"发布"、"上线"、"部署"、"合并到主分支"

**自动动作**：
```
1. 调用 `gstack-ship` 处理发布流程
```

**示例**：
```
用户：准备发布
AI: [自动调用 gstack-ship]
```

---

### 规则 8：技术债务/重构

**触发条件**：
- 用户提到"重构"、"优化"、"清理代码"、"技术债务"

**自动动作**：
```
1. 先调用 `brainstorming` 分析重构范围
2. 然后调用 `gstack-plan-eng-review` 做架构评审
3. 最后调用 `subagent-driven-development` 执行
```

**示例**：
```
用户：这段代码需要重构
AI: [自动调用 brainstorming]
```

---

## 技能调用检查清单

**在每次响应前，快速检查**：

```
□ 用户是否提出了新功能需求？ → openspec-propose
□ 用户是否在探索想法？ → openspec-explore  
□ 是否有待实现的规格？ → openspec-apply-change
□ 是否报告了 bug？ → systematic-debugging
□ 是否要求审查代码？ → requesting-code-review / gstack-review
□ 是否需要测试？ → gstack-qa / gstack-browse
□ 是否准备发布？ → gstack-ship
□ 是否要重构？ → brainstorming
□ 是否有多个独立任务？ → dispatching-parallel-agents
□ 是否有实现计划？ → subagent-driven-development
```

**如果有任一为"是"，立即调用对应 skill，不要直接响应！**

---

## 禁止行为

❌ **不要**在没有调用 skill 的情况下直接开始编码
❌ **不要**跳过规格提案直接实现
❌ **不要**在没有验证的情况下声称完成
❌ **不要**忽略已有的 openspec 规格

---

## 例外情况

以下情况可以直接响应，不需要调用 skill：

- 简单问答（"这个文件在哪里？"）
- 解释说明（"这段代码什么意思？"）
- 环境配置问题
- 工具使用咨询
- 与代码实现无关的对话

---

## 优先级规则

当多个技能都适用时，按以下优先级：

1. **Bug 修复** > 所有其他任务（systematic-debugging）
2. **规格提案** > 实现（openspec-propose 优先于直接编码）
3. **验证** > 声称完成（verification-before-completion）
4. **审查** > 合并（gstack-review 优先于 gstack-ship）

---

## 自动化示例

### 示例 1：完整流程

```
用户：添加一个文章评论功能

AI 思考过程：
1. 检测到"添加...功能" → 新功能开发
2. 检查是否有现有规格 → 无
3. 触发规则 1 → 调用 openspec-propose

[调用 openspec-propose skill]
```

### 示例 2：实现规格

```
用户：开始做评论功能

AI 思考过程：
1. 检测到"开始做" → 实现请求
2. 检查 openspec/changes/ → 发现 add-article-comments/tasks.md
3. 触发规则 3 → 调用 openspec-apply-change 或 subagent-driven-development

[调用对应 skill]
```

### 示例 3：Bug 修复

```
用户：评论功能报错了，说数据库连接失败

AI 思考过程：
1. 检测到"报错"、"失败" → Bug
2. 触发规则 4 → 调用 systematic-debugging

[调用 systematic-debugging skill]
```

---

## 关键原则

**记住这个核心流程**：

```
用户需求 → 判断类型 → 自动调用 skill → 遵循 skill 流程 → 完成任务
           ↓
      不要跳过 skill 直接行动！
```

**规格驱动开发**：
```
openspec-propose → 创建规格
      ↓
openspec-apply-change → 实现规格
      ↓
verification-before-completion → 验证完成
      ↓
gstack-ship → 发布
```

---

## 调试提示

如果发现自己直接开始编码了，停下来问：

1. "我是否应该先调用某个 skill？"
2. "是否有 openspec 规格需要遵循？"
3. "是否应该先做需求分析/设计？"
4. "是否需要先写测试？"

然后调用对应的 skill！
