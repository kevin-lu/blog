"""
Comment Model
"""
from datetime import datetime
from app.extensions import db


class Comment(db.Model):
    """Comment model"""
    
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_slug = db.Column(db.String(200), db.ForeignKey('article_meta.slug'), nullable=False)
    github_id = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    is_pinned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'article_slug': self.article_slug,
            'github_id': self.github_id,
            'status': self.status,
            'is_pinned': bool(self.is_pinned),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Comment {self.id}>'
