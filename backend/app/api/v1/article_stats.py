"""
Article Statistics API
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.article import Article
from app.services.article_visit_service import get_article_stats, get_visits_list

bp = Blueprint('article_stats', __name__)


@bp.route('/<slug>/stats', methods=['GET'])
def get_stats(slug):
    """
    获取文章统计数据
    
    Query Parameters:
        - period: 统计周期 (daily, weekly, monthly), default: daily
        - days: 统计天数，default: 30
    
    Returns:
        {
            "total_pv": 1234,
            "total_uv": 567,
            "first_visit": "2026-05-01T10:00:00",
            "last_visit": "2026-05-23T15:30:00",
            "trend": [
                {"date": "2026-05-23", "pv": 100, "uv": 50}
            ]
        }
    """
    period = request.args.get('period', 'daily')
    days = request.args.get('days', '30', type=int)
    
    # 验证文章是否存在
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    stats = get_article_stats(slug, period, days)
    
    return jsonify(stats)


@bp.route('/<slug>/visits', methods=['GET'])
def get_visits(slug):
    """
    获取访问记录列表
    
    Query Parameters:
        - page: 页码，default: 1
        - limit: 每页数量，default: 20
        - start_date: 开始日期 (ISO 8601)
        - end_date: 结束日期 (ISO 8601)
        - ip_address: IP 地址筛选
    
    Returns:
        {
            "visits": [...],
            "total": 100,
            "page": 1,
            "limit": 20,
            "total_pages": 5
        }
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ip_address = request.args.get('ip_address')
    
    # 验证文章是否存在
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    visits = get_visits_list(slug, page, limit, start_date, end_date, ip_address)
    
    return jsonify(visits)


@bp.route('/admin/<int:article_id>/stats', methods=['GET'])
@jwt_required()
def get_admin_stats(article_id):
    """
    后台管理接口 - 获取文章统计
    
    与公开接口的区别：
    - 需要 JWT 认证
    - 返回更详细的数据（包括 IP 地址等）
    """
    period = request.args.get('period', 'daily')
    days = request.args.get('days', '30', type=int)
    
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    stats = get_article_stats(article.slug, period, days)
    
    # 额外返回详细数据
    stats['slug'] = article.slug
    stats['title'] = article.title
    
    return jsonify(stats)


@bp.route('/admin/<int:article_id>/visits', methods=['GET'])
@jwt_required()
def get_admin_visits(article_id):
    """
    后台管理接口 - 获取访问记录列表
    
    与公开接口的区别：
    - 需要 JWT 认证
    - 返回完整 IP 地址
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    ip_address = request.args.get('ip_address')
    
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    visits = get_visits_list(article.slug, page, limit, start_date, end_date, ip_address)
    
    return jsonify(visits)
