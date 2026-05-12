#!/usr/bin/env python3
"""
SQLite to MySQL 数据迁移脚本
将旧 SQLite 数据库的所有数据迁移到 MySQL 8
"""
import sqlite3
import pymysql
from datetime import datetime
import sys
import os

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


def get_sqlite_data(table):
    """从 SQLite 读取数据"""
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    
    # 获取列名
    columns = [description[0] for description in cursor.description]
    conn.close()
    
    return columns, rows


def insert_to_mysql(mysql_conn, table, columns, rows):
    """插入数据到 MySQL"""
    cursor = mysql_conn.cursor()
    
    # 构建 INSERT 语句
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join([f"`{col}`" for col in columns])
    insert_sql = f"INSERT INTO `{table}` ({columns_str}) VALUES ({placeholders})"
    
    count = 0
    for row in rows:
        try:
            # 转换数据
            values = []
            for value in row:
                if isinstance(value, bytes):
                    value = value.decode('utf-8', errors='ignore')
                elif isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, (int, float)) and len(str(value)) > 10 and str(value).isdigit():
                    # SQLite 时间戳可能是毫秒级整数
                    value = datetime.fromtimestamp(int(value) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                values.append(value)
            
            cursor.execute(insert_sql, values)
            count += 1
        except Exception as e:
            print(f"  ⚠️  插入失败：{e}")
            continue
    
    mysql_conn.commit()
    cursor.close()
    return count


def migrate_table(mysql_conn, table, ignore_fields=None):
    """迁移单个表"""
    print(f"\n📊 迁移表：{table}")
    
    if ignore_fields is None:
        ignore_fields = []
    
    try:
        columns, rows = get_sqlite_data(table)
        
        # 过滤忽略的字段
        if ignore_fields:
            filtered_columns = []
            filtered_rows = []
            for i, col in enumerate(columns):
                if col not in ignore_fields:
                    filtered_columns.append(col)
                    filtered_rows.append([row[i] for row in rows])
            
            # 转置行数据
            filtered_rows = list(zip(*filtered_rows)) if filtered_rows else []
            columns = filtered_columns
            rows = filtered_rows
        
        print(f"  读取到 {len(rows)} 条记录")
        
        if len(rows) > 0:
            count = insert_to_mysql(mysql_conn, table, columns, rows)
            print(f"  ✅ 成功插入 {count} 条记录")
        else:
            print(f"  ℹ️  表为空，跳过")
            
    except Exception as e:
        print(f"  ❌ 迁移失败：{e}")


def main():
    """主函数"""
    print("=" * 60)
    print("SQLite to MySQL 数据迁移工具")
    print("=" * 60)
    print(f"\nSQLite 数据库：{SQLITE_DB}")
    print(f"MySQL 数据库：{MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")
    
    # 连接 MySQL
    print("\n📡 连接 MySQL...")
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        print("✅ MySQL 连接成功")
    except Exception as e:
        print(f"❌ MySQL 连接失败：{e}")
        sys.exit(1)
    
    # 要迁移的表
    tables_to_migrate = [
        'admins',
        'article_meta',
        'categories',
        'tags',
        'article_tags',
        'article_categories',
        'comments',
        'site_settings',
        'operation_logs'
    ]
    
    # 需要忽略的字段（SQLite 特有或 MySQL 会自动生成的字段）
    ignore_fields_map = {
        'admins': ['id'],  # MySQL 会自增
        'article_meta': ['id'],
        'categories': ['id'],
        'tags': ['id'],
        'article_tags': [],
        'article_categories': [],
        'comments': ['id'],
        'site_settings': ['id'],
        'operation_logs': ['id']
    }
    
    # 执行迁移
    for table in tables_to_migrate:
        ignore_fields = ignore_fields_map.get(table, [])
        migrate_table(mysql_conn, table, ignore_fields)
    
    # 关闭连接
    mysql_conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 数据迁移完成！")
    print("=" * 60)
    
    # 验证数据
    print("\n📊 数据验证:")
    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = mysql_conn.cursor()
    
    for table in tables_to_migrate:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条记录")
        except:
            print(f"  {table}: 表不存在")
    
    cursor.close()
    mysql_conn.close()


if __name__ == '__main__':
    main()
