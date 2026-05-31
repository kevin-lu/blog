#!/usr/bin/env python3
"""Migrate articles from SQLite to MySQL"""
import sqlite3
import pymysql
from datetime import datetime

# SQLite connection
sqlite_conn = sqlite3.connect('/Users/luzengbiao/traeProjects/blog/blog/blog.db')
sqlite_cursor = sqlite_conn.cursor()

# MySQL connection
mysql_config = {
    'host': '114.55.165.189',
    'port': 3306,
    'user': 'root',
    'password': 'Root@123456',
    'database': 'blog_db',
    'charset': 'utf8mb4'
}
mysql_conn = pymysql.connect(**mysql_config)
mysql_cursor = mysql_conn.cursor()

try:
    # Get articles from SQLite
    sqlite_cursor.execute("SELECT * FROM article_meta")
    articles = sqlite_cursor.fetchall()
    
    print(f"Found {len(articles)} articles in SQLite")
    
    # Get column names
    sqlite_cursor.execute("PRAGMA table_info(article_meta)")
    columns = [col[1] for col in sqlite_cursor.fetchall()]
    print(f"Columns: {columns}")
    
    # Migrate each article
    for article in articles:
        # Convert to dict
        article_dict = dict(zip(columns, article))
        
        # Convert timestamps
        created_at = article_dict.get('created_at')
        if created_at and isinstance(created_at, (int, float)):
            # Handle milliseconds timestamp
            if created_at > 1e12:  # milliseconds
                created_at = datetime.fromtimestamp(created_at / 1000)
            else:  # seconds
                created_at = datetime.fromtimestamp(created_at)
        elif created_at and isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except:
                created_at = datetime.now()
        else:
            created_at = datetime.now()
        
        updated_at = article_dict.get('updated_at')
        if updated_at and isinstance(updated_at, (int, float)):
            if updated_at > 1e12:
                updated_at = datetime.fromtimestamp(updated_at / 1000)
            else:
                updated_at = datetime.fromtimestamp(updated_at)
        elif updated_at and isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at)
            except:
                updated_at = created_at
        else:
            updated_at = created_at
        
        published_at = article_dict.get('published_at')
        if published_at:
            if isinstance(published_at, (int, float)):
                if published_at > 1e12:
                    published_at = datetime.fromtimestamp(published_at / 1000)
                else:
                    published_at = datetime.fromtimestamp(published_at)
            elif isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at)
                except:
                    published_at = None
        
        # Check if article already exists
        mysql_cursor.execute("SELECT COUNT(*) FROM article_meta WHERE slug = %s", (article_dict['slug'],))
        if mysql_cursor.fetchone()[0] > 0:
            print(f"⏭️  Article '{article_dict['title']}' already exists, skipping...")
            continue
        
        # Insert into MySQL
        mysql_cursor.execute("""
            INSERT INTO article_meta (
                slug, title, description, content, cover_image, source_url,
                ai_generated, ai_model, rewrite_strategy, template_type, word_count,
                auto_published, status, published_at, created_at, updated_at, view_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            article_dict.get('slug'),
            article_dict.get('title'),
            article_dict.get('description'),
            article_dict.get('content'),
            article_dict.get('cover_image'),
            article_dict.get('source_url'),
            article_dict.get('ai_generated', 0),
            article_dict.get('ai_model'),
            article_dict.get('rewrite_strategy'),
            article_dict.get('template_type'),
            article_dict.get('word_count'),
            article_dict.get('auto_published', 0),
            article_dict.get('status', 'draft'),
            published_at,
            created_at,
            updated_at,
            0  # view_count
        ))
        
        print(f"✅ Migrated: {article_dict['title']}")
    
    mysql_conn.commit()
    print(f"\n✅ Migration completed!")
    
    # Verify
    mysql_cursor.execute("SELECT COUNT(*) FROM article_meta")
    count = mysql_cursor.fetchone()[0]
    print(f"Total articles in MySQL: {count}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    mysql_conn.rollback()
finally:
    sqlite_conn.close()
    mysql_conn.close()
