"""
Comments API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.models.comment import Comment
from datetime import datetime

bp = Blueprint('comments', __name__)


@bp.route('', methods=['GET'])
@limiter.limit("30 per minute")
def get_comments():
    """
    Get comments list
    
    Query Parameters:
        article_slug: Filter by article slug
        status: Filter by status (pending, approved, rejected)
        page: Page number
        limit: Items per page
    
    Returns:
        {
            "comments": [...],
            "total": 100,
            "page": 1,
            "limit": 10
        }
    """
    article_slug = request.args.get('article_slug')
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    query = Comment.query
    
    if article_slug:
        query = query.filter_by(article_slug=article_slug)
    
    if status:
        query = query.filter_by(status=status)
    
    query = query.order_by(Comment.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    
    return jsonify({
        'comments': [comment.to_dict() for comment in pagination.items],
        'total': pagination.total,
        'page': page,
        'limit': limit
    }), 200


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("5 per hour")
def delete_comment(id):
    """
    Delete comment (requires authentication)
    
    Returns:
        {
            "message": "Comment deleted successfully"
        }
    """
    comment = Comment.query.get_or_404(id)
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({
        'message': 'Comment deleted successfully'
    }), 200


@bp.route('/<int:id>/approve', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per hour")
def approve_comment(id):
    """
    Approve comment (requires authentication)
    
    Returns:
        {
            "comment": { ...updated comment... }
        }
    """
    comment = Comment.query.get_or_404(id)
    comment.status = 'approved'
    comment.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'comment': comment.to_dict()
    }), 200


@bp.route('/<int:id>/reject', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per hour")
def reject_comment(id):
    """Reject comment (requires authentication)"""
    comment = Comment.query.get_or_404(id)
    comment.status = 'rejected'
    comment.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'comment': comment.to_dict()
    }), 200


@bp.route('', methods=['POST'])
@limiter.limit("10 per hour")
def create_comment():
    """
    创建评论或回复
    
    Request Body:
        {
            "article_slug": "article-slug",
            "content": "评论内容",
            "author_name": "张三",
            "author_email": "zhangsan@example.com",  # 可选
            "parent_id": null,  # 如果是回复，则为父评论 ID
            "reply_to": null    # 如果是回复，则为被回复者名称
        }
    
    Returns:
        {
            "success": true,
            "comment": { ... }
        }
    """
    data = request.get_json()
    
    # 验证必填字段
    if not data:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    
    article_slug = data.get('article_slug')
    content = data.get('content')
    author_name = data.get('author_name')
    
    if not article_slug or not content or not author_name:
        return jsonify({
            'success': False,
            'error': 'Missing required fields: article_slug, content, author_name'
        }), 400
    
    # 验证 parent_id（如果有）
    parent_id = data.get('parent_id')
    if parent_id:
        parent_comment = Comment.query.get(parent_id)
        if not parent_comment:
            return jsonify({'success': False, 'error': 'Parent comment not found'}), 404
    
    # 创建评论
    comment = Comment(
        article_slug=article_slug,
        content=content,
        author_name=author_name,
        author_email=data.get('author_email'),
        parent_id=parent_id,
        reply_to=data.get('reply_to'),
        status='approved',  # 自动通过
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': comment.to_dict()
    }), 201


@bp.route('/article/<slug>', methods=['GET'])
@limiter.limit("60 per minute")
def get_article_comments(slug):
    """
    获取文章评论列表（树形结构）
    
    Query Parameters:
        page: 页码
        limit: 每页数量
    
    Returns:
        {
            "comments": [...],  # 树形结构
            "total": 100,
            "page": 1,
            "limit": 20
        }
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # 获取顶级评论（parent_id 为 null）
    query = Comment.query.filter_by(
        article_slug=slug,
        parent_id=None,
        status='approved'
    )
    
    query = query.order_by(Comment.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    
    # 构建树形结构
    comments = []
    for comment in pagination.items:
        comment_dict = comment.to_dict(include_replies=True)
        # 将 replies 从动态加载器转换为列表
        if 'replies' in comment_dict:
            comment_dict['replies'] = [
                reply.to_dict(include_replies=False) 
                for reply in comment.replies.order_by(Comment.created_at.asc()).all()
            ]
        comments.append(comment_dict)
    
    return jsonify({
        'comments': comments,
        'total': pagination.total,
        'page': page,
        'limit': limit
    }), 200


@bp.route('/article/<slug>/count', methods=['GET'])
@limiter.limit("60 per minute")
def get_article_comment_count(slug):
    """
    获取文章评论数
    
    Returns:
        {
            "count": 10
        }
    """
    count = Comment.query.filter_by(
        article_slug=slug,
        status='approved'
    ).count()
    
    return jsonify({'count': count}), 200
