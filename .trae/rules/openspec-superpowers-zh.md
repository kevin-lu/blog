---
alwaysApply: true
---
# OpenSpec + Superpowers + GStack 三工具集成规则

本规则整合三大 AI 编程工具链，实现规格驱动 → 专家角色 → 验证闭环的完整开发流程。

## 核心理念

| 工具 | 职责 | 阶段 |
|------|------|------|
| **OpenSpec** | 规格管理 - 产出 proposal/specs/design/tasks | 规划阶段 |
| **GStack** | 认知模式切换 - 9+ 专业角色专家 | 执行阶段 |
| **Superpowers** | 流程控制 - 子代理 + TDD + 验证 | 协调阶段 |

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           完整开发流程                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│   │  规划    │───▶│  设计    │───▶│  实现    │───▶│  发布    │      │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘      │
│        │               │               │               │                │
│        ▼               ▼               ▼               ▼                │
│   OpenSpec         GStack          Superpowers       GStack            │
│   proposal      plan-ceo-review   subagent-dev     ship               │
│   specs         plan-eng-review   test-driven      land-and-deploy    │
│   design        design-review     verification     canary             │
│   tasks         qa                before-completion                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## GStack 核心技能映射

> **注意**：以下是 GStack 原始命令。在 Trae 环境中，请使用对应的本地 skills：
> - 使用 **gstack-plan-ceo-review** 代替 /plan-ceo-review
> - 使用 **gstack-plan-eng-review** 代替 /plan-eng-review
> - 使用 **gstack-review** 代替 /review
> - 使用 **gstack-qa** 代替 /qa
> - 使用 **gstack-ship** 代替 /ship
> - 使用 **gstack-browse** 代替 /browse
> - 使用 **gstack-investigate** 代替 /investigate
> - 使用 **gstack-office-hours** 代替 /office-hours

### 规划阶段 (Plan)

| GStack Skill | 用途 | 对接 OpenSpec | Trae Skill |
|--------------|------|---------------|------------|
| /office-hours | 产品方向六问，重新定义问题 | proposal 审查 | gstack-office-hours |
| /plan-ceo-review | 寻找 10 星产品，扩展/收缩 scope | proposal 验证 | gstack-plan-ceo-review |
| /plan-eng-review | 架构评审，生成技术设计图 | specs → design | gstack-plan-eng-review |
| /plan-design-review | 设计评审，交互/视觉评分 | design 审查 |
| /plan-devex-review | DX 评审，TTHW 测量 | 开发体验优化 |

### 执行阶段 (Build)

| GStack Skill | 用途 | 对接 Superpowers | Trae Skill |
|--------------|------|------------------|-------------|
| /review | 代码审查，找生产级 bug | requesting-code-review | gstack-review |
| /investigate | 系统调试，根因分析 | systematic-debugging | gstack-investigate |
| /design-consultation | 创建设计系统 | (可选) | - |
| /design-shotgun | 设计方案探索 | (可选) | - |
| /design-html | 生成高质量 HTML | (可选) | - |

### 测试阶段 (Test)

| GStack Skill | 用途 | 触发时机 | Trae Skill |
|--------------|------|---------|-------------|
| /qa | 自动化测试，找 bug，修复，重新验证 | implementation 后 | gstack-qa |
| /qa-only | 只报告 bug，不修复 | 代码审查时 | gstack-qa |
| /browse | 浏览器自动化，视觉验证 | UI 实现后 | gstack-browse |
| /benchmark | 性能基准测试 | 优化前后对比 | - |

### 发布阶段 (Ship)

| GStack Skill | 用途 | Trae Skill |
|--------------|------|------------|
| /ship | 同步、测试、推送、开 PR | gstack-ship |
| /land-and-deploy | 合并、等待 CI、部署、生产验证 | gstack-ship |
| /canary | 发布后监控，错误/性能回归检测 | - |
| /cso | 安全审计，OWASP Top 10 | - |

---

## 自动触发规则

### 场景 1：全新功能开发

**触发条件**：用户提出新功能需求（"添加 XXX 功能"）

