#!/usr/bin/env python3
"""Check users in database"""
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
    
    # Check users table
    cursor.execute("SELECT id, username, email FROM users")
    users = cursor.fetchall()
    print(f"Users table has {len(users)} records:")
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
    
    # Check if admin2 exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ('admin2',))
    count = cursor.fetchone()[0]
    print(f"\nadmin2 exists: {count > 0}")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if connection:
        connection.close()
