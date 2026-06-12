# GitNexus 使用指南

## ✅ 安装完成状态

### 已完成的配置

1. **代码知识图谱已生成**
   - 索引位置：`.gitnexus/`
   - 符号数量：3,977 个
   - 关系数量：6,157 条
   - 功能集群：116 个
   - 执行流程：188 个

2. **MCP 服务器已配置**
   - 配置文件：`~/Library/Application Support/Claude/claude_desktop_config.json`
   - GitNexus MCP：✅ 已配置
   - Draw.io MCP：✅ 已配置

3. **AI 助手技能文件**
   - 位置：`.claude/skills/gitnexus/`
   - 包含：探索、调试、影响分析、重构等技能

---

## 🚀 如何使用

### 1. 重启 IDE

配置完成后，需要重启 IDE 应用以加载新的 MCP 服务器。

#### Trae IDE
- 重启 Trae IDE
- MCP 配置会自动加载
- 配置位置：`~/Library/Application Support/Trae/mcp_settings.json`

#### Claude Desktop
- 重启 Claude Desktop
- 配置位置：`~/Library/Application Support/Claude/claude_desktop_config.json`

### 2. 验证 MCP 连接

在 Trae IDE 中，可以询问：
- "列出所有可用的 MCP 工具"
- "GitNexus 能提供什么功能？"
- "使用 GitNexus 工具查看项目架构"

### 3. 常用功能

#### 🔍 代码探索
```
帮我找到处理用户登录的代码流程
这个项目的认证机制是如何工作的？
找出所有调用 UserService 的地方
```

#### ⚠️ 影响分析（修改前必用）
```
如果修改这个函数会影响哪些地方？
运行影响分析：target: "authenticateUser"
```

#### 🐛 调试追踪
```
为什么登录功能失败了？追踪执行流程
找出从 Controller 到 Database 的完整调用链
```

#### 🔧 重构辅助
```
使用 gitnexus_rename 重命名这个函数
帮我提取这个方法到独立的类
```

#### 📊 架构理解
```
显示项目的功能集群分布
列出所有的执行流程
这个模块的依赖关系是什么？
```

---

## 📁 生成的文件说明

### `.gitnexus/` 目录
```
.gitnexus/
├── lbug          # 图数据库文件 (79MB)
├── meta.json     # 元数据信息
├── parse-cache/  # 解析缓存
└── .gitignore    # Git 忽略配置
```

### `CLAUDE.md` / `AGENTS.md`
- 包含 GitNexus 使用规范
- 定义了"必须做"和"禁止做"的规则
- 提供快速参考指南

### `.claude/skills/gitnexus/` 技能目录
```
gitnexus/
├── gitnexus-cli/           # CLI 命令使用
├── gitnexus-debugging/     # 调试技能
├── gitnexus-exploring/     # 探索技能
├── gitnexus-guide/         # 使用指南
├── gitnexus-impact-analysis/ # 影响分析
└── gitnexus-refactoring/   # 重构技能
```

---

## 🛠️ CLI 命令参考

### 重新索引代码
```bash
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

### 清理缓存
```bash
npx gitnexus clean
```

---

## 🎯 最佳实践

### ✅ 必须遵守的规则

1. **修改代码前必须运行影响分析**
   ```
   在修改任何函数前，先运行 gitnexus_impact
   ```

2. **提交前必须检查影响范围**
   ```
   提交前运行 gitnexus_detect_changes()
   ```

3. **高风险警告必须重视**
   ```
   如果影响分析返回 HIGH 或 CRITICAL，必须警告用户
   ```

### ❌ 禁止的行为

1. **不要直接编辑函数而不做影响分析**
2. **不要忽略高风险警告**
3. **不要用查找替换重命名符号** - 使用 `gitnexus_rename`
4. **不要提交前不检查影响范围**

---

## 🔗 Web UI 访问

GitNexus 提供浏览器界面用于可视化探索：

1. **启动本地服务**
   ```bash
   npx gitnexus serve
   ```

2. **访问 Web UI**
   - 打开浏览器访问：https://gitnexus.vercel.app
   - 会自动检测到本地服务
   - 可以可视化查看知识图谱

3. **功能**
   - 交互式代码图谱
   - AI 对话探索
   - 调用链可视化
   - 依赖关系图

---

## ⚙️ MCP 配置说明

### 当前配置位置

**Trae IDE:**
```
~/Library/Application Support/Trae/mcp_settings.json
```

**Claude Desktop:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### 配置内容
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

### 如何添加其他 MCP 服务器

在 `mcpServers` 对象中添加新的服务器配置即可。

---

## 📊 项目代码统计

基于 GitNexus 分析结果：

| 指标 | 数量 |
|------|------|
| 代码符号 | 3,977 |
| 关系边 | 6,157 |
| 功能集群 | 116 |
| 执行流程 | 188 |
| 索引时间 | 27.9 秒 |

---

## 🆘 故障排查

### MCP 服务器未加载

**症状**: Claude Desktop 中无法使用 GitNexus 工具

**解决方案**:
1. 确认已重启 Claude Desktop
2. 检查配置文件 JSON 格式是否正确
3. 查看 Claude Desktop 日志

### 索引过时

**症状**: GitNexus 警告索引与代码不同步

**解决方案**:
```bash
npx gitnexus analyze
```

### Node.js 版本警告

**症状**: 出现 `Unsupported engine` 警告

**说明**: GitNexus 推荐 Node.js 22+，但 Node.js 20 也可以运行

---

## 📚 相关资源

- GitNexus GitHub: https://github.com/abhigyanpatwari/GitNexus
- GitNexus Web UI: https://gitnexus.vercel.app
- MCP 协议文档：https://modelcontextprotocol.io

---

## ⚠️ 许可说明

GitNexus 使用 **PolyForm Noncommercial License 1.0.0**

- ✅ 可用于：个人学习、研究、开源项目分析
- ❌ 不可用于：商业项目、公司开发、创业项目

如需商业使用，请联系：founders@akonlabs.com

---

*最后更新：2026-05-24*
*项目：blog (前后端分离的博客系统)*
