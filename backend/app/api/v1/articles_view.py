"""
Article View Count API v1
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db, limiter
from app.models.article import Article

bp = Blueprint('article_views', __name__)


def get_client_ip():
    """获取客户端 IP 地址"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'


@bp.route('/<slug>/view', methods=['POST'])
@limiter.limit("100 per hour")
def increment_view_count(slug):
    """
    增加文章浏览次数
    
    防刷策略：
    - 同一 IP 在 24 小时内只计一次
    - 使用内存缓存记录 IP 访问时间
    
    Returns:
        {
            "success": true,
            "view_count": 1234
        }
    """
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'success': False, 'error': 'Article not found'}), 404
    
    # 获取客户端 IP
    client_ip = get_client_ip()
    
    # 缓存 key
    cache_key = f'article_view:{slug}:{client_ip}'
    
    # 检查是否在 24 小时内已访问（简单内存缓存实现）
    if not hasattr(current_app, 'view_cache'):
        current_app.view_cache = {}
    
    last_view = current_app.view_cache.get(cache_key)
    if last_view:
        # 检查是否在 24 小时内
        if datetime.now() - last_view < timedelta(hours=24):
            # 已访问过，不增加计数，但返回当前浏览次数
            return jsonify({
                'success': True,
                'view_count': article.view_count or 0,
                'cached': True
            })
    
    # 增加浏览次数
    article.view_count = (article.view_count or 0) + 1
    db.session.commit()
    
    # 更新缓存
    current_app.view_cache[cache_key] = datetime.now()
    
    return jsonify({
        'success': True,
        'view_count': article.view_count
    }), 200
