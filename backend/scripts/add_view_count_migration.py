"""
Migration: Add view_count to articles
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.extensions import db
from app import create_app


def upgrade():
    """Add view_count field to article_meta table"""
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            # Check if column exists
            inspector = db.inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('article_meta')]
            
            if 'view_count' not in columns:
                conn.execute(db.text(
                    "ALTER TABLE article_meta ADD COLUMN view_count INTEGER DEFAULT 0 NOT NULL"
                ))
                conn.execute(db.text(
                    "CREATE INDEX idx_article_view_count ON article_meta(view_count)"
                ))
                conn.commit()
                print("✓ view_count 字段添加成功")
            else:
                print("✓ view_count 字段已存在")


def downgrade():
    """Remove view_count field from article_meta table"""
    app = create_app()
    with app.app_context():
        with db.engine.connect() as conn:
            conn.execute(db.text(
                "ALTER TABLE article_meta DROP COLUMN view_count"
            ))
            conn.commit()
            print("✓ view_count 字段已移除")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--downgrade':
        downgrade()
    else:
        upgrade()
