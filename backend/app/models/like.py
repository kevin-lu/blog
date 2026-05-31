"""
Article Like Model
"""
from datetime import datetime
from app.extensions import db


class ArticleLike(db.Model):
    """Article Like model"""
    
    __tablename__ = 'article_likes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article_meta.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    article = db.relationship('Article', backref=db.backref('likes', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('Admin', backref=db.backref('article_likes', lazy='dynamic'))
    
    # Unique constraints
    __table_args__ = (
        db.UniqueConstraint('article_id', 'user_id', name='uq_article_user'),
        db.UniqueConstraint('article_id', 'session_id', name='uq_article_session'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'article_id': self.article_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<ArticleLike article_id={self.article_id} user_id={self.user_id}>'
