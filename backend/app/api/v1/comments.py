"""
Comments API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask_limiter import limiter
from app.extensions import db
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
