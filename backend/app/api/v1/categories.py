"""
Categories API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.models.category import Category
from app.utils.jwt import get_current_admin
from datetime import datetime

bp = Blueprint('categories', __name__)


@bp.route('', methods=['GET'])
@limiter.limit("30 per minute")
def get_categories():
    """
    Get all categories
    
    Returns:
        {
            "categories": [...]
        }
    """
    categories = Category.query.order_by(Category.sort_order, Category.name).all()
    
    return jsonify({
        'categories': [category.to_dict(include_article_count=True) for category in categories]
    }), 200


@bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def create_category():
    """
    Create new category (requires authentication)
    
    Request JSON:
        {
            "name": "Category name",
            "slug": "category-slug",
            "description": "Category description",
            "parent_id": 1,
            "sort_order": 0
        }
    
    Returns:
        {
            "category": { ...created category... }
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    if not data.get('name') or not data.get('slug'):
        return jsonify({'error': 'Name and slug are required'}), 400
    
    # Check if slug already exists
    if Category.query.filter_by(slug=data.get('slug')).first():
        return jsonify({'error': 'Slug already exists'}), 400
    
    category = Category(
        name=data.get('name'),
        slug=data.get('slug'),
        description=data.get('description'),
        parent_id=data.get('parent_id'),
        sort_order=data.get('sort_order', 0)
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'category': category.to_dict()
    }), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@limiter.limit("10 per hour")
def update_category(id):
    """Update category (requires authentication)"""
    category = Category.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    if 'name' in data:
        category.name = data['name']
    if 'slug' in data:
        existing = Category.query.filter_by(slug=data['slug']).first()
        if existing and existing.id != category.id:
            return jsonify({'error': 'Slug already exists'}), 400
        category.slug = data['slug']
    if 'description' in data:
        category.description = data['description']
    if 'parent_id' in data:
        category.parent_id = data['parent_id']
    if 'sort_order' in data:
        category.sort_order = data['sort_order']

    category.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'category': category.to_dict()
    }), 200


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@limiter.limit("30 per minute")
def delete_category(id):
    """
    Delete category (requires authentication)
    
    Returns:
        {
            "message": "Category deleted successfully"
        }
    """
    category = Category.query.get_or_404(id)
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({
        'message': 'Category deleted successfully'
    }), 200
