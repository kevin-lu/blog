"""
Tags API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.models.tag import Tag
from datetime import datetime

bp = Blueprint('tags', __name__)


@bp.route('', methods=['GET'])
@limiter.limit("30 per minute")
def get_tags():
    """
    Get all tags
    
    Returns:
        {
            "tags": [...]
        }
    """
    tags = Tag.query.order_by(Tag.name).all()
    
    return jsonify({
        'tags': [tag.to_dict() for tag in tags]
    }), 200


@bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_tag():
    """
    Create new tag (requires authentication)
    
    Request JSON:
        {
            "name": "Tag name",
            "slug": "tag-slug"
        }
    
    Returns:
        {
            "tag": { ...created tag... }
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    if not data.get('name') or not data.get('slug'):
        return jsonify({'error': 'Name and slug are required'}), 400
    
    # Check if slug already exists
    if Tag.query.filter_by(slug=data.get('slug')).first():
        return jsonify({'error': 'Slug already exists'}), 400
    
    tag = Tag(
        name=data.get('name'),
        slug=data.get('slug'),
        color=data.get('color') or '#18a058',
    )
    
    db.session.add(tag)
    db.session.commit()
    
    return jsonify({
        'tag': tag.to_dict()
    }), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per hour")
def update_tag(id):
    """Update tag (requires authentication)"""
    tag = Tag.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    if 'name' in data:
        tag.name = data['name']
    if 'slug' in data:
        existing = Tag.query.filter_by(slug=data['slug']).first()
        if existing and existing.id != tag.id:
            return jsonify({'error': 'Slug already exists'}), 400
        tag.slug = data['slug']
    if 'color' in data:
        tag.color = data.get('color') or '#18a058'

    tag.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'tag': tag.to_dict()
    }), 200


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("5 per hour")
def delete_tag(id):
    """
    Delete tag (requires authentication)
    
    Returns:
        {
            "message": "Tag deleted successfully"
        }
    """
    tag = Tag.query.get_or_404(id)
    
    db.session.delete(tag)
    db.session.commit()
    
    return jsonify({
        'message': 'Tag deleted successfully'
    }), 200
