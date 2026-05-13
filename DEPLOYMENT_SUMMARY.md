# 站点头像功能部署总结

## 新增文件清单

### 1. 数据库 DML 脚本
📄 **位置：** `backend/database/dml/002_site_settings.sql`

**作用：** 初始化站点设置数据，包括新增的 `site_avatar` 字段

**主要内容：**
- 插入 `site_avatar` 默认值
- 确保所有基本设置存在
- 确保关于页面设置存在
- 确保评论设置存在
- 幂等性设计（使用 `ON DUPLICATE KEY UPDATE`）

---

### 2. Python 初始化脚本
📄 **位置：** `backend/scripts/init_site_settings.py`

**作用：** 方便执行站点设置初始化的 Python 工具

**使用方法：**
```bash
# 初始化所有站点设置
python scripts/init_site_settings.py --init

# 单独更新站点头像
python scripts/init_site_settings.py --update-avatar "https://example.com/avatar.png"
```

**支持的环境变量：**
- `DB_HOST` - 数据库主机（默认：localhost）
- `DB_PORT` - 数据库端口（默认：3306）
- `DB_USER` - 数据库用户（默认：root）
- `DB_PASSWORD` - 数据库密码（默认：空）
- `DB_NAME` - 数据库名称（默认：blog_db）

---

### 3. 一键部署脚本
📄 **位置：** `backend/scripts/deploy.sh`

**作用：** 一键完成数据库 DDL 和 DML 的执行

**使用方法：**
```bash
cd backend
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**自动完成：**
- ✅ 检查环境变量
- ✅ 执行 DDL（创建表结构）
- ✅ 执行 DML（初始化数据）
- ✅ 验证部署结果

---

### 4. 部署文档
📄 **位置：** `backend/scripts/DEPLOYMENT.md`

**内容：**
- 快速部署指南
- 手动部署步骤
- 配置站点头像的三种方式
- 部署检查清单
- 常见问题排查
- 完整部署示例
- 回滚操作
- 监控和维护

---

### 5. DML 说明文档
📄 **位置：** `backend/database/dml/README.md`

**内容：**
- 目录结构说明
- 云部署流程（三种方式）
- 环境变量配置
- 站点设置字段说明
- 回滚操作
- 验证方法
- 常见问题

---

## 修改的文件清单

### 后端修改

1. **`backend/app/schemas/site_setting.py`**
   - `SiteSettingUpdate` 类：添加 `site_avatar` 字段
   - `SiteSettingResponse` 类：添加 `site_avatar` 字段

2. **`backend/app/api/v1/settings.py`**
   - `DEFAULT_SETTINGS` 字典：添加 `site_avatar` 默认值

---

### 前端修改

1. **`frontend/src/api/setting.ts`**
   - `SiteSettings` 接口：添加 `site_avatar` 字段

2. **`frontend/src/components/article/Sidebar.vue`**
   - 导入 `settingApi`
   - 修改 `siteSettings` 数据结构
   - 在 `onMounted` 中调用 API 获取设置
   - 模板中使用正确的字段名

3. **`frontend/src/views/admin/settings/SiteSettings.vue`**
   - 添加"站点头像"上传字段
   - 添加 `siteAvatar` 到 `formData`
   - 添加 `handleAvatarUpload` 处理函数
   - 在 `handleSave` 中提交 `site_avatar`
   - 在 `loadSettings` 中加载 `site_avatar`

---

## 快速部署流程

### 方式一：一键部署（推荐）

```bash
cd /path/to/blog/backend

# 设置环境变量
export DB_HOST="114.55.165.189"
export DB_PORT="3306"
export DB_USER="root"
export DB_PASSWORD="Root@123456"
export DB_NAME="blog_db"

# 执行一键部署
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 方式二：手动部署

```bash
cd /path/to/blog/backend

# 1. 执行 DDL
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < database/ddl/000_init_database.sql
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < database/ddl/001_add_comments_and_view_count.sql

# 2. 执行 DML
python scripts/init_site_settings.py --init

# 3. 验证
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT key_name, key_value FROM site_settings ORDER BY key_name"
```

