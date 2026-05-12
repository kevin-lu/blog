#!/usr/bin/env python3
"""Create admin user"""
import pymysql
from werkzeug.security import generate_password_hash

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
    
    # Check if admin2 exists
    cursor.execute("SELECT COUNT(*) FROM admins WHERE username = %s", ('admin2',))
    count = cursor.fetchone()[0]
    
    if count > 0:
        print("ℹ️  admin2 already exists, deleting...")
        cursor.execute("DELETE FROM admins WHERE username = %s", ('admin2',))
        connection.commit()
    
    # Create admin2
    password_hash = generate_password_hash('Admin@123456')
    cursor.execute("""
        INSERT INTO admins (username, password_hash, email, role, created_at, updated_at)
        VALUES (%s, %s, %s, %s, NOW(), NOW())
    """, ('admin2', password_hash, 'admin@example.com', 'admin'))
    connection.commit()
    
    print("✅ Admin user 'admin2' created successfully!")
    print("Username: admin2")
    print("Password: Admin@123456")
    
    # Verify
    cursor.execute("SELECT id, username, email FROM admins WHERE username = 'admin2'")
    admin = cursor.fetchone()
    if admin:
        print(f"\nVerified: ID={admin[0]}, Username={admin[1]}, Email={admin[2]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if connection:
        connection.close()
