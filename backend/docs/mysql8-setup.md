# MySQL 8 数据库配置指南

## 1. 安装依赖

```bash
cd backend
./venv/bin/pip install pymysql
```

## 2. 创建 MySQL 数据库

登录 MySQL 后执行：

```sql
CREATE DATABASE blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'blog_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON blog_db.* TO 'blog_user'@'%';
FLUSH PRIVILEGES;
```

## 3. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，修改数据库连接：

```env
# MySQL 8 Configuration
DATABASE_URL=mysql+pymysql://blog_user:your_password@localhost:3306/blog_db?charset=utf8mb4
```

### 连接字符串说明

```
mysql+pymysql://username:password@host:port/database?charset=utf8mb4
```

- `username`: MySQL 用户名
- `password`: MySQL 密码
- `host`: MySQL 服务器地址（本地为 `localhost` 或 `127.0.0.1`）
- `port`: MySQL 端口（默认 `3306`）
- `database`: 数据库名称
- `charset=utf8mb4`: 使用 utf8mb4 字符集（支持 emoji）

## 4. 运行数据库迁移

```bash
# 如果已有迁移脚本
./venv/bin/python scripts/add_view_count_migration.py
./venv/bin/python scripts/add_comment_fields_migration.py

# 或者使用 Flask-Migrate（如果已安装）
flask db upgrade
```

## 5. 验证连接

```bash
./venv/bin/python << 'EOF'
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    try:
        db.engine.connect()
        print("✅ 数据库连接成功！")
        print(f"数据库引擎：{db.engine.name}")
        print(f"数据库 URL：{db.engine.url}")
    except Exception as e:
        print(f"❌ 数据库连接失败：{e}")
EOF
```

## 6. 远程 MySQL 配置

如果 MySQL 服务器在远程机器上：

### 6.1 修改 MySQL 配置

编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`：

```ini
[mysqld]
bind-address = 0.0.0.0
```

重启 MySQL：

```bash
sudo systemctl restart mysql
```

### 6.2 配置防火墙

```bash
sudo ufw allow 3306/tcp
```

### 6.3 创建远程访问用户

```sql
CREATE USER 'blog_user'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON blog_db.* TO 'blog_user'@'%';
FLUSH PRIVILEGES;
```

### 6.4 环境变量

```env
DATABASE_URL=mysql+pymysql://blog_user:your_password@remote-host-ip:3306/blog_db?charset=utf8mb4
```

## 7. 连接池配置

已在 `app/config.py` 中配置了优化的连接池参数：

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,      # 连接前 ping 测试
    'pool_recycle': 300,        # 5 分钟回收连接
    'pool_size': 10,            # 连接池大小
    'max_overflow': 20,         # 最大溢出连接数
    'pool_timeout': 30,         # 获取连接超时
}
```

## 8. 常见问题

### 问题 1：`No module named 'pymysql'`

**解决**：安装 pymysql

```bash
./venv/bin/pip install pymysql
```

### 问题 2：`Access denied for user`

**解决**：检查用户名密码是否正确，确保用户有访问权限

### 问题 3：`Can't connect to MySQL server`

**解决**：
- 检查 MySQL 服务是否运行
- 检查防火墙设置
- 检查 `bind-address` 配置

### 问题 4：`Unknown character set: 'utf8mb4'`

**解决**：确保 MySQL 版本 >= 5.5.3，并创建数据库时指定字符集

## 9. 备份与恢复

### 备份数据库

```bash
mysqldump -u blog_user -p blog_db > backup.sql
```

### 恢复数据库

```bash
mysql -u blog_user -p blog_db < backup.sql
```

## 10. 性能优化建议

1. **添加索引**：为常用查询字段添加索引
2. **查询优化**：使用 EXPLAIN 分析慢查询
3. **连接池**：根据并发量调整连接池大小
4. **慢查询日志**：开启慢查询日志优化 SQL

```sql
-- 查看慢查询日志
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';
```

---

配置完成后，重启后端服务即可使用 MySQL 8 数据库！
