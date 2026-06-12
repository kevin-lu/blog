# ✅ Blog 后端服务已启动

> 服务运行状态和访问信息

---

## 🎉 启动成功

**启动时间**: 2026-05-23  
**服务地址**: Flask Application  
**运行状态**: ✅ 正常运行中

---

## 🌐 访问地址

### 本地访问
```
http://127.0.0.1:5001
```

### 局域网访问
```
http://192.168.31.66:5001
```

---

## 📋 API 端点

### 基础信息
- **Swagger UI**: `http://localhost:5001/api/v1/docs`
- **OpenAPI JSON**: `http://localhost:5001/api/v1/openapi.json`

### 核心接口

#### 文章相关
```
GET  /api/v1/articles              # 获取文章列表
GET  /api/v1/articles/:slug        # 获取文章详情
POST /api/v1/articles              # 创建文章
PUT  /api/v1/articles/:slug        # 更新文章
DELETE /api/v1/articles/:slug      # 删除文章
POST /api/v1/articles/:id/like     # 点赞文章
```

#### 评论相关
```
GET  /api/v1/comments              # 获取评论列表
POST /api/v1/comments              # 创建评论
PUT  /api/v1/comments/:id/approve  # 审核评论
DELETE /api/v1/comments/:id        # 删除评论
```

#### 认证相关
```
POST /api/v1/auth/login            # 管理员登录
POST /api/v1/auth/logout           # 登出
POST /api/v1/auth/refresh          # 刷新令牌
```

#### 分类和标签
```
GET  /api/v1/categories            # 获取分类列表
POST /api/v1/categories            # 创建分类
DELETE /api/v1/categories/:id      # 删除分类

GET  /api/v1/tags                  # 获取标签列表
POST /api/v1/tags                  # 创建标签
DELETE /api/v1/tags/:id            # 删除标签
```

#### 其他
```
GET  /api/v1/settings              # 获取站点设置
PUT  /api/v1/settings              # 更新设置
POST /api/v1/upload                # 上传图片
POST /api/v1/ai-chat               # AI 聊天
```

---

## 🧪 快速测试

### 测试 1: 获取文章列表

```bash
curl http://localhost:5001/api/v1/articles
```

**预期响应**:
```json
{
  "articles": [...],
  "total": 10,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

---

### 测试 2: 获取站点设置

```bash
curl http://localhost:5001/api/v1/settings
```

**预期响应**:
```json
{
  "site_name": "我的博客",
  "site_description": "...",
  ...
}
```

---

### 测试 3: 管理员登录

```bash
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

**预期响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

---

## 🚀 用于性能压测

### MCP 压测配置

现在后端已启动，可以在 Trae IDE 中进行压测：

**在 Trae IDE 中输入**:
```
帮我生成一个压测脚本，测试 GET http://localhost:5001/api/v1/articles 接口
并发用户 100，压测 5 分钟
```

### 压测接口列表

**推荐压测的接口**:

| 接口 | 方法 | 说明 | 建议并发数 |
|------|------|------|-----------|
| `/api/v1/articles` | GET | 文章列表 | 100-200 |
| `/api/v1/articles/:slug` | GET | 文章详情 | 150-300 |
| `/api/v1/articles/:id/like` | POST | 点赞文章 | 30-50 |
| `/api/v1/comments` | GET | 获取评论 | 100-200 |
| `/api/v1/comments` | POST | 创建评论 | 20-40 |
| `/api/v1/auth/login` | POST | 管理员登录 | 5-10 |

---

## 📊 服务信息

### 运行环境
- **Python**: 3.7.3
- **Flask**: 开发服务器
- **模式**: production (debug=False)
- **端口**: 5001

### 数据库配置
查看 `.env` 文件中的 `DATABASE_URL` 配置

### 日志输出
服务日志会直接输出到终端

---

## ⚠️ 注意事项

### 1. 服务停止

需要停止服务时，在终端按 `Ctrl+C`

### 2. 服务重启

如果修改了代码或配置，需要重启服务：
```bash
# 先停止（Ctrl+C）
# 然后重新启动
python3 run.py
```

### 3. 端口占用

如果端口 5001 被占用，可以修改 `run.py` 中的端口号：
```python
app.run(host='0.0.0.0', port=5001, debug=False)
# 改为其他端口，如 5002
```

### 4. 生产环境

当前使用的是 Flask 开发服务器，不适合生产环境。
生产环境应使用 Gunicorn 或 uWSGI 等 WSGI 服务器。

---

## 🔧 故障排查

### 问题 1: 数据库连接失败

**检查**:
```bash
# 查看 .env 配置
cat .env | grep DATABASE_URL

# 测试数据库连接
python3 scripts/check_db.py
```

### 问题 2: 接口返回 404

**检查**:
1. 确认接口路径正确
2. 确认 HTTP 方法正确（GET/POST/PUT/DELETE）
3. 查看服务日志获取详细错误信息

### 问题 3: 认证失败

**解决**:
1. 确认已先登录获取 token
2. 确认 token 格式正确：`Authorization: Bearer <token>`
3. 确认 token 未过期

---

## 📚 相关文档

- [后端 README](./README.md)
- [快速启动指南](./scripts/QUICK_START.md)
- [API 文档](http://localhost:5001/api/v1/docs)
- [MCP 压测配置](../mcp-servers/CONFIGURATION-COMPLETE.md)

---

## ✅ 下一步

1. **测试接口是否正常**:
   ```bash
   curl http://localhost:5001/api/v1/articles
   ```

2. **在 Trae IDE 中开始压测**:
   ```
   帮我生成压测脚本，测试文章列表接口
   ```

3. **查看压测结果并优化性能**

---

**服务启动完成！准备好进行性能压测了吗？** 🚀
