"""
Database Migration Script
Migrate data from old Drizzle ORM database to new SQLAlchemy database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import create_app
from app.extensions import db
from app.models.admin import Admin
from app.models.article import Article, ArticleCategory, ArticleTag
from app.models.category import Category
from app.models.tag import Tag
from app.models.comment import Comment
from app.models.site_setting import SiteSetting
from app.models.operation_log import OperationLog
import json
from datetime import datetime


def export_old_data():
    """Export data from old database to JSON"""
    # This would connect to the old database and export data
    # For now, we'll create a template
    print("Exporting old data...")
    
    # TODO: Implement actual export logic
    # This is a placeholder for the export structure
    export_data = {
        'admins': [],
        'articles': [],
        'categories': [],
        'tags': [],
        'comments': [],
        'site_settings': [],
        'operation_logs': []
    }
    
    return export_data


def import_new_data(data):
    """Import data to new database"""
    print("Importing data to new database...")
    
    # Import admins
    for admin_data in data.get('admins', []):
        admin = Admin(
            id=admin_data.get('id'),
            username=admin_data.get('username'),
            password_hash=admin_data.get('password_hash'),
            email=admin_data.get('email'),
            avatar=admin_data.get('avatar'),
            role=admin_data.get('role', 'admin'),
            created_at=datetime.fromisoformat(admin_data['created_at']) if admin_data.get('created_at') else None,
        )
        db.session.add(admin)
    
    # Import categories
    for category_data in data.get('categories', []):
        category = Category(
            id=category_data.get('id'),
            name=category_data.get('name'),
            slug=category_data.get('slug'),
            description=category_data.get('description'),
            parent_id=category_data.get('parent_id'),
            sort_order=category_data.get('sort_order', 0),
            created_at=datetime.fromisoformat(category_data['created_at']) if category_data.get('created_at') else None,
        )
        db.session.add(category)
    
    # Import tags
    for tag_data in data.get('tags', []):
        tag = Tag(
            id=tag_data.get('id'),
            name=tag_data.get('name'),
            slug=tag_data.get('slug'),
            created_at=datetime.fromisoformat(tag_data['created_at']) if tag_data.get('created_at') else None,
        )
        db.session.add(tag)
    
    # Import articles
    for article_data in data.get('articles', []):
        article = Article(
            id=article_data.get('id'),
            slug=article_data.get('slug'),
            title=article_data.get('title'),
            description=article_data.get('description'),
            cover_image=article_data.get('cover_image'),
            status=article_data.get('status', 'draft'),
            published_at=datetime.fromisoformat(article_data['published_at']) if article_data.get('published_at') else None,
            created_at=datetime.fromisoformat(article_data['created_at']) if article_data.get('created_at') else None,
        )
        db.session.add(article)
    
    # Import comments
    for comment_data in data.get('comments', []):
        comment = Comment(
            id=comment_data.get('id'),
            article_slug=comment_data.get('article_slug'),
            github_id=comment_data.get('github_id'),
            status=comment_data.get('status', 'pending'),
            is_pinned=comment_data.get('is_pinned', 0),
            created_at=datetime.fromisoformat(comment_data['created_at']) if comment_data.get('created_at') else None,
        )
        db.session.add(comment)
    
    # Import site settings
    for setting_data in data.get('site_settings', []):
        setting = SiteSetting(
            id=setting_data.get('id'),
            key_name=setting_data.get('key_name'),
            key_value=setting_data.get('key_value'),
            description=setting_data.get('description'),
            created_at=datetime.fromisoformat(setting_data['created_at']) if setting_data.get('created_at') else None,
        )
        db.session.add(setting)
    
    db.session.commit()
    print("Data import completed!")


def migrate():
    """Main migration function"""
    app = create_app()
    
    with app.app_context():
        # Export old data
        old_data = export_old_data()
        
        # Save to JSON file for backup
        with open('data_export.json', 'w', encoding='utf-8') as f:
            json.dump(old_data, f, ensure_ascii=False, indent=2)
        
        print(f"Exported data to data_export.json")
        
        # Import to new database
        import_new_data(old_data)
        
        print("Migration completed successfully!")


if __name__ == '__main__':
    migrate()
