#!/usr/bin/env python3
"""Check SQLite database for articles"""
import sqlite3

try:
    connection = sqlite3.connect('/Users/luzengbiao/traeProjects/blog/blog/blog.db')
    cursor = connection.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("SQLite tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check if articles table exists
    print("\n=== articles table ===")
    cursor.execute("SELECT COUNT(*) FROM articles")
    count = cursor.fetchone()[0]
    print(f"Total articles: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, title, slug, status, created_at FROM articles ORDER BY created_at DESC LIMIT 5")
        articles = cursor.fetchall()
        print("\nRecent articles:")
        for article in articles:
            print(f"  ID: {article[0]}, Title: {article[1]}, Slug: {article[2]}, Status: {article[3]}, Created: {article[4]}")
    
    # Check article_content table
    print("\n=== article_content table ===")
    cursor.execute("SELECT COUNT(*) FROM article_content")
    count = cursor.fetchone()[0]
    print(f"Total article_content records: {count}")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if connection:
        connection.close()
