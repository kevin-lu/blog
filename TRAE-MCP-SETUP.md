# Trae IDE - GitNexus MCP 配置完成

## ✅ 配置状态

### Trae IDE MCP 配置
- **配置文件**: `~/Library/Application Support/Trae/mcp_settings.json`
- **状态**: ✅ 已创建
- **MCP 服务器**:
  - ✅ GitNexus (代码知识图谱)
  - ✅ Draw.io (图表绘制)

### 代码索引状态
- **项目**: blog
- **位置**: `/Users/luzengbiao/traeProjects/blog/blog`
- **索引目录**: `.gitnexus/`
- **符号数量**: 3,977 个
- **关系数量**: 6,157 条
- **功能集群**: 116 个
- **执行流程**: 188 个

---

## 🚀 立即开始使用

### 1. 重启 Trae IDE

关闭并重新打开 Trae IDE，MCP 服务器会自动加载。

### 2. 验证连接

在 Trae IDE 的 AI 助手中输入：
```
列出所有可用的 MCP 工具
```

或
```
GitNexus 能提供什么功能？
```

### 3. 开始使用 GitNexus

#### 代码探索
```
帮我找到处理用户登录的完整流程
这个项目的认证机制是如何工作的？
找出所有调用 UserService 的地方
```

#### 影响分析（修改前必用）
```
如果修改 authenticateUser 函数会影响哪些地方？
运行影响分析：target: "authenticateUser"
```

#### 调试追踪
```
为什么登录功能失败了？追踪执行流程
找出从 Controller 到 Database 的完整调用链
```

#### 架构理解
```
显示项目的功能集群分布
列出所有的执行流程
这个模块的依赖关系是什么？
```

---

## 📁 配置文件详情

### mcp_settings.json 内容

```json
{
  "mcpServers": {
    "gitnexus": {
      "command": "npx",
      "args": ["-y", "gitnexus", "mcp"]
    },
    "drawio": {
      "command": "npx",
      "args": ["@next-ai-drawio/mcp-server@latest"]
    }
  }
}
```

### 配置文件位置

**Trae IDE:**
```
~/Library/Application Support/Trae/mcp_settings.json
```

**Claude Desktop (也支持):**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

---

## 📊 GitNexus 提供的 MCP 工具

GitNexus MCP 服务器提供以下工具：

| 工具 | 功能 | 使用场景 |
|------|------|----------|
| `gitnexus_query` | 语义搜索 | 查找代码概念、功能 |
| `gitnexus_context` | 符号上下文 | 查看某个符号的完整上下文 |
| `gitnexus_impact` | 影响分析 | 修改前评估影响范围 |
| `gitnexus_detect_changes` | 变更检测 | 提交前检查影响 |
| `gitnexus_rename` | 智能重命名 | 安全重命名符号 |
| `gitnexus_cypher` | 图查询 | 直接查询知识图谱 |

---

## 🎯 在 Trae 中的最佳实践

### ✅ 必须遵守的规则

1. **修改代码前必须运行影响分析**
   ```
   在修改任何函数前，先询问 AI 运行 gitnexus_impact
   ```

2. **提交前必须检查影响范围**
   ```
   提交前让 AI 运行 gitnexus_detect_changes()
   ```

3. **高风险警告必须重视**
   ```
   如果影响分析返回 HIGH 或 CRITICAL，必须停止并评估
   ```

### ❌ 禁止的行为

1. ❌ 直接编辑函数而不做影响分析
2. ❌ 忽略高风险警告
3. ❌ 用查找替换重命名符号 - 使用 `gitnexus_rename`
4. ❌ 提交前不检查影响范围

---

## 🔧 CLI 命令

在终端中可以使用以下命令：

### 重新索引代码
```bash
cd /Users/luzengbiao/traeProjects/blog/blog
npx gitnexus analyze
```

### 查看索引状态
```bash
npx gitnexus status
```

