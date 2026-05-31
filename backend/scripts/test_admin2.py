#!/usr/bin/env python3
"""Test admin2 password"""
import pymysql
from werkzeug.security import check_password_hash

conn = pymysql.connect(host='114.55.165.189', port=3306, user='root', password='Root@123456', database='blog_db', charset='utf8mb4')
cursor = conn.cursor()

# Get full password hash
cursor.execute('SELECT username, password_hash FROM admins WHERE username = %s', ('admin2',))
result = cursor.fetchone()
if result:
    username, password_hash = result
    print(f'Username: {username}')
    print(f'Password Hash Length: {len(password_hash)}')
    print(f'Password Hash: {password_hash}')
    
    # Test password
    test_password = 'Admin@123456'
    result = check_password_hash(password_hash, test_password)
    print(f'\nPassword check result for "Admin@123456": {result}')

conn.close()
