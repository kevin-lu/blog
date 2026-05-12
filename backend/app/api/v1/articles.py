"""
Articles API v1
"""
import threading
from datetime import datetime, timezone
from html import unescape
import re

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, verify_jwt_in_request, get_jwt_identity
from app.extensions import db, limiter
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag
from app.services.ai_rewrite import slugify, process_rewrite_task
from app.services.ai_tasks import create_task, get_task, list_tasks, clear_finished_tasks

bp = Blueprint('articles', __name__)


def parse_datetime_value(value):
    """Parse ISO strings or timestamps into naive UTC datetimes."""
    if value in (None, ''):
        return None
    if isinstance(value, (int, float)):
        timestamp = value / 1000 if value > 10_000_000_000 else value
        return datetime.utcfromtimestamp(timestamp)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        try:
            if normalized.endswith('Z'):
                normalized = normalized[:-1] + '+00:00'
            parsed = datetime.fromisoformat(normalized)
            if parsed.tzinfo:
                return parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return parsed
        except ValueError:
            return None
    return None


def summarize_description(content, fallback='', limit=200):
    if fallback:
        return fallback[:limit]
    text = re.sub(r'<[^>]+>', ' ', content or '')
    text = unescape(re.sub(r'\s+', ' ', text)).strip()
    return text[:limit]


def build_article_slug(raw_slug, title, existing_article=None):
    base = slugify(raw_slug or title or '') or 'article'
    candidate = base
    counter = 1
    while True:
        found = Article.query.filter_by(slug=candidate).first()
        if not found or (existing_article and found.id == existing_article.id):
            return candidate
        counter += 1
        candidate = f'{base}-{counter}'


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
    order_by = request.args.get('order_by', 'published_at')
    order_dir = request.args.get('order_dir', 'desc')
    
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
    
    # Order by field
    order_map = {
        'published_at': Article.published_at,
        'view_count': Article.view_count,
        'created_at': Article.created_at,
    }
    order_field = order_map.get(order_by, Article.published_at)
    if order_dir == 'asc':
        query = query.order_by(order_field.asc())
    else:
        query = query.order_by(order_field.desc())
    
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
    is_admin_request = False
    try:
        verify_jwt_in_request(optional=True)
        is_admin_request = get_jwt_identity() is not None
    except Exception:
        is_admin_request = False

    query = Article.query.filter_by(slug=slug)
    if not is_admin_request:
        query = query.filter_by(status='published')

    article = query.first_or_404()
    
    return jsonify({
        'article': article.to_dict(include_content=True)
    }), 200


@bp.route('/ai-rewrite', methods=['POST'])
@jwt_required()
@limiter.limit(lambda: current_app.config.get('AI_REWRITE_RATE_LIMIT', '30 per minute'))
def ai_rewrite():
    """Submit an AI rewrite task."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    source_url = (data.get('sourceUrl') or '').strip()
    rewrite_strategy = data.get('rewriteStrategy', 'standard')
    template_type = data.get('templateType', 'tutorial')
    auto_publish = bool(data.get('autoPublish', False))

    if not source_url:
        return jsonify({'error': '请提供文章链接'}), 400
    if 'mp.weixin.qq.com' not in source_url:
        return jsonify({'error': '目前仅支持微信公众号文章链接'}), 400
    if rewrite_strategy not in ('standard', 'deep', 'creative'):
        return jsonify({'error': '不支持的改写策略'}), 400
    if template_type not in ('tutorial', 'concept', 'comparison', 'practice'):
        return jsonify({'error': '不支持的文章模板'}), 400
    if not current_app.config.get('MINIMAX_API_KEY'):
        return jsonify({'error': '后端未配置 MINIMAX_API_KEY'}), 400

    task = create_task({
        'status': 'processing',
        'progress': 5,
        'message': '任务已创建，准备抓取原文...',
        'source_url': source_url,
        'rewrite_strategy': rewrite_strategy,
        'template_type': template_type,
        'auto_publish': auto_publish,
    })

    app = current_app._get_current_object()
    worker = threading.Thread(
        target=process_rewrite_task,
        args=(app, task['id'], source_url, rewrite_strategy, template_type, auto_publish),
        daemon=True,
    )
    worker.start()

    return jsonify({
        'task': task,
    }), 202


@bp.route('/ai-progress', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def ai_progress():
    """Fetch rewrite task progress or recent task history."""
    task_id = request.args.get('taskId')

    if task_id:
        task = get_task(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify({'task': task}), 200

    return jsonify({
        'tasks': list_tasks(),
    }), 200


@bp.route('/ai-tasks/clear', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def clear_ai_tasks():
    """Clear completed and failed AI tasks from memory."""
    cleared = clear_finished_tasks()
    return jsonify({'cleared': cleared}), 200


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

    slug = build_article_slug(data.get('slug'), data.get('title'))

    # Check if slug already exists
    if Article.query.filter_by(slug=slug).first():
        return jsonify({'error': 'Slug already exists'}), 400
    
    # Create article
    article = Article(
        slug=slug,
        title=data.get('title'),
        description=data.get('description') or summarize_description(data.get('content'), ''),
        content=data.get('content'),
        cover_image=data.get('cover_image'),
        source_url=data.get('source_url'),
        ai_generated=1 if data.get('ai_generated') else 0,
        ai_model=data.get('ai_model'),
        rewrite_strategy=data.get('rewrite_strategy'),
        template_type=data.get('template_type'),
        word_count=data.get('word_count'),
        auto_published=1 if data.get('auto_published') else 0,
        status=data.get('status', 'draft'),
        published_at=(
            parse_datetime_value(data.get('published_at')) or datetime.utcnow()
            if data.get('status') == 'published' else parse_datetime_value(data.get('published_at'))
        ),
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
        'article': article.to_dict(include_content=True)
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
    if 'slug' in data:
        article.slug = build_article_slug(data.get('slug'), data.get('title') or article.title, article)
    if 'description' in data:
        article.description = data['description']
    elif 'content' in data and not article.description:
        article.description = summarize_description(data.get('content'), article.description or '')
    if 'content' in data:
        article.content = data['content']
    if 'cover_image' in data:
        article.cover_image = data['cover_image']
    if 'source_url' in data:
        article.source_url = data['source_url']
    if 'ai_generated' in data:
        article.ai_generated = 1 if data.get('ai_generated') else 0
    if 'ai_model' in data:
        article.ai_model = data.get('ai_model')
    if 'rewrite_strategy' in data:
        article.rewrite_strategy = data.get('rewrite_strategy')
    if 'template_type' in data:
        article.template_type = data.get('template_type')
    if 'word_count' in data:
        article.word_count = data.get('word_count')
    if 'auto_published' in data:
        article.auto_published = 1 if data.get('auto_published') else 0
    if 'status' in data:
        article.status = data['status']
        if data['status'] == 'published' and not article.published_at:
            article.published_at = datetime.utcnow()
    if 'published_at' in data:
        article.published_at = parse_datetime_value(data.get('published_at'))
    
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
        'article': article.to_dict(include_content=True)
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
