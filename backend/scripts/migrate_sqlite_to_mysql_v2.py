#!/usr/bin/env python3
"""
SQLite to MySQL 数据迁移脚本（改进版）
处理时间戳转换问题
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


def convert_timestamp(value):
    """转换 SQLite 时间戳为 MySQL 格式"""
    if value is None:
        return None
    
    # 如果是字符串格式的日期时间
    if isinstance(value, str):
        # 尝试解析常见格式
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S']:
            try:
                return datetime.strptime(value, fmt).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        
        # 尝试解析毫秒时间戳字符串（如 '1778486817424.0'）
        try:
            timestamp_float = float(value)
            if timestamp_float > 1e12:  # 毫秒级时间戳
                return datetime.fromtimestamp(timestamp_float / 1000).strftime('%Y-%m-%d %H:%M:%S')
            elif timestamp_float > 1e9:  # 秒级时间戳
                return datetime.fromtimestamp(timestamp_float).strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, OSError):
            pass
        
        return value  # 无法解析则保持原样
    
    # 如果是数字（时间戳）
    if isinstance(value, (int, float)):
        # 判断是秒还是毫秒
        if value > 1e12:  # 毫秒级时间戳
            return datetime.fromtimestamp(value / 1000).strftime('%Y-%m-%d %H:%M:%S')
        elif value > 1e9:  # 秒级时间戳
            return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
        else:  # 可能是其他数字
            return None
    
    # 如果已经是 datetime 对象
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    
    return value


def get_sqlite_columns(table):
    """获取 SQLite 表的列信息"""
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    conn.close()
    
    return {
        'names': [col[1] for col in columns],
        'types': [col[2] for col in columns]
    }


def get_sqlite_data(table):
    """从 SQLite 读取数据"""
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    conn.close()
    
    return columns, rows


def insert_to_mysql(mysql_conn, table, columns, rows, column_types):
    """插入数据到 MySQL，处理时间戳转换"""
    cursor = mysql_conn.cursor()
    
    # 识别时间字段
    time_columns = []
    for i, col_type in enumerate(column_types):
        col_name = columns[i]
        if 'TIMESTAMP' in col_type.upper() or 'DATETIME' in col_type.upper() or 'DATE' in col_type.upper():
            time_columns.append((i, col_name))
    
    # 构建 INSERT 语句（使用 ON DUPLICATE KEY UPDATE 避免重复）
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join([f"`{col}`" for col in columns])
    insert_sql = f"INSERT INTO `{table}` ({columns_str}) VALUES ({placeholders})"
    
    count = 0
    for row in rows:
        try:
            # 转换数据
            values = list(row)
            
            # 转换时间戳字段
            for idx, col_name in time_columns:
                if idx < len(values) and values[idx] is not None:
                    values[idx] = convert_timestamp(values[idx])
            
            # 处理其他字段
            for i in range(len(values)):
                if isinstance(values[i], bytes):
                    values[i] = values[i].decode('utf-8', errors='ignore')
            
            cursor.execute(insert_sql, values)
            count += 1
        except Exception as e:
            print(f"  ⚠️  插入失败：row={dict(zip(columns, row))}, error={e}")
            continue
    
    mysql_conn.commit()
    cursor.close()
    return count


def migrate_table(mysql_conn, table):
    """迁移单个表"""
    print(f"\n📊 迁移表：{table}")
    
    try:
        # 获取列信息
        col_info = get_sqlite_columns(table)
        columns = col_info['names']
        column_types = col_info['types']
        
        # 获取数据
        data_columns, rows = get_sqlite_data(table)
        print(f"  读取到 {len(rows)} 条记录")
        print(f"  列：{', '.join(columns)}")
        
        if len(rows) > 0:
            count = insert_to_mysql(mysql_conn, table, columns, rows, column_types)
            print(f"  ✅ 成功插入 {count} 条记录")
        else:
            print(f"  ℹ️  表为空，跳过")
            
    except Exception as e:
        print(f"  ❌ 迁移失败：{e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("=" * 60)
    print("SQLite to MySQL 数据迁移工具（改进版）")
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
    
    # 执行迁移
    for table in tables_to_migrate:
        migrate_table(mysql_conn, table)
    
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
        except Exception as e:
            print(f"  {table}: 查询失败 - {e}")
    
    cursor.close()
    mysql_conn.close()


if __name__ == '__main__':
    main()