---

## 配置站点头像

### 后台管理界面配置

1. 访问：`http://your-domain.com/admin`
2. 进入"站点设置"
3. 在"基本信息"卡片中找到"站点头像"
4. 点击"上传头像"
5. 保存设置

### 脚本配置

```bash
python scripts/init_site_settings.py --update-avatar "https://example.com/your-avatar.png"
```

### 直接 SQL 配置

```sql
UPDATE site_settings 
SET key_value = 'https://example.com/your-avatar.png', 
    updated_at = NOW() 
WHERE key_name = 'site_avatar';
```

---

## 验证部署

### 1. 检查数据库

```sql
-- 查看所有设置
SELECT key_name, key_value, description 
FROM site_settings 
ORDER BY key_name;

-- 查看头像设置
SELECT key_name, key_value, description 
FROM site_settings 
WHERE key_name = 'site_avatar';

-- 统计设置数量
SELECT COUNT(*) as total FROM site_settings;
```

### 2. 检查前端

访问博客首页，查看右侧边栏：
- 头像应该显示在"我的博客"卡片顶部
- 如果未设置头像，显示默认图标

### 3. 检查后台

访问后台管理页面：
- 进入"站点设置"
- 应该能看到"站点头像"上传字段
- 可以上传新头像并保存

---

## 数据字段说明

### 新增字段

| 字段名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `site_avatar` | String | 站点头像 URL | (空) |

### 完整设置列表

**基本设置（7 个）：**
- `site_name` - 站点名称
- `site_description` - 站点描述
- `site_logo` - 站点 Logo
- `site_avatar` - **站点头像（新增）**
- `site_url` - 站点 URL
- `site_keywords` - 站点关键词
- `og_image` - OG 图片

**社交媒体（4 个）：**
- `github_url` - GitHub 链接
- `twitter_url` - Twitter 链接
- `weibo_url` - 微博链接
- `email` - 联系邮箱

**关于页面（10 个）：**
- `about_welcome_title` - 欢迎标题
- `about_welcome_content` - 欢迎内容
- `about_author_title` - 作者标题
- `about_author_content` - 作者内容
- `about_tech_stack_title` - 技术栈标题
- `about_tech_stack_items` - 技术栈列表（JSON）
- `about_contact_title` - 联系标题
- `about_contact_email` - 联系邮箱
- `about_contact_github` - GitHub 链接
- `about_contact_github_label` - GitHub 显示文本

**评论设置（2 个）：**
- `comment_require_review` - 评论审核
- `comment_enabled` - 启用评论

**总计：** 23 个设置字段

---

## 回滚方案

### 删除新增的头像设置

```bash
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
    DELETE FROM site_settings WHERE key_name = 'site_avatar';
"
```

### 删除所有站点设置

```bash
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
    DELETE FROM site_settings;
"
```

---

## 文件依赖关系

```
后端修改
├── app/schemas/site_setting.py (添加 site_avatar 字段)
├── app/api/v1/settings.py (添加默认值)
└── database/dml/002_site_settings.sql (初始化数据)

前端修改
├── src/api/setting.ts (添加类型定义)
├── src/components/article/Sidebar.vue (显示头像)
└── src/views/admin/settings/SiteSettings.vue (配置头像)

部署工具
├── scripts/deploy.sh (一键部署)
├── scripts/init_site_settings.py (Python 初始化工具)
├── scripts/DEPLOYMENT.md (部署文档)
└── database/dml/README.md (DML 说明)
```

---

## 最佳实践

1. **幂等性设计** - 所有 DML 使用 `ON DUPLICATE KEY UPDATE` 确保可重复执行
2. **环境变量** - 敏感信息通过环境变量传递，不要硬编码
3. **备份优先** - 部署前先备份数据库
4. **验证部署** - 部署完成后执行验证步骤
5. **文档更新** - 保持文档与代码同步

---

## 相关文档

- [部署指南](scripts/DEPLOYMENT.md)
- [DML 说明](database/dml/README.md)
- [API 文档](docs/api/)
- [前端部署](frontend/README.md)

---

## 更新日期

2026-05-13
