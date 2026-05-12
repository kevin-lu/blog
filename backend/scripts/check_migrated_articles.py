#!/usr/bin/env python3
"""Check migrated articles"""
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
    
    cursor.execute("SELECT id, title, status, published_at FROM article_meta ORDER BY created_at DESC")
    articles = cursor.fetchall()
    print(f"Total articles: {len(articles)}")
    print("\nAll articles:")
    for article in articles:
        print(f"  ID: {article[0]}, Title: {article[1][:50]}..., Status: {article[2]}, Published: {article[3]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if connection:
        connection.close()
