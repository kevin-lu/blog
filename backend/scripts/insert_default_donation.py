#!/usr/bin/env python3
"""Insert default donation settings"""
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
    
    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM donation_settings")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insert default data
        cursor.execute("""
            INSERT INTO donation_settings (title, description, enabled)
            VALUES (%s, %s, %s)
        """, ('支持博主', '代码编织梦想，分享传递价值\n每一分支持，都是前行的光', 1))
        connection.commit()
        print("✅ Default data inserted successfully!")
    else:
        print(f"ℹ️  Already has {count} records")
    
    # Verify
    cursor.execute("SELECT id, title, enabled FROM donation_settings")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Title: {row[1]}, Enabled: {row[2]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if connection:
        connection.close()
