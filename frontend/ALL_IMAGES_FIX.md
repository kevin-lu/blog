# 全站图片显示修复

## 问题描述

所有上传的图片（站点头像、Logo、打赏二维码）都不显示了。

## 问题原因

1. **环境变量缺失**：没有设置 `VITE_API_TARGET`，导致 `resolveServerAssetUrl` 使用默认的本地地址
2. **Sidebar 组件未处理**：`Sidebar.vue` 中加载站点头像时没有使用 `resolveServerAssetUrl` 处理 URL

## 修复内容

### 1. 环境变量配置

**修改的文件：**
- `frontend/.env`
- `frontend/.env.production`
- `frontend/.env.example`（新建）

**添加的配置：**
```bash
VITE_API_TARGET=http://114.55.165.189:5001
```

### 2. Sidebar 组件修复

**文件：** `frontend/src/components/article/Sidebar.vue`

**修改前：**
```typescript
import { categoryApi, tagApi, settingApi } from '@/api'
import DonationCard from '@/components/donation/DonationCard.vue'

// ...

siteSettings.value = {
  site_name: settings.site_name || '我的博客',
  site_description: settings.site_description || '技术分享平台',
  site_avatar: settings.site_avatar || '',  // ❌ 未处理 URL
  github_url: settings.github_url || '',
  twitter_url: settings.twitter_url || '',
  email: settings.email || '',
}
```

**修改后：**
```typescript
import { categoryApi, tagApi, settingApi } from '@/api'
import DonationCard from '@/components/donation/DonationCard.vue'
import { resolveServerAssetUrl } from '@/utils/assets'  // ✅ 添加工具导入

// ...

siteSettings.value = {
  site_name: settings.site_name || '我的博客',
  site_description: settings.site_description || '技术分享平台',
  site_avatar: resolveServerAssetUrl(settings.site_avatar || ''),  // ✅ 处理 URL
  github_url: settings.github_url || '',
  twitter_url: settings.twitter_url || '',
  email: settings.email || '',
}
```

### 3. DonationCard 组件增强

**文件：** `frontend/src/components/donation/DonationCard.vue`

**修改内容：**
- 添加调试日志
- 确保空值处理正确

```typescript
onMounted(async () => {
  try {
    const data = await donationApi.getSettings()
    console.log('[DonationCard] Raw data:', data)
    if (data) {
      settings.value = {
        ...data,
        wechat_qr: resolveServerAssetUrl(data.wechat_qr || ''),  // ✅ 处理空值
        alipay_qr: resolveServerAssetUrl(data.alipay_qr || ''),  // ✅ 处理空值
      }
      console.log('[DonationCard] Processed settings:', settings.value)
    }
  } catch (error) {
    console.error('Failed to load donation settings:', error)
  }
})
```

## 修改的文件汇总

1. ✅ `frontend/.env` - 添加 `VITE_API_TARGET`
2. ✅ `frontend/.env.production` - 添加 `VITE_API_TARGET`
3. ✅ `frontend/.env.example` - 新建示例文件
4. ✅ `frontend/src/components/article/Sidebar.vue` - 添加头像 URL 处理
5. ✅ `frontend/src/components/donation/DonationCard.vue` - 增强空值处理和日志

## 工作原理

`resolveServerAssetUrl` 函数会自动识别并处理特定前缀的相对路径：

```typescript
// 输入（数据库存储的相对路径）
'/documents/avatar.png'
'/uploads/qrcode-wechat.png'
'/images/logo.png'

// 输出（完整的 URL）
'http://114.55.165.189:5001/documents/avatar.png'
'http://114.55.165.189:5001/uploads/qrcode-wechat.png'
'http://114.55.165.189:5001/images/logo.png'
```

## 验证方法

### 1. 浏览器控制台日志

打开浏览器开发者工具（F12），应该能看到以下日志：

```
[Sidebar] Raw settings: {...}
[Sidebar] Processed settings: {...}
[DonationCard] Raw data: {...}
[DonationCard] Processed settings: {...}
```

### 2. 图片 URL 检查

在控制台中检查图片元素的 `src` 属性：
- 站点头像：应该是完整的 URL（包含 `http://114.55.165.189:5001`）
- 微信二维码：应该是完整的 URL
- 支付宝二维码：应该是完整的 URL

### 3. 直接访问

在浏览器中直接访问图片 URL 验证服务器是否正常：
```
http://114.55.165.189:5001/documents/xxx.png
http://114.55.165.189:5001/uploads/xxx.png
```

## 测试步骤

### 站点头像测试

1. 访问后台管理页面
2. 进入"站点设置"
3. 上传站点头像
4. 保存设置
5. 访问前端博客页面
6. 检查侧边栏是否显示头像

### 打赏二维码测试

1. 访问后台管理页面
2. 进入"打赏设置"
3. 上传微信/支付宝二维码
4. 保存设置
5. 访问前端博客页面
6. 检查侧边栏是否显示二维码

## 前端服务器

已重启前端开发服务器，运行在：
- **地址：** http://localhost:5175/
- **API 目标：** http://114.55.165.189:5001

## 注意事项

1. **环境变量修改后必须重启**：Vite 在启动时读取环境变量
2. **生产环境需要重新构建**：`npm run build` 会打包时的环境变量
3. **缓存问题**：如果图片仍然不显示，尝试清除浏览器缓存（Ctrl+Shift+Delete）

## 相关文件

- 工具函数：`frontend/src/utils/assets.ts`
- 站点设置：`frontend/src/views/admin/settings/SiteSettings.vue`
- 打赏设置：`frontend/src/views/admin/donation/DonationSettings.vue`
- 侧边栏：`frontend/src/components/article/Sidebar.vue`
- 打赏卡片：`frontend/src/components/donation/DonationCard.vue`

## 快速修复命令

```bash
# 如果图片仍然不显示，重启前端服务器
cd frontend
# Ctrl+C 停止当前服务器
npm run dev
```
