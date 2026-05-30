"""
Article Visit Service
"""
from datetime import datetime, timedelta
from flask import request
from app.models.article_visit import ArticleVisit
from app.extensions import db
from sqlalchemy import func


def get_client_ip():
    """获取客户端 IP 地址"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'


def record_visit(article_id, article_slug, user_agent=None):
    """
    记录文章访问
    
    Args:
        article_id: 文章 ID
        article_slug: 文章 slug
        user_agent: User-Agent 字符串
    
    Returns:
        ArticleVisit: 访问记录对象
    """
    ip_address = get_client_ip()
    
    # 检查 24 小时内是否已访问
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    existing_visit = ArticleVisit.query.filter(
        ArticleVisit.article_id == article_id,
        ArticleVisit.ip_address == ip_address,
        ArticleVisit.visited_at >= twenty_four_hours_ago
    ).first()
    
    if existing_visit:
        return existing_visit
    
    # 创建新访问记录
    visit = ArticleVisit(
        article_id=article_id,
        article_slug=article_slug,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.session.add(visit)
    db.session.commit()
    
    return visit


def get_article_stats(article_slug, period='daily', days=30):
    """
    获取文章统计数据
    
    Args:
        article_slug: 文章 slug
        period: 统计周期 ('daily', 'weekly', 'monthly')
        days: 统计天数
    
    Returns:
        dict: 统计数据
    """
    # 确保 days 是整数
    if isinstance(days, str):
        days = int(days)
    
    # 总 PV 和 UV
    total_pv = ArticleVisit.query.filter_by(article_slug=article_slug).count()
    total_uv = db.session.query(
        func.count(func.distinct(ArticleVisit.ip_address))
    ).filter_by(article_slug=article_slug).scalar()
    
    # 首次和最近访问时间
    first_visit = ArticleVisit.query.filter_by(
        article_slug=article_slug
    ).order_by(ArticleVisit.visited_at.asc()).first()
    
    last_visit = ArticleVisit.query.filter_by(
        article_slug=article_slug
    ).order_by(ArticleVisit.visited_at.desc()).first()
    
    # 按周期统计
    if period == 'daily':
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        stats = db.session.query(
            func.date(ArticleVisit.visited_at).label('date'),
            func.count(ArticleVisit.id).label('pv'),
            func.count(func.distinct(ArticleVisit.ip_address)).label('uv')
        ).filter(
            ArticleVisit.article_slug == article_slug,
            ArticleVisit.visited_at >= cutoff_date
        ).group_by(func.date(ArticleVisit.visited_at)).all()
    elif period == 'weekly':
        cutoff_date = datetime.utcnow() - timedelta(weeks=days // 7)
        # MySQL 使用 YEARWEEK 函数
        stats = db.session.query(
            func.yearweek(ArticleVisit.visited_at, 0).label('date'),
            func.count(ArticleVisit.id).label('pv'),
            func.count(func.distinct(ArticleVisit.ip_address)).label('uv')
        ).filter(
            ArticleVisit.article_slug == article_slug,
            ArticleVisit.visited_at >= cutoff_date
        ).group_by(func.yearweek(ArticleVisit.visited_at, 0)).all()
    else:  # monthly
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        # MySQL 使用 DATE_FORMAT 函数
        stats = db.session.query(
            func.date_format(ArticleVisit.visited_at, '%Y-%m').label('date'),
            func.count(ArticleVisit.id).label('pv'),
            func.count(func.distinct(ArticleVisit.ip_address)).label('uv')
        ).filter(
            ArticleVisit.article_slug == article_slug,
            ArticleVisit.visited_at >= cutoff_date
        ).group_by(func.date_format(ArticleVisit.visited_at, '%Y-%m')).all()
    
    return {
        'total_pv': total_pv,
        'total_uv': total_uv,
        'first_visit': first_visit.visited_at.isoformat() if first_visit else None,
        'last_visit': last_visit.visited_at.isoformat() if last_visit else None,
        'trend': [
            {
                'date': str(row.date),
                'pv': row.pv,
                'uv': row.uv
            }
            for row in stats
        ]
    }


def get_visits_list(article_slug, page=1, limit=20, start_date=None, end_date=None, ip_address=None):
    """
    获取访问记录列表
    
    Args:
        article_slug: 文章 slug
        page: 页码
        limit: 每页数量
        start_date: 开始日期
        end_date: 结束日期
        ip_address: IP 地址筛选
    
    Returns:
        dict: 访问记录列表和总数
    """
    query = ArticleVisit.query.filter_by(article_slug=article_slug)
    
    if start_date:
        query = query.filter(ArticleVisit.visited_at >= start_date)
    if end_date:
        query = query.filter(ArticleVisit.visited_at <= end_date)
    if ip_address:
        query = query.filter_by(ip_address=ip_address)
    
    total = query.count()
    visits = query.order_by(
        ArticleVisit.visited_at.desc()
    ).offset((page - 1) * limit).limit(limit).all()
    
    return {
        'visits': [visit.to_dict() for visit in visits],
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': (total + limit - 1) // limit
    }
