#!/usr/bin/env python3
"""Check all tables in database"""
import pymysql

config = {
    'host': '114.55.165.189',
    'port': 3306,
    'user': 'root',
    'password': 'Root@123456',
    'database': 'blog_db',
    'charset': 'utf8mb4'
}

try:
    connection = pymysql.connect(**config)
    cursor = connection.cursor()
    
    # List all tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"Database has {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if connection:
        connection.close()
