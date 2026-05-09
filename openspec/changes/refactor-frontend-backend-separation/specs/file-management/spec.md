## ADDED Requirements

### Requirement: 文件上传

系统应支持文件上传功能，包括图片、文档等文件的上传和管理。

#### Scenario: 上传图片
- **WHEN** 用户上传 JPG/PNG 格式的图片
- **THEN** 系统保存文件到 `uploads/images/` 目录，返回文件 URL

#### Scenario: 上传文档
- **WHEN** 用户上传 PDF/Word 文档
- **THEN** 系统保存文件到 `uploads/documents/` 目录，返回文件 URL

#### Scenario: 文件大小限制
- **WHEN** 用户上传超过 10MB 的文件
- **THEN** 系统拒绝上传并返回错误提示

#### Scenario: 文件类型限制
- **WHEN** 用户上传不支持的文件类型
- **THEN** 系统拒绝上传并返回错误提示

### Requirement: 图片压缩

系统应自动压缩上传的图片，减少存储空间和加载时间。

#### Scenario: 压缩大图
- **WHEN** 用户上传分辨率超过 1920x1080 的图片
- **THEN** 系统自动压缩图片到最大 1920x1080，质量 85%

#### Scenario: 生成缩略图
- **WHEN** 用户上传文章封面图
- **THEN** 系统自动生成 300x200 的缩略图

#### Scenario: 保留 Exif 信息
- **WHEN** 系统压缩图片
- **THEN** 系统保留图片的 Exif 元数据 (拍摄时间、相机信息等)

### Requirement: CDN 集成

系统应支持 CDN 加速，提升静态资源访问速度。

#### Scenario: CDN 资源访问
- **WHEN** 用户请求上传的文件
- **THEN** 系统返回 CDN 域名下的文件 URL

#### Scenario: CDN 缓存刷新
- **WHEN** 管理员更新文件
- **THEN** 系统自动刷新 CDN 缓存
