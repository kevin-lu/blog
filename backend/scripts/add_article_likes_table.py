"""
Migration script to add article_likes table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.like import ArticleLike

def migrate():
    """Create article_likes table"""
    app = create_app()
    with app.app_context():
        print("Creating article_likes table...")
        db.create_all()
        print("Table created successfully!")
        
        # Verify table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if 'article_likes' in tables:
            print("✓ article_likes table verified")
        else:
            print("✗ article_likes table not found")

if __name__ == '__main__':
    migrate()
