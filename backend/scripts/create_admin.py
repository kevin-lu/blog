#!/usr/bin/env python
"""
Create Admin User Script
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from app.models.admin import Admin

def create_admin(username, password, email=None):
    """Create admin user"""
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            print(f"Admin '{username}' already exists!")
            return False
        
        # Create new admin
        admin = Admin(
            username=username,
            email=email or f'{username}@example.com'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user '{username}' created successfully!")
        print(f"Email: {admin.email}")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <username> <password> [email]")
        print("Example: python create_admin.py admin admin123 admin@example.com")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    email = sys.argv[3] if len(sys.argv) > 3 else None
    
    create_admin(username, password, email)
