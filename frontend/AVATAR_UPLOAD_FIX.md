# 站点头像上传功能修复

## 问题描述

站点头像上传后不显示图片，上传成功但预览区域空白。

## 问题原因

原实现使用了 `:action` 和 `@finish` 方式，这种方式需要后端返回特定格式，并且没有正确处理文件上传的响应数据。

## 解决方案

参考打赏功能（DonationSettings）的实现，使用 `:custom-request` 来处理上传。

## 修改内容

### 1. 修改上传组件

**修改前：**
```vue
<n-upload
  :action="uploadUrl"
  :headers="uploadHeaders"
  :show-file-list="false"
  @finish="handleAvatarUpload"
>
  <n-button>上传头像</n-button>
</n-upload>
<div v-if="formData.siteAvatar" class="preview">
  <img :src="formData.siteAvatar" alt="Avatar" />
</div>
```

**修改后：**
```vue
<div class="avatar-preview">
  <img
    v-if="formData.siteAvatar"
    :src="formData.siteAvatar"
    alt="站点头像"
    class="avatar-preview-image"
  />
  <div v-else class="avatar-placeholder">
    <n-icon :component="PersonOutline" size="48" />
    <n-text depth="3">未上传</n-text>
  </div>
</div>
<n-upload
  :custom-request="handleAvatarUpload"
  :show-file-list="false"
  accept="image/*"
>
  <n-button style="width: 100%; margin-top: 12px">
    上传头像
  </n-button>
</n-upload>
```

### 2. 修改上传处理函数

**修改前：**
```typescript
const handleAvatarUpload = ({ event }: any) => {
  const response = JSON.parse(event.target.response)
  formData.siteAvatar = response.url
  message.success('头像上传成功')
}
```

**修改后：**
```typescript
const handleAvatarUpload = async ({ file }: { file: any }) => {
  try {
    const rawFile = file.file || file
    const result = await uploadFile(rawFile as File)
    formData.siteAvatar = resolveServerAssetUrl(result.url)
    message.success('头像上传成功')
  } catch (error: any) {
    console.error('[Upload] Avatar error:', error)
    message.error(`上传失败：${error.response?.data?.error || error.message}`)
  }
}

const uploadFile = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await fetch('/api/v1/upload', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    },
    body: formData,
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || '上传失败')
  }
  
  return await response.json()
}
```

### 3. 添加图片 URL 处理

导入并使用 `resolveServerAssetUrl` 处理服务器返回的图片 URL：

```typescript
import { resolveServerAssetUrl } from '@/utils/assets'

// 在 loadSettings 中
siteAvatar: resolveServerAssetUrl(settings.site_avatar) || ''
siteLogo: resolveServerAssetUrl(settings.site_logo) || ''
ogImage: resolveServerAssetUrl(settings.og_image) || ''
```

### 4. 添加样式

```css
.avatar-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 200px;
  height: 200px;
  background: #f5f5f5;
  border-radius: 8px;
  border: 2px dashed #d9d9d9;
  margin-bottom: 12px;
}

.avatar-preview-image {
  max-width: 100%;
  max-height: 180px;
  border-radius: 8px;
  object-fit: cover;
}

.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #999;
}
```

## 修改的文件

- `frontend/src/views/admin/settings/SiteSettings.vue`

## 功能测试

### 测试步骤

1. 登录后台管理页面
2. 进入"站点设置"
3. 在"基本信息"卡片中找到"站点头像"
4. 点击"上传头像"按钮
5. 选择一张图片文件

### 预期结果

- ✅ 上传成功后显示"上传成功"提示
- ✅ 预览区域显示上传的图片
- ✅ 图片在 200x200 的预览框内居中显示
- ✅ 未上传时显示默认图标和"未上传"文字
- ✅ 保存设置后，前端博客侧边栏显示头像

## 相关功能

同样的修改也应用到了：
- Logo 上传 (`handleLogoUpload`)
- OG 图片上传 (`handleOgImageUpload`)

现在所有图片上传功能都使用统一的处理方式。

## 技术要点

1. **使用 `:custom-request`**：允许完全自定义上传逻辑
2. **处理 File 对象**：Naive UI 传递的是包装对象，需要通过 `file.file || file` 获取真实 File
3. **使用 `resolveServerAssetUrl`**：处理服务器返回的相对路径，转换为完整 URL
4. **错误处理**：捕获上传错误并显示友好提示
5. **预览样式**：参考打赏功能，使用统一的预览样式

## 参考资料

- 打赏功能实现：`frontend/src/views/admin/donation/DonationSettings.vue`
- 图片工具函数：`frontend/src/utils/assets.ts`