### 启动本地服务（用于 Web UI）
```bash
npx gitnexus serve
```

### 生成 Wiki 文档
```bash
npx gitnexus wiki generate
```

---

## 🌐 Web UI 可视化

GitNexus 提供浏览器界面用于可视化探索代码图谱：

1. **启动本地服务**
   ```bash
   npx gitnexus serve
   ```

2. **访问 Web UI**
   - 打开浏览器：https://gitnexus.vercel.app
   - 会自动检测到本地服务
   - 可视化查看知识图谱

3. **功能**
   - 🗺️ 交互式代码图谱
   - 💬 AI 对话探索
   - 🔗 调用链可视化
   - 📦 依赖关系图

---

## 📚 项目文件说明

### `.gitnexus/` 目录
```
.gitnexus/
├── lbug          # 图数据库文件 (79MB)
├── meta.json     # 元数据信息
├── parse-cache/  # 解析缓存
└── .gitignore    # Git 忽略配置
```

### AI 助手配置文件
- **[AGENTS.md](file:///Users/luzengbiao/traeProjects/blog/blog/AGENTS.md)** - AI 助手使用规范（项目根目录）
- **[CLAUDE.md](file:///Users/luzengbiao/traeProjects/blog/blog/CLAUDE.md)** - 同上（别名）

### GitNexus 技能文件
```
.claude/skills/gitnexus/
├── gitnexus-cli/           # CLI 命令使用
├── gitnexus-debugging/     # 调试技能
├── gitnexus-exploring/     # 探索技能
├── gitnexus-guide/         # 使用指南
├── gitnexus-impact-analysis/ # 影响分析
└── gitnexus-refactoring/   # 重构技能
```

### 使用指南
- **[GITNEXUS-GUIDE.md](file:///Users/luzengbiao/traeProjects/blog/blog/GITNEXUS-GUIDE.md)** - 完整使用指南

---

## ⚠️ 故障排查

### MCP 服务器未加载

**症状**: Trae AI 助手无法使用 GitNexus 工具

**解决方案**:
1. ✅ 确认已重启 Trae IDE
2. ✅ 检查配置文件 JSON 格式是否正确
3. ✅ 查看 Trae IDE 日志
4. ✅ 验证配置文件路径正确

### 索引过时

**症状**: GitNexus 警告索引与代码不同步

**解决方案**:
```bash
cd /Users/luzengbiao/traeProjects/blog/blog
npx gitnexus analyze
```

### Node.js 版本警告

**症状**: 出现 `Unsupported engine` 警告

**说明**: GitNexus 推荐 Node.js 22+，但 Node.js 20 也可以正常运行

---

## 📋 快速参考卡片

### 常用命令
```bash
# 索引代码
npx gitnexus analyze

# 启动 Web UI 服务
npx gitnexus serve

# 查看状态
npx gitnexus status

# 生成 Wiki
npx gitnexus wiki generate
```

### 常用 AI 提示词
```
帮我找到处理 [功能] 的代码流程
修改 [函数名] 会影响哪些地方？
显示 [模块] 的依赖关系
追踪从 [A] 到 [B] 的调用链
列出所有调用 [函数] 的地方
```

---

## ⚠️ 许可说明

GitNexus 使用 **PolyForm Noncommercial License 1.0.0**

- ✅ 可用于：个人学习、研究、开源项目分析
- ❌ 不可用于：商业项目、公司开发、创业项目

如需商业使用，请联系：founders@akonlabs.com

---

## 📞 需要帮助？

- 📖 GitNexus GitHub: https://github.com/abhigyanpatwari/GitNexus
- 🌐 Web UI: https://gitnexus.vercel.app
- 📚 MCP 协议：https://modelcontextprotocol.io

---

*配置完成时间：2026-05-24*  
*项目：blog (前后端分离的博客系统)*  
*IDE: Trae IDE*
