#!/usr/bin/env python3
"""
SQLite to MySQL 数据迁移脚本（最终版）
将 SQLite 的 article_meta 数据迁移到 MySQL 的 articles 和 article_meta 表
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


def generate_slug(title):
    """从标题生成 slug"""
    # 简单处理：移除特殊字符，替换空格为连字符
    slug = title.lower()
    slug = ''.join(c if c.isalnum() or c in ' -_' else '' for c in slug)
    slug = slug.replace(' ', '-').replace('_', '-')
    # 截断到合理长度
    return slug[:200] if len(slug) > 200 else slug


# 连接 SQLite
sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# 连接 MySQL
mysql_conn = pymysql.connect(**MYSQL_CONFIG)
mysql_cursor = mysql_conn.cursor()

print("=" * 60)
print("SQLite to MySQL 数据迁移（文章数据）")
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
        
        # 生成 slug（如果原 slug 太长或格式不对）
        slug = row['slug']
        if not slug or len(slug) > 200:
            slug = generate_slug(row['title'])
        
        # 确保 slug 唯一
        mysql_cursor.execute("SELECT COUNT(*) FROM articles WHERE slug = %s", (slug,))
        if mysql_cursor.fetchone()[0] > 0:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
            print(f"  ⚠️  slug 重复，使用新 slug: {slug}")
        
        # 插入 articles 表
        mysql_cursor.execute("""
            INSERT INTO articles 
            (title, slug, summary, content, status, created_at, updated_at, published_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['title'],
            slug,
            row['description'] if row['description'] else None,
            row['content'] if row['content'] else None,
            row['status'] if row['status'] else 'draft',
            created_at,
            updated_at,
            published_at
        ))
        
        article_id = mysql_cursor.lastrowid
        print(f"  ✅ 插入 articles 表，ID={article_id}")
        
        # 插入 article_meta 表（view_count 默认为 0）
        view_count = 0  # SQLite 的 article_meta 没有 view_count 字段，使用默认值
            
        mysql_cursor.execute("""
            INSERT INTO article_meta (article_id, view_count)
            VALUES (%s, %s)
        """, (article_id, view_count))
        
        print(f"  ✅ 插入 article_meta 表，views={view_count}")
        migrated_count += 1
        
    except Exception as e:
        print(f"  ❌ 失败：{e}")
        import traceback
        traceback.print_exc()

mysql_conn.commit()

# 迁移 categories
print("\n" + "=" * 60)
print("迁移分类数据...")
print("=" * 60)

sqlite_cursor.execute("SELECT * FROM categories")
categories = sqlite_cursor.fetchall()

cat_count = 0
for row in categories:
    try:
        created_at = convert_timestamp(row['created_at']) if row['created_at'] else None
        updated_at = convert_timestamp(row['updated_at']) if row['updated_at'] else None
        
        mysql_cursor.execute("""
            INSERT INTO categories 
            (id, name, slug, description, parent_id, sort_order, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['id'], row['name'], row['slug'], row['description'] if row['description'] else None,
            row['parent_id'] if row['parent_id'] else None, row['sort_order'] if row['sort_order'] else 0,
            created_at, updated_at
        ))
        print(f"  ✅ 迁移分类：{row['name']}")
        cat_count += 1
    except Exception as e:
        print(f"  ⚠️  失败：{e}")

mysql_conn.commit()

# 迁移 tags
print("\n迁移标签数据...")
sqlite_cursor.execute("SELECT * FROM tags")
tags = sqlite_cursor.fetchall()

tag_count = 0
for row in tags:
    try:
        created_at = convert_timestamp(row['created_at']) if row['created_at'] else None
        updated_at = convert_timestamp(row['updated_at']) if row['updated_at'] else None
        
        mysql_cursor.execute("""
            INSERT INTO tags 
            (id, name, slug, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s)
        """, (
            row['id'], row['name'], row['slug'],
            created_at, updated_at
        ))
        print(f"  ✅ 迁移标签：{row['name']}")
        tag_count += 1
    except Exception as e:
        print(f"  ⚠️  失败：{e}")

mysql_conn.commit()

# 迁移 admins
print("\n迁移管理员数据...")
sqlite_cursor.execute("SELECT * FROM admins")
admins = sqlite_cursor.fetchall()

admin_count = 0
for row in admins:
    try:
        email = row['email'] if row['email'] else f"{row['username']}@admin.com"
        created_at = row['created_at'] if row['created_at'] else None
        updated_at = row['updated_at'] if row['updated_at'] else None
        
        mysql_cursor.execute("""
            INSERT INTO users 
            (username, email, password_hash, is_admin, is_active, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row['username'],
            email,
            row['password_hash'],
            True,  # is_admin
            True,  # is_active
            created_at,
            updated_at
        ))
        print(f"  ✅ 迁移管理员：{row['username']}")
        admin_count += 1
    except Exception as e:
        print(f"  ⚠️  失败：{e}")

mysql_conn.commit()

# 关闭连接
sqlite_cursor.close()
sqlite_conn.close()
mysql_cursor.close()
mysql_conn.close()

print("\n" + "=" * 60)
print("✅ 迁移完成！")
print(f"   - 文章：{migrated_count}/{len(rows)}")
print(f"   - 分类：{cat_count}/{len(categories)}")
print(f"   - 标签：{tag_count}/{len(tags)}")
print(f"   - 管理员：{admin_count}/{len(admins)}")
print("=" * 60)
