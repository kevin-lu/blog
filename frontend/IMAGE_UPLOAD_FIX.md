# 图片上传不显示问题修复

## 问题描述

上传站点头像后，返回的 URL 是 `/documents/4ca6380f355b4eb5baeddf50445200fd_test.png`，但图片不显示。

## 问题原因

`resolveServerAssetUrl` 函数会将相对路径转换为完整 URL，但需要使用 `VITE_API_TARGET` 环境变量来指定服务器地址。

之前没有设置这个环境变量，所以使用了默认值 `http://127.0.0.1:5001`（本地地址）。

## 解决方案

### 1. 设置环境变量

**开发环境（.env）：**
```bash
VITE_API_TARGET=http://127.0.0.1:5001
```

**生产环境（.env.production）：**
```bash
VITE_API_TARGET=http://114.55.165.189:5001
```

### 2. 重启开发服务器

修改 `.env` 文件后，需要重启 Vite 开发服务器：

```bash
# 停止当前服务器（Ctrl+C）
# 然后重新启动
npm run dev
```

### 3. 重新构建生产版本

如果是生产环境问题，需要重新构建：

```bash
npm run build
```

## 工作原理

`resolveServerAssetUrl` 函数会自动处理以 `/uploads/`、`/images/`、`/documents/` 开头的路径：

```typescript
// 输入
resolveServerAssetUrl('/documents/4ca6380f355b4eb5baeddf50445200fd_test.png')

// 输出（开发环境）
http://127.0.0.1:5001/documents/4ca6380f355b4eb5baeddf50445200fd_test.png

// 输出（生产环境）
http://114.55.165.189:5001/documents/4ca6380f355b4eb5baeddf50445200fd_test.png
```

## 验证方法

### 方法 1：浏览器开发者工具

1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 上传图片
4. 查看图片请求的完整 URL
5. 确认 URL 是否正确

### 方法 2：控制台日志

在 SiteSettings.vue 中添加日志：

```typescript
const handleAvatarUpload = async ({ file }: { file: any }) => {
  try {
    const rawFile = file.file || file
    const result = await uploadFile(rawFile as File)
    const avatarUrl = resolveServerAssetUrl(result.url)
    console.log('[Upload] Original URL:', result.url)
    console.log('[Upload] Resolved URL:', avatarUrl)
    formData.siteAvatar = avatarUrl
    message.success('头像上传成功')
  } catch (error: any) {
    console.error('[Upload] Avatar error:', error)
    message.error(`上传失败：${error.response?.data?.error || error.message}`)
  }
}
```

### 方法 3：直接访问

在浏览器中直接访问图片 URL：
```
http://114.55.165.189:5001/documents/4ca6380f355b4eb5baeddf50445200fd_test.png
```

如果能正常显示图片，说明服务器端正常，只是前端 URL 解析问题。

## 修改的文件

- ✅ `frontend/.env` - 添加 `VITE_API_TARGET`
- ✅ `frontend/.env.production` - 添加 `VITE_API_TARGET`
- ✅ `frontend/.env.example` - 环境变量示例

## 注意事项

1. **修改 .env 后必须重启**：Vite 在启动时读取环境变量，运行时修改不会生效
2. **生产环境需要重新构建**：`npm run build` 会打包时的环境变量
3. **检查 CORS**：确保后端服务器允许跨域请求

## 相关文件

- 工具函数：`frontend/src/utils/assets.ts`
- 使用位置：`frontend/src/views/admin/settings/SiteSettings.vue`
- 打赏功能参考：`frontend/src/views/admin/donation/DonationSettings.vue`

## 快速修复步骤

```bash
# 1. 确认 .env 文件已修改
cat frontend/.env

# 2. 重启开发服务器
cd frontend
npm run dev

# 3. 测试上传功能
# 访问 http://localhost:5173/admin/settings
# 上传站点头像
```

## 生产环境部署

```bash
# 1. 设置生产环境变量
export VITE_API_TARGET=http://114.55.165.189:5001

# 2. 构建生产版本
npm run build

# 3. 部署到服务器
# (复制 dist 目录到 web 服务器)
```
