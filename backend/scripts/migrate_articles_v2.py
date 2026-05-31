#!/usr/bin/env python3
"""
SQLite to MySQL 数据迁移脚本（最终版）
将 SQLite 的 article_meta 数据直接更新到 MySQL 的 article_meta 表
"""
import sqlite3
import pymysql
import os
from datetime import datetime
import uuid

# 配置
SQLITE_DB = os.path.join(os.path.dirname(__file__), '../../blog.db')
MYSQL_CONFIG = {
    'host': '114.55.165.189',
    'port': 3306,
    'user': 'root',
    'password': 'Root@123456',
    'database': 'blog_db',
    'charset': 'utf8mb4'
}


def convert_timestamp(value):
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

print("=" * 60)
print("SQLite to MySQL 数据迁移（更新 article_meta 表）")
print("=" * 60)

# 读取 SQLite 数据
sqlite_cursor.execute("SELECT * FROM article_meta")
rows = sqlite_cursor.fetchall()

print(f"\n📊 读取到 {len(rows)} 篇文章")

migrated_count = 0
for i, row in enumerate(rows, 1):
    try:
        print(f"\n[{i}/{len(rows)}] 迁移文章：{row['title'][:50]}...")
        
        # 转换时间戳
        created_at = convert_timestamp(row['created_at']) if row['created_at'] else None
        updated_at = convert_timestamp(row['updated_at']) if row['updated_at'] else None
        published_at = convert_timestamp(row['published_at']) if row['published_at'] else None
        
        # 更新 MySQL 的 article_meta 表
        mysql_cursor.execute("""
            UPDATE article_meta 
            SET title=%s, slug=%s, description=%s, content=%s, 
                status=%s, published_at=%s, created_at=%s, updated_at=%s
            WHERE id=%s
        """, (
            row['title'],
            row['slug'],
            row['description'] if row['description'] else None,
            row['content'] if row['content'] else None,
            row['status'] if row['status'] else 'draft',
            published_at,
            created_at,
            updated_at,
            row['id']
        ))
        
        print(f"  ✅ 更新 article_meta 表，ID={row['id']}")
        migrated_count += 1
        
    except Exception as e:
        print(f"  ❌ 失败：{e}")
        import traceback
        traceback.print_exc()

mysql_conn.commit()

# 关闭连接
sqlite_cursor.close()
sqlite_conn.close()
mysql_cursor.close()
mysql_conn.close()

print("\n" + "=" * 60)
print(f"✅ 迁移完成！更新：{migrated_count}/{len(rows)}")
print("=" * 60)
