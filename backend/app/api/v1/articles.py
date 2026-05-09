"""
Articles API v1
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from flask_limiter import limiter
from app.extensions import db
from app.models.article import Article, ArticleCategory, ArticleTag
from app.models.category import Category
from app.models.tag import Tag
from app.utils.jwt import get_current_admin
from datetime import datetime

bp = Blueprint('articles', __name__)


@bp.route('', methods=['GET'])
@limiter.limit("30 per minute")
def get_articles():
    """
    Get articles list with pagination and filters
    
    Query Parameters:
        page: Page number (default: 1)
        limit: Items per page (default: 10)
        category: Filter by category slug
        tag: Filter by tag slug
        status: Filter by status (published, draft, archived)
        search: Search in title and description
    
    Returns:
        {
            "articles": [...],
            "total": 100,
            "page": 1,
            "limit": 10,
            "pages": 10
        }
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    category = request.args.get('category')
    tag = request.args.get('tag')
    status = request.args.get('status', 'published')
    search = request.args.get('search')
    
    # Build query
    query = Article.query
    
    # Filter by status
    if status:
        query = query.filter_by(status=status)
    
    # Filter by category
    if category:
        cat = Category.query.filter_by(slug=category).first()
        if cat:
            query = query.filter(Article.categories.contains(cat))
    
    # Filter by tag
    if tag:
        t = Tag.query.filter_by(slug=tag).first()
        if t:
            query = query.filter(Article.tags.contains(t))
    
    # Search
    if search:
        query = query.filter(
            db.or_(
                Article.title.ilike(f'%{search}%'),
                Article.description.ilike(f'%{search}%')
            )
        )
    
    # Order by published_at desc
    query = query.order_by(Article.published_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    articles = pagination.items
    
    return jsonify({
        'articles': [article.to_dict() for article in articles],
        'total': pagination.total,
        'page': page,
        'limit': limit,
        'pages': pagination.pages
    }), 200


@bp.route('/<slug>', methods=['GET'])
@limiter.limit("30 per minute")
def get_article(slug):
    """
    Get article by slug
    
    Returns:
        {
            "article": { ...article data... }
        }
    """
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()
    
    return jsonify({
        'article': article.to_dict()
    }), 200


@bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_article():
    """
    Create new article (requires authentication)
    
    Request JSON:
        {
            "title": "Article title",
            "slug": "article-slug",
            "description": "Article description",
            "cover_image": "cover image url",
            "category_ids": [1, 2],
            "tag_ids": [3, 4]
        }
    
    Returns:
        {
            "article": { ...created article... }
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    # Validate required fields
    if not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    # Check if slug already exists
    if Article.query.filter_by(slug=data.get('slug')).first():
        return jsonify({'error': 'Slug already exists'}), 400
    
    # Create article
    article = Article(
        slug=data.get('slug'),
        title=data.get('title'),
        description=data.get('description'),
        cover_image=data.get('cover_image'),
        status=data.get('status', 'draft'),
        published_at=datetime.utcnow() if data.get('status') == 'published' else None
    )
    
    # Set categories
    if data.get('category_ids'):
        categories = Category.query.filter(Category.id.in_(data['category_ids'])).all()
        article.categories = categories
    
    # Set tags
    if data.get('tag_ids'):
        tags = Tag.query.filter(Tag.id.in_(data['tag_ids'])).all()
        article.tags = tags
    
    db.session.add(article)
    db.session.commit()
    
    return jsonify({
        'article': article.to_dict()
    }), 201


@bp.route('/<slug>', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per hour")
def update_article(slug):
    """
    Update article (requires authentication)
    
    Request JSON:
        {
            "title": "Updated title",
            "description": "Updated description",
            "cover_image": "updated cover image",
            "status": "published",
            "category_ids": [1, 2],
            "tag_ids": [3, 4]
        }
    
    Returns:
        {
            "article": { ...updated article... }
        }
    """
    article = Article.query.filter_by(slug=slug).first_or_404()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    # Update fields
    if 'title' in data:
        article.title = data['title']
    if 'description' in data:
        article.description = data['description']
    if 'cover_image' in data:
        article.cover_image = data['cover_image']
    if 'status' in data:
        article.status = data['status']
        if data['status'] == 'published' and not article.published_at:
            article.published_at = datetime.utcnow()
    
    # Update categories
    if 'category_ids' in data:
        categories = Category.query.filter(Category.id.in_(data['category_ids'])).all()
        article.categories = categories
    
    # Update tags
    if 'tag_ids' in data:
        tags = Tag.query.filter(Tag.id.in_(data['tag_ids'])).all()
        article.tags = tags
    
    article.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'article': article.to_dict()
    }), 200


@bp.route('/<slug>', methods=['DELETE'])
@jwt_required()
@limiter.limit("5 per hour")
def delete_article(slug):
    """
    Delete article (requires authentication)
    
    Returns:
        {
            "message": "Article deleted successfully"
        }
    """
    article = Article.query.filter_by(slug=slug).first_or_404()
    
    db.session.delete(article)
    db.session.commit()
    
    return jsonify({
        'message': 'Article deleted successfully'
    }), 200
