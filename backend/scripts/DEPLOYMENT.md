# 云部署指南

本文档详细介绍如何在云服务器上部署博客系统的数据库和初始化数据。

## 快速部署（推荐）

### 1. 准备环境变量

在云服务器上设置以下环境变量：

```bash
export DB_HOST="114.55.165.189"
export DB_PORT="3306"
export DB_USER="root"
export DB_PASSWORD="Root@123456"
export DB_NAME="blog_db"
```

### 2. 执行一键部署脚本

```bash
cd /path/to/blog/backend
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

脚本会自动：
- ✅ 执行 DDL 创建数据库表
- ✅ 执行 DML 初始化数据
- ✅ 验证部署结果

## 手动部署

如果不想使用一键脚本，可以手动执行：

### 步骤 1：执行 DDL

```bash
cd /path/to/blog/backend

# 主表结构
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < database/ddl/000_init_database.sql

# 评论和浏览数字段
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < database/ddl/001_add_comments_and_view_count.sql
```

### 步骤 2：执行 DML

```bash
# 使用 Python 脚本初始化站点设置
python scripts/init_site_settings.py --init
```

### 步骤 3：验证部署

```bash
# 查看站点设置
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
    SELECT key_name, key_value 
    FROM site_settings 
    ORDER BY key_name;
"
```

## 配置站点头像

### 方式一：通过后台管理界面

1. 访问后台管理页面：`http://your-domain.com/admin`
2. 登录后进入"站点设置"
3. 在"基本信息"卡片中找到"站点头像"
4. 点击"上传头像"按钮
5. 保存设置

### 方式二：使用脚本

```bash
python scripts/init_site_settings.py --update-avatar "https://example.com/your-avatar.png"
```

### 方式三：直接 SQL

```sql
UPDATE site_settings 
SET key_value = 'https://example.com/your-avatar.png', 
    updated_at = NOW() 
WHERE key_name = 'site_avatar';
```

## 部署检查清单

部署完成后，请确认以下事项：

- [ ] 数据库表已创建（`site_settings` 表存在）
- [ ] 站点设置已初始化（至少 20 条设置）
- [ ] `site_avatar` 字段已插入
- [ ] 前端能正常显示博客侧边栏
- [ ] 后台能正常上传和配置头像

## 常见问题排查

### 问题 1：权限不足

**错误信息：** `Access denied for user 'root'@'...'`

**解决方案：**
```bash
# 检查密码是否正确
mysql -h "$DB_HOST" -u "$DB_USER" -p

# 如果需要重置密码
mysql -h "$DB_HOST" -u root -p
> ALTER USER 'root'@'%' IDENTIFIED BY 'new_password';
> FLUSH PRIVILEGES;
```

### 问题 2：数据库不存在

**错误信息：** `Unknown database 'blog_db'`

**解决方案：**
```bash
# 创建数据库
mysql -h "$DB_HOST" -u "$DB_USER" -p -e "CREATE DATABASE IF NOT EXISTS blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 问题 3：找不到 DML 文件

**错误信息：** `FileNotFoundError: database/dml/002_site_settings.sql`

**解决方案：**
```bash
# 确保在 backend 目录下执行
cd /path/to/blog/backend
pwd  # 确认当前目录

# 检查文件是否存在
ls -la database/dml/002_site_settings.sql
```

### 问题 4：Python 依赖缺失

**错误信息：** `ModuleNotFoundError: No module named 'pymysql'`

**解决方案：**
```bash
# 安装依赖
pip install pymysql

# 或者使用虚拟环境
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 部署示例（完整流程）

以下是在云服务器上的完整部署示例：

```bash
# 1. 克隆代码（如果是首次部署）
git clone https://github.com/your-repo/blog.git
cd blog/backend

# 2. 设置环境变量
export DB_HOST="114.55.165.189"
export DB_PORT="3306"
export DB_USER="root"
export DB_PASSWORD="Root@123456"
export DB_NAME="blog_db"

# 3. 安装 Python 依赖
pip install -r requirements.txt

# 4. 执行部署脚本
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 5. 验证部署
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
    SELECT COUNT(*) as setting_count FROM site_settings;
"

# 6. 启动后端服务
python app.py
```

## 回滚操作

如果需要回滚到部署前的状态：

```bash
# 删除新增的站点设置
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
    DELETE FROM site_settings WHERE key_name = 'site_avatar';
"

# 或者删除所有站点设置（谨慎使用）
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
    DELETE FROM site_settings;
"
```

## 监控和维护

### 查看设置数量

```bash
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
    SELECT COUNT(*) as total_settings FROM site_settings;
"
```

### 查看最近更新的设置

```bash
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
    SELECT key_name, key_value, updated_at 
    FROM site_settings 
    ORDER BY updated_at DESC 
    LIMIT 10;
"
```

### 定期备份

```bash
# 备份站点设置表
mysqldump -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" site_settings > site_settings_backup_$(date +%Y%m%d_%H%M%S).sql
```

## 相关文档

- [DML 脚本说明](README.md)
- [站点设置字段说明](README.md#站点设置字段说明)
- [后端 API 文档](../../docs/api/)
- [前端部署指南](../../frontend/README.md)
