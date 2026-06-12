#!/usr/bin/env python3
"""Check SQLite database for articles in article_meta table"""
import sqlite3

try:
    connection = sqlite3.connect('/Users/luzengbiao/traeProjects/blog/blog/blog.db')
    cursor = connection.cursor()
    
    # Check article_meta table
    print("=== article_meta table ===")
    cursor.execute("SELECT COUNT(*) FROM article_meta")
    count = cursor.fetchone()[0]
    print(f"Total articles: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, title, slug, status, created_at FROM article_meta ORDER BY created_at DESC LIMIT 5")
        articles = cursor.fetchall()
        print("\nRecent articles:")
        for article in articles:
            print(f"  ID: {article[0]}, Title: {article[1]}, Slug: {article[2]}, Status: {article[3]}, Created: {article[4]}")
    
    # Check table structure
    print("\n=== article_meta structure ===")
    cursor.execute("PRAGMA table_info(article_meta)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]}: {col[2]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if connection:
        connection.close()
