#!/usr/bin/env python
"""
Add comment fields migration
添加评论系统所需字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        # 添加 content 字段
        db.session.execute(text(
            "ALTER TABLE comments ADD COLUMN content TEXT"
        ))
        
        # 添加 author_name 字段
        db.session.execute(text(
            "ALTER TABLE comments ADD COLUMN author_name VARCHAR(100)"
        ))
        
        # 添加 author_email 字段
        db.session.execute(text(
            "ALTER TABLE comments ADD COLUMN author_email VARCHAR(100)"
        ))
        
        # 添加 parent_id 字段（回复关系）
        db.session.execute(text(
            "ALTER TABLE comments ADD COLUMN parent_id INTEGER"
        ))
        
        # 添加 reply_to 字段
        db.session.execute(text(
            "ALTER TABLE comments ADD COLUMN reply_to VARCHAR(100)"
        ))
        
        # 添加 parent_id 索引
        db.session.execute(text(
            "CREATE INDEX idx_comments_parent_id ON comments(parent_id)"
        ))
        
        db.session.commit()
        print("✅ 数据库迁移完成")

if __name__ == '__main__':
    migrate()
