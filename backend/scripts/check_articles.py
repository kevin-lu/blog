#!/usr/bin/env python3
"""Check articles in database"""
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
    
    # Check what tables exist related to articles
    cursor.execute("SHOW TABLES LIKE '%article%'")
    tables = cursor.fetchall()
    print("Article-related tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check article_meta table
    print("\n=== article_meta table ===")
    cursor.execute("SELECT COUNT(*) FROM article_meta")
    count = cursor.fetchone()[0]
    print(f"Total articles: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, title, slug, status, created_at FROM article_meta ORDER BY created_at DESC LIMIT 5")
        articles = cursor.fetchall()
        print("\nRecent articles:")
        for article in articles:
            print(f"  ID: {article[0]}, Title: {article[1]}, Slug: {article[2]}, Status: {article[3]}, Created: {article[4]}")
    
    # Check if articles table exists
    print("\n=== articles table ===")
    cursor.execute("SHOW TABLES LIKE 'articles'")
    result = cursor.fetchone()
    if result:
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        print(f"Total articles in 'articles' table: {count}")
    else:
        print("'articles' table does not exist")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if connection:
        connection.close()
