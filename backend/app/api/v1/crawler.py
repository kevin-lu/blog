"""
Crawler API Routes
RSS 抓取相关接口
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.rss_crawler import RSSCrawler, create_crawler_task, update_crawler_task
from app.services.ai_queue import enqueue_article
from app.models.crawler import CrawlerTask, CrawledURL
from app.extensions import db
from datetime import datetime

logger = logging.getLogger(__name__)

bp = Blueprint('crawler', __name__)


@bp.route('/fetch', methods=['POST'])
@jwt_required()
def trigger_fetch():
    """
    手动触发 RSS 抓取
    
    Request Body:
        sources: array (可选) - 指定源名称列表，不传则抓取所有
        limit: int (可选) - 每个源抓取数量，默认 20
        
    Returns:
        task_id: str - 任务 ID
    """
    data = request.get_json() or {}
    source_filters = data.get('sources', [])  # 支持多源
    limit = data.get('limit', 20)
    
    crawler = RSSCrawler(timeout=10, retry_times=2)
    
    # 获取源配置
    from app.config import Config
    sources = [src for src in Config.RSS_SOURCES if src.get('enabled', True)]
    
    # 如果指定了源，只抓取指定的源
    if source_filters:
        sources = [src for src in sources if src['name'] in source_filters]
        if not sources:
            return jsonify({'error': '未找到指定的源'}), 404
    
    total_found = 0
    total_new = 0
    all_articles = []
    
    for source in sources:
        try:
            # 更新抓取限制
            source['fetch_limit'] = limit
            result, articles = crawler.fetch_source(source)
            total_found += result['found']
            total_new += result['new']
            all_articles.extend(articles)
            
        except Exception as e:
            logger.error(f"抓取源失败 {source['name']}: {e}")
            continue
    
    # 创建任务记录
    source_name = ','.join(source_filters) if source_filters else 'all'
    task_id = create_crawler_task(source_name, total_found, total_new)
    
    # 将文章加入 AI 队列
    articles_queued = 0
    for article in all_articles:
        try:
            enqueue_article(
                title=article['title'],
                original_content=article['text_content'],
                source_url=article['link'],
                author=article.get('author'),
                published_at=article.get('published'),
            )
            articles_queued += 1
        except Exception as e:
            continue
    
    # 更新任务状态
    update_crawler_task(task_id, 'completed', articles_queued=articles_queued)
    
    return jsonify({
        'task_id': task_id,
        'status': 'completed',
        'message': f'抓取完成：发现 {total_found} 篇，新增 {total_new} 篇，入队 {articles_queued} 篇',
        'stats': {
            'found': total_found,
            'new': total_new,
            'queued': articles_queued,
        }
    }), 200


@bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """
    获取抓取历史
    
    Query Params:
        page: int (可选) - 页码，默认 1
        limit: int (可选) - 每页数量，默认 20
        source: str (可选) - 按源过滤
        
    Returns:
        tasks: list - 任务列表
        total: int - 总数
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    source_filter = request.args.get('source')
    
    query = CrawlerTask.query
    
    if source_filter:
        query = query.filter_by(source=source_filter)
    
    # 分页
    pagination = query.order_by(CrawlerTask.created_at.desc()) \
        .paginate(page=page, per_page=limit, error_out=False)
    
    tasks = []
    for task in pagination.items:
        tasks.append({
            'id': task.id,
            'task_id': task.task_id,
            'source': task.source,
            'status': task.status,
            'articles_found': task.articles_found,
            'articles_new': task.articles_new,
            'articles_queued': task.articles_queued,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'created_at': task.created_at.isoformat(),
        })
    
    return jsonify({
        'total': pagination.total,
        'page': page,
        'limit': limit,
        'items': tasks,
    }), 200


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """
    获取抓取统计信息
    
    Returns:
        统计数据
    """
    # 总抓取数
    total_crawled = CrawledURL.query.count()
    
    # 按源统计
    from sqlalchemy import func
    source_stats = db.session.query(
        CrawledURL.source,
        func.count(CrawledURL.id).label('count')
    ).group_by(CrawledURL.source).all()
    
    source_breakdown = {stat.source: stat.count for stat in source_stats}
    
    # 最近抓取
    recent = CrawledURL.query.order_by(CrawledURL.crawled_at.desc()).limit(5).all()
    recent_list = [
        {
            'url': url.url,
            'title': url.title,
            'source': url.source,
            'crawled_at': url.crawled_at.isoformat(),
        }
        for url in recent
    ]
    
    return jsonify({
        'total_crawled': total_crawled,
        'by_source': source_breakdown,
        'recent': recent_list,
    }), 200


@bp.route('/sources', methods=['GET'])
@jwt_required()
def get_sources():
    """
    获取 RSS 源列表
    
    Returns:
        RSS 源配置列表
    """
    from app.config import Config
    
    sources = [
        {
            'name': src['name'],
            'url': src['url'],
            'enabled': src.get('enabled', True),
            'fetch_limit': src.get('fetch_limit', 20),
            'category': src.get('category', '未分类'),
        }
        for src in Config.RSS_SOURCES
    ]
    
    return jsonify(sources), 200


@bp.route('/sources/<source_name>/toggle', methods=['POST'])
@jwt_required()
def toggle_source(source_name):
    """
    切换 RSS 源启用状态
    
    注意：这只是临时切换，不会保存到配置文件
    如需永久保存，请修改配置文件
    
    Args:
        source_name: RSS 源名称
        
    Request Body:
        enabled: bool - 是否启用
        
    Returns:
        操作结果
    """
    data = request.get_json() or {}
    enabled = data.get('enabled', True)
    
    from app.config import Config
    
    # 查找源配置
    source_found = False
    for src in Config.RSS_SOURCES:
        if src['name'] == source_name:
            src['enabled'] = enabled
            source_found = True
            break
    
    if not source_found:
        return jsonify({'error': f'未找到源：{source_name}'}), 404
    
    return jsonify({
        'message': f'已{"启用" if enabled else "禁用"}源：{source_name}',
        'source': source_name,
        'enabled': enabled,
    }), 200