**完整流程**：
```
┌──────────────────────────────────────────────────────────────────┐
│  1. OpenSpec 产出规格                                            │
│     └── /propose → openspec/changes/                            │
│           ↓                                                      │
│  2. GStack 产品方向审查 (/plan-ceo-review)                       │
│     └── 验证 proposal 是否是 10 星方案                            │
│           ↓                                                      │
│  3. GStack 架构评审 (/plan-eng-review)                           │
│     └── 生成技术设计 → openspec/specs/design/                   │
│           ↓                                                      │
│  4. Superpowers 实现                                             │
│     └── subagent-driven-development + test-driven-development   │
│           ↓                                                      │
│  5. GStack 验证                                                  │
│     └── /qa + /browse (UI) 或 /review (代码)                     │
│           ↓                                                      │
│  6. GStack 发布                                                  │
│     └── /ship → /land-and-deploy → /canary                      │
└──────────────────────────────────────────────────────────────────┘
```

### 场景 2：现有规格实现

**触发条件**：检测到 `openspec/specs/` 有未完成规格

**流程**：
```
writing-plans → subagent-driven-development → verification-before-completion
     ↓                        ↓                           ↓
plan-eng-review              /review                   /qa + /ship
```

### 场景 3：Bug 修复

**触发条件**：报告 bug 或测试失败

**流程**：
```
systematic-debugging → /investigate → test-driven-development → /qa
```

### 场景 4：代码审查

**触发条件**：用户要求审查代码

**流程**：
```
verification-before-completion → /review (GStack) → requesting-code-review
```

### 场景 5：技术债务/重构

**触发条件**：用户提到"重构"、"优化"、"清理"

**流程**：
```
brainstorming → plan-eng-review → subagent-driven-development → /qa + /benchmark
```

### 场景 6：发布上线

**触发条件**：功能完成，准备发布

**流程**：
```
/ship → /land-and-deploy → /canary → /health
```

---

## 技能调用优先级

当多个工具/技能可用时，按以下优先级：

1. **产品方向** → /plan-ceo-review (GStack) → 验证 proposal
2. **技术设计** → /plan-eng-review (GStack) → 产出 design
3. **实现执行** → subagent-driven-development (Superpowers)
4. **代码质量** → /review (GStack) → verification-before-completion
5. **测试验证** → /qa (GStack) → /browse (UI 验证)
6. **发布部署** → /ship (GStack) → /land-and-deploy → /canary

---

## 文件结构约定

```
项目根目录/
├── openspec/                    # OpenSpec 规格
│   ├── specs/                   # 主规格 (Source of Truth)
│   │   ├── design/              # 技术设计
│   │   └── tasks/               # 任务列表
│   └── changes/                 # 变更提案
│       └── archive/
├── .claude/
│   └── skills/
│       ├── gstack/              # GStack 技能 (如果项目安装)
│       └── superpowers/         # Superpowers 技能
└── .trae/
    └── skills/                  # 本地 skills
```

---

## 快速命令参考

| 需求 | 推荐技能组合 |
|------|-------------|
| 新功能从 0 到 1 | OpenSpec /propose → /plan-ceo-review → /plan-eng-review → subagent-dev → /qa → /ship |
| 实现现有规格 | writing-plans → subagent-dev → verification-before-completion |
| Bug 修复 | systematic-debugging → /investigate → test-driven → /qa |
| 代码审查 | /review → verification-before-completion |
| UI/视觉验证 | /browse → /design-review |
| 性能优化 | /benchmark → subagent-dev → /benchmark 对比 |
| 安全审计 | /cso → verification-before-completion |
| 发布上线 | /ship → /land-and-deploy → /canary |

---

## 关键原则

1. **规划阶段 GStack 优先** - 产品方向用 /plan-ceo-review，架构用 /plan-eng-review
2. **实现阶段 Superpowers 优先** - 用 subagent-driven-development + TDD
3. **验证阶段 GStack 优先** - 用 /qa、/review、/browse 进行全面验证
4. **发布阶段 GStack 优先** - 用 /ship、/canary 实现自动化发布
5. **规格即契约** - 实现必须严格遵循 openspec/specs/ 中的规格
