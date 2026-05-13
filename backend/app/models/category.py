"""
Category Model
"""
from datetime import datetime
from app.extensions import db


class Category(db.Model):
    """Category model"""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self, include_article_count=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_article_count:
            # 统计该分类下的文章数量
            from app.models.article import Article
            article_count = Article.query.filter(
                Article.categories.contains(self),
                Article.status == 'published'
            ).count()
            data['article_count'] = article_count
        
        return data
    
    def __repr__(self):
        return f'<Category {self.name}>'
