"""
AI Queue API Routes
AI 改写队列相关接口
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.ai_queue import (
    get_queue_status,
    process_queue_batch,
    retry_failed_task,
)
from app.models.crawler import AIQueue

bp = Blueprint('queue', __name__)


@bp.route('/status', methods=['GET'])
@jwt_required()
def get_status():
    """
    获取队列状态
    
    Returns:
        pending: int - 待处理数量
        processing: int - 处理中数量
        completed: int - 已完成数量
        failed: int - 失败数量
        estimated_time_minutes: float - 预计处理时间 (分钟)
    """
    status = get_queue_status()
    return jsonify(status), 200


@bp.route('/items', methods=['GET'])
@jwt_required()
def get_items():
    """
    获取队列列表
    
    Query Params:
        page: int (可选) - 页码，默认 1
        limit: int (可选) - 每页数量，默认 20
        status: str (可选) - 按状态过滤 (pending, processing, completed, failed)
        
    Returns:
        items: list - 队列项列表
        total: int - 总数
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    status_filter = request.args.get('status')
    
    query = AIQueue.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # 分页
    pagination = query.order_by(AIQueue.queued_at.desc()) \
        .paginate(page=page, per_page=limit, error_out=False)
    
    items = []
    for item in pagination.items:
        items.append({
            'id': item.id,
            'queue_id': item.queue_id,
            'article_id': item.article_id,
            'title': item.title,
            'source_url': item.source_url,
            'author': item.author,
            'status': item.status,
            'priority': item.priority,
            'retry_count': item.retry_count,
            'queued_at': item.queued_at.isoformat(),
            'started_at': item.started_at.isoformat() if item.started_at else None,
            'completed_at': item.completed_at.isoformat() if item.completed_at else None,
            'error_message': item.error_message,
        })
    
    return jsonify({
        'total': pagination.total,
        'page': page,
        'limit': limit,
        'items': items,
    }), 200


@bp.route('/process', methods=['POST'])
@jwt_required()
def process_queue():
    """
    手动处理队列
    
    Request Body:
        count: int (可选) - 处理数量，不传则处理所有
        
    Returns:
        processed: int - 处理数量
        success: int - 成功数量
        failed: int - 失败数量
    """
    data = request.get_json() or {}
    count = data.get('count', 50)
    
    result = process_queue_batch(batch_size=count)
    
    return jsonify(result), 200


@bp.route('/retry/<queue_id>', methods=['POST'])
@jwt_required()
def retry_queue_item(queue_id):
    """
    重试失败的队列任务
    
    Args:
        queue_id: 队列 ID
        
    Returns:
        message: str - 操作结果
    """
    success = retry_failed_task(queue_id)
    
    if success:
        return jsonify({
            'queue_id': queue_id,
            'status': 'pending',
            'message': '任务已重新加入队列',
        }), 200
    else:
        return jsonify({
            'error': '重试失败，任务可能不存在或状态不正确',
        }), 400


@bp.route('/<queue_id>', methods=['GET'])
@jwt_required()
def get_queue_item(queue_id):
    """
    获取单个队列项详情
    
    Args:
        queue_id: 队列 ID
        
    Returns:
        队列项详情
    """
    item = AIQueue.query.filter_by(queue_id=queue_id).first()
    
    if not item:
        return jsonify({'error': '队列项不存在'}), 404
    
    return jsonify({
        'id': item.id,
        'queue_id': item.queue_id,
        'article_id': item.article_id,
        'title': item.title,
        'original_content': item.original_content,
        'source_url': item.source_url,
        'author': item.author,
        'published_at': item.published_at.isoformat() if item.published_at else None,
        'status': item.status,
        'priority': item.priority,
        'retry_count': item.retry_count,
        'rewritten_content': item.rewritten_content,
        'ai_model': item.ai_model,
        'rewrite_strategy': item.rewrite_strategy,
        'queued_at': item.queued_at.isoformat(),
        'started_at': item.started_at.isoformat() if item.started_at else None,
        'completed_at': item.completed_at.isoformat() if item.completed_at else None,
        'error_message': item.error_message,
    }), 200
