#!/usr/bin/env python
"""
Database Migration Script - Add Article Visits Table
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

def migrate():
    """Execute migration"""
    app = create_app('development')
    
    with app.app_context():
        # Read SQL file
        sql_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'ddl', '004_add_article_visits.sql')
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Split and execute statements
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        success_count = 0
        for statement in statements:
            if statement and not statement.startswith('DROP'):
                try:
                    db.session.execute(db.text(statement))
                    success_count += 1
                    print(f'✓ Executed statement {success_count}')
                except Exception as e:
                    print(f'✗ Error: {e}')
                    db.session.rollback()
                    return False
        
        db.session.commit()
        print(f'\n✓ Migration completed successfully! Executed {success_count} statements.')
        return True

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
