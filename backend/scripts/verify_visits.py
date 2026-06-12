#!/usr/bin/env python
"""
Verify Article Visits Table
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

def verify():
    """Verify table exists"""
    app = create_app('development')
    
    with app.app_context():
        try:
            result = db.session.execute(db.text("SHOW TABLES LIKE 'article_visits'"))
            if result.fetchone():
                print('✓ Table article_visits exists')
                
                # Show table structure
                result = db.session.execute(db.text("DESCRIBE article_visits"))
                print('\nTable structure:')
                for row in result:
                    print(f'  {row[0]}: {row[1]}')
                
                return True
            else:
                print('✗ Table article_visits not found')
                return False
        except Exception as e:
            print(f'✗ Error: {e}')
            return False

if __name__ == '__main__':
    success = verify()
    sys.exit(0 if success else 1)
