"""
Article Model
"""
from datetime import datetime
from app.extensions import db


class Article(db.Model):
    """Article model"""
    
    __tablename__ = 'article_meta'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    source_url = db.Column(db.Text)
    ai_generated = db.Column(db.Integer, default=0)
    ai_model = db.Column(db.String(100))
    rewrite_strategy = db.Column(db.String(20))
    template_type = db.Column(db.String(20))
    word_count = db.Column(db.Integer)
    auto_published = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = db.relationship(
        'Category',
        secondary='article_categories',
        backref='articles',
        lazy='dynamic'
    )
    tags = db.relationship(
        'Tag',
        secondary='article_tags',
        backref='articles',
        lazy='dynamic'
    )
    comments = db.relationship('Comment', backref='article', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_content=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'description': self.description,
            'cover_image': self.cover_image,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'categories': [c.to_dict() for c in self.categories],
            'tags': [t.to_dict() for t in self.tags],
        }
        if include_content:
            data.update({
                'content': self.content or '',
                'source_url': self.source_url,
                'ai_generated': bool(self.ai_generated),
                'ai_model': self.ai_model,
                'rewrite_strategy': self.rewrite_strategy,
                'template_type': self.template_type,
                'word_count': self.word_count,
                'auto_published': bool(self.auto_published),
            })
        return data
    
    def __repr__(self):
        return f'<Article {self.title}>'


class ArticleCategory(db.Model):
    """Article-Category association table"""
    
    __tablename__ = 'article_categories'
    
    article_id = db.Column(db.Integer, db.ForeignKey('article_meta.id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)


class ArticleTag(db.Model):
    """Article-Tag association table"""
    
    __tablename__ = 'article_tags'
    
    article_id = db.Column(db.Integer, db.ForeignKey('article_meta.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
