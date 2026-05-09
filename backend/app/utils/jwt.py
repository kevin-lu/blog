"""
JWT Token Utilities
"""
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended.utils import get_jwt_identity
from app.models.admin import Admin


def generate_tokens(admin: Admin) -> dict:
    """
    Generate access and refresh tokens for admin
    
    Args:
        admin: Admin user object
    
    Returns:
        Dictionary containing access and refresh tokens
    """
    access_token = create_access_token(
        identity=admin.id,
        additional_claims={
            'username': admin.username,
            'role': admin.role
        }
    )
    refresh_token = create_refresh_token(
        identity=admin.id,
        additional_claims={
            'username': admin.username
        }
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }


def get_current_admin() -> Admin:
    """
    Get current admin user from JWT token
    
    Returns:
        Admin user object
    
    Raises:
        ValueError: If admin not found
    """
    admin_id = get_jwt_identity()
    admin = Admin.query.get(admin_id)
    
    if not admin:
        raise ValueError('Admin not found')
    
    return admin
