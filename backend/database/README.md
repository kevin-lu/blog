# 数据库迁移指南

本目录包含所有数据库迁移脚本，用于 MySQL 8 数据库的初始化和数据迁移。

## 目录结构

```
backend/database/
├── ddl/                      # Data Definition Language (结构定义)
│   ├── 000_init_database.sql    # 数据库初始化（创建所有表）
│   └── 001_add_comments_and_view_count.sql  # 增量变更
├── dml/                      # Data Manipulation Language (数据操作)
│   └── 001_init_data.sql        # 初始化数据
└── README.md                 # 本文档
```

## 使用方法

### 方法 1：全新安装（推荐）

如果是全新安装 MySQL 8，直接运行初始化脚本：

```bash
# 连接到 MySQL
mysql -h 114.55.165.189 -u root -p

# 执行初始化脚本
source /path/to/backend/database/ddl/000_init_database.sql

# 执行数据初始化脚本
source /path/to/backend/database/dml/001_init_data.sql
```

### 方法 2：增量迁移

如果数据库已存在，只需运行增量脚本：

```bash
# 连接到 MySQL
mysql -h 114.55.165.189 -u root -p blog_db

# 执行增量 DDL 脚本
source /path/to/backend/database/ddl/001_add_comments_and_view_count.sql

# 执行数据初始化脚本
source /path/to/backend/database/dml/001_init_data.sql
```

### 方法 3：使用 Python 脚本

也可以使用 Python 脚本自动执行：

```bash
cd backend

# 初始化数据库
./venv/bin/python -c "
import pymysql
conn = pymysql.connect(host='114.55.165.189', user='root', password='Root@123456', charset='utf8mb4')
cursor = conn.cursor()
with open('database/ddl/000_init_database.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
    cursor.execute(sql)
conn.commit()
conn.close()
"
```

## 脚本说明

### DDL 脚本

#### 000_init_database.sql
- 创建数据库 `blog_db`
- 创建所有基础表结构：
  - `users` - 用户表
  - `articles` - 文章表
  - `article_meta` - 文章元数据（浏览次数等）
  - `tags` - 标签表
  - `article_tags` - 文章标签关联表
  - `categories` - 分类表
  - `article_categories` - 文章分类关联表
  - `comments` - 评论表
  - `settings` - 系统设置表
  - `operation_logs` - 操作日志表

#### 001_add_comments_and_view_count.sql
- 增量变更脚本
- 添加 `view_count` 字段到 `article_meta` 表
- 创建评论系统相关索引

### DML 脚本

#### 001_init_data.sql
- 初始化数据脚本
- 更新现有文章的浏览次数
- 可选：插入测试数据
- 可选：数据清理和迁移

## 版本历史

| 版本 | 日期 | 脚本 | 说明 |
|------|------|------|------|
| 1.0 | 2026-05-12 | 000_init_database.sql | 初始数据库结构 |
| 1.1 | 2026-05-12 | 001_add_comments_and_view_count.sql | 添加评论和浏览次数 |

## 回滚方法

如果需要回滚变更，每个 DDL 脚本底部都包含回滚 SQL（已注释）。

示例：回滚浏览次数字段

```sql
-- 移除浏览次数索引
DROP INDEX idx_article_view_count ON article_meta;

-- 移除浏览次数字段
ALTER TABLE article_meta DROP COLUMN view_count;
```

## 验证迁移

迁移完成后，验证表结构：

```sql
USE blog_db;

-- 查看所有表
SHOW TABLES;

-- 查看文章表结构
DESCRIBE articles;

-- 查看文章元数据表
DESCRIBE article_meta;

-- 查看评论表
DESCRIBE comments;

-- 检查数据
SELECT COUNT(*) FROM articles;
SELECT COUNT(*) FROM comments;
SELECT SUM(view_count) FROM article_meta;
```

## 注意事项

1. **执行顺序**：先执行 DDL，再执行 DML
2. **字符集**：所有表使用 `utf8mb4` 字符集（支持 emoji）
3. **外键约束**：使用 `ON DELETE CASCADE` 或 `SET NULL`
4. **时间字段**：使用 `TIMESTAMP` 自动更新
5. **索引优化**：常用查询字段已添加索引

## 常见问题

### Q: 如何查看当前数据库版本？
A: 查看 `settings` 表中的版本信息（如果已添加版本管理）

### Q: 迁移失败怎么办？
A: 检查错误日志，确认是语法错误还是数据冲突，然后使用回滚脚本恢复

### Q: 如何在生产环境执行？
A: 
1. 先在测试环境验证
2. 备份生产数据库
3. 在业务低峰期执行
4. 执行后验证数据完整性

## 自动化迁移（未来计划）

计划集成 Alembic 或 Flask-Migrate 实现自动化迁移：

```bash
# 未来可能支持的命令
flask db init
flask db migrate -m "Add comments"
flask db upgrade
```

---

**维护者**: 开发团队  
**最后更新**: 2026-05-12
