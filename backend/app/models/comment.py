"""Comment Model"""
from datetime import datetime
from app.extensions import db


class Comment(db.Model):
    """Comment model"""
    
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_slug = db.Column(db.String(200), db.ForeignKey('article_meta.slug'), nullable=False)
    content = db.Column(db.Text)  # 评论内容
    author_name = db.Column(db.String(100))  # 作者名称
    author_email = db.Column(db.String(100))  # 作者邮箱
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # 父评论 ID
    reply_to = db.Column(db.String(100))  # 回复对象名称
    github_id = db.Column(db.String(50))
    status = db.Column(db.String(20), default='approved')  # 默认自动通过
    is_pinned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 自引用关系
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy='dynamic'))
    
    def to_dict(self, include_replies=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'article_slug': self.article_slug,
            'content': self.content,
            'author_name': self.author_name,
            'author_email': self.author_email,
            'parent_id': self.parent_id,
            'reply_to': self.reply_to,
            'github_id': self.github_id,
            'status': self.status,
            'is_pinned': bool(self.is_pinned),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_replies and hasattr(self, 'replies'):
            data['replies'] = [reply.to_dict(include_replies=False) for reply in self.replies]
        
        return data
    
    def __repr__(self):
        return f'<Comment {self.id} for {self.article_slug}>'
