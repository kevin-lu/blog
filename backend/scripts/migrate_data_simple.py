#!/usr/bin/env python3
"""
SQLite to MySQL 数据迁移脚本（最终版）
直接处理 article_meta 和 categories 表的时间戳问题
"""
import sqlite3
import pymysql
from datetime import datetime

# 配置
SQLITE_DB = '../../blog.db'
MYSQL_CONFIG = {
    'host': '114.55.165.189',
    'port': 3306,
    'user': 'root',
    'password': 'Root@123456',
    'database': 'blog_db',
    'charset': 'utf8mb4'
}


def convert_timestamp_string(value):
    """转换时间戳字符串为日期格式"""
    if value is None:
        return None
    
    # 如果是字符串且看起来像时间戳
    if isinstance(value, str) and '.' in value:
        try:
            timestamp = float(value)
            if timestamp > 1e12:  # 毫秒级
                return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, OSError):
            pass
    
    return value


# 连接 SQLite
sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# 连接 MySQL
mysql_conn = pymysql.connect(**MYSQL_CONFIG)
mysql_cursor = mysql_conn.cursor()

print("📊 迁移 article_meta 表...")

# 读取 SQLite 数据
sqlite_cursor.execute("SELECT * FROM article_meta")
rows = sqlite_cursor.fetchall()

for row in rows:
    try:
        # 转换时间戳
        created_at = convert_timestamp_string(row['created_at'])
        updated_at = convert_timestamp_string(row['updated_at'])
        published_at = convert_timestamp_string(row['published_at'])
        
        # 插入 MySQL
        mysql_cursor.execute("""
            INSERT INTO article_meta 
            (id, view_count, created_at, updated_at, published_at) 
            VALUES (%s, %s, %s, %s, %s)
        """, (row['id'], row['view_count'], created_at, updated_at, published_at))
        print(f"  ✅ 迁移文章 ID={row['id']}, views={row['view_count']}")
    except Exception as e:
        print(f"  ⚠️  失败：{e}")

mysql_conn.commit()

print("\n📊 迁移 categories 表...")

# 读取 categories 数据
sqlite_cursor.execute("SELECT * FROM categories")
rows = sqlite_cursor.fetchall()

for row in rows:
    try:
        # 转换时间戳
        created_at = convert_timestamp_string(row['created_at'])
        updated_at = convert_timestamp_string(row['updated_at'])
        
        # 插入 MySQL
        mysql_cursor.execute("""
            INSERT INTO categories 
            (id, name, slug, description, parent_id, sort_order, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (row['id'], row['name'], row['slug'], row['description'], 
              row['parent_id'], row['sort_order'], created_at, updated_at))
        print(f"  ✅ 迁移分类 ID={row['id']}, name={row['name']}")
    except Exception as e:
        print(f"  ⚠️  失败：{e}")

mysql_conn.commit()

# 关闭连接
sqlite_cursor.close()
sqlite_conn.close()
mysql_cursor.close()
mysql_conn.close()

print("\n✅ 迁移完成！")
