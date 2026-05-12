"""
Authentication API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.extensions import db, limiter
from app.models.admin import Admin
from app.utils.jwt import generate_tokens, get_current_admin
from datetime import timedelta

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    Admin login endpoint
    
    Request JSON:
        {
            "username": "admin username",
            "password": "admin password"
        }
    
    Returns:
        {
            "access_token": "JWT access token",
            "refresh_token": "JWT refresh token",
            "user": { ...user info... }
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find admin by username
    admin = Admin.query.filter_by(username=username).first()
    
    if not admin:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Verify password
    if not admin.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate tokens
    tokens = generate_tokens(admin)
    
    return jsonify({
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'user': admin.to_dict()
    }), 200


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Admin logout endpoint
    
    Note: In production, you should add the token to a blacklist
    """
    # TODO: Implement token blacklist
    return jsonify({'message': 'Successfully logged out'}), 200


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    
    Returns:
        {
            "access_token": "new JWT access token"
        }
    """
    admin_id = get_jwt_identity()
    admin = Admin.query.get(admin_id)
    
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    # Generate new access token
    access_token = create_access_token(
        identity=admin.id,
        additional_claims={
            'username': admin.username,
            'role': admin.role
        }
    )
    
    return jsonify({'access_token': access_token}), 200


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current admin user info
    
    Returns:
        {
            "user": { ...user info... }
        }
    """
    admin_id = get_jwt_identity()
    admin = Admin.query.get(admin_id)
    
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    return jsonify({
        'user': admin.to_dict()
    }), 200
