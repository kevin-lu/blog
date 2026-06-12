#!/usr/bin/env python3
"""Check admins table"""
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
    
    # Check admins table structure
    cursor.execute("DESCRIBE admins")
    columns = cursor.fetchall()
    print("Admins table structure:")
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    # Check admins data
    cursor.execute("SELECT id, username, email, password_hash FROM admins")
    admins = cursor.fetchall()
    print(f"\nAdmins table has {len(admins)} records:")
    for admin in admins:
        print(f"  ID: {admin[0]}, Username: {admin[1]}, Email: {admin[2]}, Password: {admin[3][:20]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if connection:
        connection.close()
