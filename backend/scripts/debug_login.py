#!/usr/bin/env python3
"""Debug admin2 login"""
import sys
sys.path.insert(0, '/Users/luzengbiao/traeProjects/blog/blog/backend')

from app import create_app
from app.extensions import db
from app.models.admin import Admin

app = create_app('development')

with app.app_context():
    # Find admin
    admin = Admin.query.filter_by(username='admin2').first()
    
    if not admin:
        print('❌ Admin not found in database')
        sys.exit(1)
    
    print(f'✅ Admin found: ID={admin.id}, Username={admin.username}')
    print(f'Password Hash: {admin.password_hash[:50]}...')
    print(f'Password Hash Length: {len(admin.password_hash)}')
    
    # Test password
    password = 'Admin@123456'
    result = admin.check_password(password)
    print(f'\nPassword check result: {result}')
    
    if not result:
        # Check hash prefix
        BCRYPT_PREFIXES = ('$2a$', '$2b$', '$2y$')
        print(f'\nHash starts with bcrypt prefix: {admin.password_hash.startswith(BCRYPT_PREFIXES)}')
        print(f'Hash starts with pbkdf2: {admin.password_hash.startswith("pbkdf2:")}')
