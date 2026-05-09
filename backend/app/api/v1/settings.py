"""
Site Settings API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from flask_limiter import limiter
from app.extensions import db
from app.models.site_setting import SiteSetting
from datetime import datetime

bp = Blueprint('settings', __name__)


@bp.route('', methods=['GET'])
@limiter.limit("30 per minute")
def get_settings():
    """
    Get all site settings
    
    Returns:
        {
            "settings": [...]
        }
    """
    settings = SiteSetting.query.all()
    
    return jsonify({
        'settings': [setting.to_dict() for setting in settings]
    }), 200


@bp.route('', methods=['PUT'])
@jwt_required()
@limiter.limit("5 per hour")
def update_settings():
    """
    Update site settings (requires authentication)
    
    Request JSON:
        {
            "settings": [
                {
                    "key_name": "site_title",
                    "key_value": "My Blog"
                }
            ]
        }
    
    Returns:
        {
            "settings": [...updated settings...]
        }
    """
    data = request.get_json()
    
    if not data or not data.get('settings'):
        return jsonify({'error': 'Settings array is required'}), 400
    
    updated_settings = []
    
    for setting_data in data['settings']:
        key_name = setting_data.get('key_name')
        key_value = setting_data.get('key_value')
        
        if not key_name:
            continue
        
        setting = SiteSetting.query.filter_by(key_name=key_name).first()
        
        if setting:
            setting.key_value = key_value
            setting.description = setting_data.get('description', setting.description)
            setting.updated_at = datetime.utcnow()
            updated_settings.append(setting)
    
    db.session.commit()
    
    return jsonify({
        'settings': [setting.to_dict() for setting in updated_settings]
    }), 200
