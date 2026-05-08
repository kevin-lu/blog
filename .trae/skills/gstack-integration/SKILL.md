---
name: gstack-integration
description: GStack 集成——整合 7 个 GStack 核心 skills 到 Trae 环境。根据场景自动选择合适的 GStack skill 进行处理。
---

## 概述

GStack 是一套认知模式切换工具，把 AI 变成虚拟工程团队。本 skill 整合以下核心能力：

| Skill | 角色 | 用途 |
|-------|------|------|
| gstack-office-hours | YC 导师 | 产品方向六问 |
| gstack-plan-ceo-review | CEO | 10 星产品审查 |
| gstack-plan-eng-review | 技术负责人 | 架构评审 |
| gstack-review | 高级工程师 | 生产级 bug 审查 |
| gstack-investigate | 调试工程师 | 根因分析 |
| gstack-qa | QA Lead | 自动化测试 |
| gstack-ship | 发布工程师 | 自动化发布 |
| gstack-browse | 浏览器自动化 | 视觉验证 |

## 场景路由

根据用户输入，自动匹配对应的 skill：

### 场景 1: 产品方向不清晰

**触发条件**：用户提出新想法、新功能、新项目

**调用**：
1. gstack-office-hours - 回答六个关键问题
2. gstack-plan-ceo-review - 验证 10 星方案

### 场景 2: 技术架构设计

**触发条件**：产品方向已确认，需要技术方案

**调用**：gstack-plan-eng-review - 架构评审 + 图表

### 场景 3: 代码审查

**触发条件**：用户要求审查代码、审查 PR、审查变更

**调用**：
1. gstack-review - 寻找生产级 bug
2. (可选) gstack-browse - UI 审查

### 场景 4: Bug 调试

**触发条件**：用户报告 bug、测试失败、系统异常

**调用**：
1. gstack-investigate - 根因分析
2. gstack-review - 修复后审查
3. gstack-qa - 验证修复

### 场景 5: 测试验证

**触发条件**：代码变更后需要验证

**调用**：
1. gstack-qa - 自动化测试
2. gstack-browse - 视觉验证

### 场景 6: 发布上线

**触发条件**：代码完成，准备发布

**调用**：
1. gstack-review - 最终审查
2. gstack-ship - 同步、测试、推送、创建 PR

## 完整工作流

```
[新功能]
    ↓
gstack-office-hours (产品六问)
    ↓
gstack-plan-ceo-review (CEO 审查)
    ↓
gstack-plan-eng-review (架构评审)
    ↓
[实现]
    ↓
gstack-review (代码审查)
    ↓
gstack-investigate (如有 bug)
    ↓
gstack-qa (测试验证)
    ↓
gstack-browse (视觉验证)
    ↓
gstack-ship (发布)
```

## 使用方式

根据需求选择合适的处理方式：

| 你说... | 自动处理 |
|---------|---------|
| "帮我看看这个想法" | gstack-office-hours |
| "这个功能方向对不对" | gstack-plan-ceo-review |
| "帮我看下技术方案" | gstack-plan-eng-review |
| "代码审一下" | gstack-review |
| "有个 bug" | gstack-investigate |
| "跑下测试" | gstack-qa |
| "看看 UI 对不对" | gstack-browse |
| "可以发布了" | gstack-ship |

## 输出格式

```markdown
## GStack 处理报告

### 场景识别
- 类型: [产品方向/技术设计/代码审查/调试/测试/发布]
- 调用的 Skills: [列表]

### 处理结果
[详细的处理报告]

### 下一步
[建议的后续操作]
```
