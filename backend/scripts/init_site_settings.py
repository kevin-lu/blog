#!/usr/bin/env python3
"""
初始化站点设置数据
用于云部署时自动插入默认站点设置
"""
import pymysql
import sys
import os

# 数据库配置
config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'blog_db'),
    'charset': 'utf8mb4'
}

def insert_default_settings():
    """插入默认站点设置"""
    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        print("📋 开始初始化站点设置...")
        
        # 执行 DML 脚本
        with open('database/dml/002_site_settings.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 分割 SQL 语句（按分号分隔）
        sql_statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        # 只执行 INSERT 语句
        for statement in sql_statements:
            if statement.upper().startswith('INSERT INTO site_settings'):
                cursor.execute(statement)
        
        connection.commit()
        print("✅ 站点设置初始化完成！")
        
        # 验证插入结果
        print("\n📊 当前站点设置:")
        cursor.execute("SELECT key_name, key_value, description FROM site_settings ORDER BY key_name")
        for row in cursor.fetchall():
            key_name, key_value, description = row
            # 截断过长的值
            display_value = key_value[:50] + '...' if len(key_value) > 50 else key_value
            print(f"  - {key_name}: {display_value}")
        
        # 统计设置数量
        cursor.execute("SELECT COUNT(*) FROM site_settings")
        count = cursor.fetchone()[0]
        print(f"\n总计：{count} 条设置")
        
    except FileNotFoundError:
        print("❌ 错误：找不到 DML 文件 'database/dml/002_site_settings.sql'")
        print("   请确保在 backend 目录下执行此脚本")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)
    finally:
        if connection:
            connection.close()

def update_avatar_url(avatar_url):
    """更新站点头像 URL"""
    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO site_settings (key_name, key_value, description, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            ON DUPLICATE KEY UPDATE key_value = %s, updated_at = NOW()
        """, ('site_avatar', avatar_url, '站点头像 URL', avatar_url))
        
        connection.commit()
        print(f"✅ 站点头像已更新：{avatar_url}")
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='站点设置初始化工具')
    parser.add_argument('--update-avatar', type=str, help='更新站点头像 URL')
    parser.add_argument('--init', action='store_true', help='初始化所有站点设置')
    
    args = parser.parse_args()
    
    if args.update_avatar:
        update_avatar_url(args.update_avatar)
    elif args.init:
        insert_default_settings()
    else:
        # 默认执行初始化
        insert_default_settings()
