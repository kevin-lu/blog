# 数据库初始化脚本说明

本文档说明博客系统的数据库初始化脚本使用方法。

## 目录结构

```
backend/database/
├── ddl/                        # 数据定义语言（表结构）
│   ├── 000_init_database.sql   # 初始化数据库和所有表
│   └── 001_add_comments_and_view_count.sql  # 新增评论和浏览数字段
└── dml/                        # 数据操作语言（初始化数据）
    ├── 001_init_data.sql       # 初始化浏览次数和评论数据
    ├── 002_site_settings.sql   # 初始化站点设置（新增）
    └── README.md               # 本文档
```

## 云部署流程

### 方式一：自动部署（推荐）

在云服务器上执行以下命令：

```bash
cd /path/to/blog/backend

# 1. 执行 DDL（表结构）
mysql -h <数据库地址> -u <用户名> -p <数据库名> < database/ddl/000_init_database.sql
mysql -h <数据库地址> -u <用户名> -p <数据库名> < database/ddl/001_add_comments_and_view_count.sql

# 2. 执行 DML（初始化数据）
python scripts/init_site_settings.py --init

# 3. 验证设置
mysql -h <数据库地址> -u <用户名> -p <数据库名> -e "SELECT key_name, key_value FROM site_settings ORDER BY key_name"
```

### 方式二：手动执行 SQL

```bash
# 连接到数据库
mysql -h <数据库地址> -u <用户名> -p <数据库名>

# 执行 DML 脚本
source /path/to/backend/database/dml/002_site_settings.sql

# 查看结果
SELECT key_name, key_value FROM site_settings WHERE key_name = 'site_avatar';
```

### 方式三：使用 Python 脚本

```bash
cd /path/to/blog/backend

# 初始化所有站点设置
python scripts/init_site_settings.py --init

# 单独更新站点头像
python scripts/init_site_settings.py --update-avatar "https://example.com/avatar.png"
```

## 环境变量

脚本支持以下环境变量：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DB_HOST` | 数据库主机地址 | localhost |
| `DB_PORT` | 数据库端口 | 3306 |
| `DB_USER` | 数据库用户名 | root |
| `DB_PASSWORD` | 数据库密码 | (空) |
| `DB_NAME` | 数据库名称 | blog_db |

示例：

```bash
DB_HOST=114.55.165.189 \
DB_USER=root \
DB_PASSWORD=Root@123456 \
DB_NAME=blog_db \
python scripts/init_site_settings.py --init
```

## 站点设置字段说明

### 基本设置

| 字段名 | 说明 | 默认值 |
|--------|------|--------|
| `site_name` | 博客站点名称 | 我的博客 |
| `site_description` | 博客站点描述 | 技术分享平台 |
| `site_logo` | 博客站点 Logo URL | (空) |
| `site_avatar` | **站点头像 URL**（新增） | (空) |
| `site_url` | 博客站点 URL | (空) |
| `site_keywords` | 博客站点关键词 | (空) |
| `og_image` | 默认 OG 图片 | (空) |

### 社交媒体链接

| 字段名 | 说明 | 默认值 |
|--------|------|--------|
| `github_url` | GitHub 主页链接 | (空) |
| `twitter_url` | Twitter 主页链接 | (空) |
| `weibo_url` | 微博主页链接 | (空) |
| `email` | 联系邮箱 | (空) |

### 关于页面设置

| 字段名 | 说明 | 默认值 |
|--------|------|--------|
| `about_welcome_title` | 欢迎标题 | 欢迎来到我的博客 |
| `about_welcome_content` | 欢迎内容 | (技术分享平台描述) |
| `about_author_title` | 作者标题 | 关于博主 |
| `about_author_content` | 作者内容 | (开发者描述) |
| `about_tech_stack_title` | 技术栈标题 | 技术栈 |
| `about_tech_stack_items` | 技术栈列表（JSON） | ["Vue.js", "React", ...] |
| `about_contact_title` | 联系标题 | 联系方式 |
| `about_contact_email` | 联系邮箱 | (空) |
| `about_contact_github` | GitHub 链接 | (空) |
| `about_contact_github_label` | GitHub 显示文本 | GitHub |

### 评论设置

| 字段名 | 说明 | 默认值 |
|--------|------|--------|
| `comment_require_review` | 评论需要审核 | true |
| `comment_enabled` | 启用评论功能 | true |

## 回滚操作

如果需要回滚（删除新增的设置）：

```bash
mysql -h <数据库地址> -u <用户名> -p <数据库名> -e "DELETE FROM site_settings WHERE key_name = 'site_avatar'"
```

或者删除所有站点设置（谨慎使用）：

```bash
mysql -h <数据库地址> -u <用户名> -p <数据库名> -e "DELETE FROM site_settings"
```

## 验证部署

执行以下 SQL 验证部署是否成功：

```sql
-- 查看所有设置
SELECT key_name, key_value, description 
FROM site_settings 
ORDER BY key_name;

-- 查看头像设置
SELECT key_name, key_value, description 
FROM site_settings 
WHERE key_name = 'site_avatar';
```

## 常见问题

### Q: 脚本执行失败怎么办？
A: 检查以下几点：
1. 确保在 `backend` 目录下执行脚本
2. 检查数据库连接配置是否正确
3. 确保数据库用户有足够权限
4. 查看错误日志

### Q: 如何更新已有的设置？
A: 使用后台管理界面的"站点设置"页面进行修改，或者直接使用 SQL UPDATE 语句。

### Q: 头像上传后在哪里显示？
A: 头像会显示在博客前端右侧边栏的"我的博客"卡片顶部。

## 更新日志

### 2026-05-13
- 新增 `site_avatar` 字段支持站点头像配置
- 创建 `002_site_settings.sql` 初始化脚本
- 创建 `init_site_settings.py` Python 工具脚本

### 2026-05-12
- 新增评论系统相关表和字段
- 新增浏览次数统计功能
