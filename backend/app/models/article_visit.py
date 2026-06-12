"""
Article Visit Model
"""
from datetime import datetime
from app.extensions import db


class ArticleVisit(db.Model):
    """Article Visit model - records each article visit with IP address"""
    
    __tablename__ = 'article_visits'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article_meta.id', ondelete='CASCADE'), nullable=False)
    article_slug = db.Column(db.String(200), nullable=False, index=True)
    ip_address = db.Column(db.String(50), nullable=False, index=True)
    user_agent = db.Column(db.String(500))
    visited_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    article = db.relationship('Article', backref=db.backref('visits', lazy='dynamic', cascade='all, delete-orphan'))
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'article_id': self.article_id,
            'article_slug': self.article_slug,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'visited_at': self.visited_at.isoformat() if self.visited_at else None,
        }
    
    def __repr__(self):
        return f'<ArticleVisit article_id={self.article_id} ip={self.ip_address}>'
