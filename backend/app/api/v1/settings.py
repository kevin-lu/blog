"""
Site Settings API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.models.site_setting import SiteSetting
from app.schemas.site_setting import SiteSettingUpdate
from datetime import datetime
import json

bp = Blueprint('settings', __name__)

DEFAULT_SETTINGS = {
    'site_name': '我的博客',
    'site_description': '技术分享平台',
    'site_logo': '',
    'site_url': '',
    'site_keywords': '',
    'og_image': '',
    'site_avatar': '',
    'github_url': '',
    'twitter_url': '',
    'weibo_url': '',
    'email': '',
    'about_welcome_title': '欢迎来到我的博客',
    'about_welcome_content': '这是一个技术分享平台，主要记录我在学习和工作中的技术心得和经验总结。',
    'about_author_title': '关于博主',
    'about_author_content': '一名热爱技术的开发者，专注于 Web 开发领域。',
    'about_tech_stack_title': '技术栈',
    'about_tech_stack_items': json.dumps(['Vue.js', 'React', 'TypeScript', 'Node.js']),
    'about_contact_title': '联系方式',
    'about_contact_email': '',
    'about_contact_github': '',
    'about_contact_github_label': 'GitHub',
    'comment_require_review': 'true',
    'comment_enabled': 'true',
}


def initialize_default_settings():
    """Initialize default settings if not exist"""
    for key, value in DEFAULT_SETTINGS.items():
        if not SiteSetting.get_value(key):
            SiteSetting.set_value(key, value, f'Default {key}')


@bp.route('', methods=['GET'])
@limiter.limit("30 per minute")
def get_settings():
    """
    Get all site settings
    
    Returns:
        {
            "settings": {
                "site_name": "...",
                "site_description": "...",
                ...
            }
        }
    """
    initialize_default_settings()
    
    settings_dict = SiteSetting.get_settings_dict()
    
    tech_stack_raw = settings_dict.get('about_tech_stack_items', '[]')
    try:
        settings_dict['about_tech_stack_items'] = json.loads(tech_stack_raw)
    except (json.JSONDecodeError, TypeError):
        settings_dict['about_tech_stack_items'] = []
    
    for key in ['comment_require_review', 'comment_enabled']:
        if key in settings_dict:
            settings_dict[key] = settings_dict[key].lower() == 'true'
    
    return jsonify({
        'settings': settings_dict
    }), 200


@bp.route('', methods=['PUT'])
@jwt_required()
@limiter.limit("30 per minute")
def update_settings():
    """
    Update site settings (requires authentication)
    
    支持两种请求格式：
    
    格式 1（新）：扁平对象
        {
            "site_name": "My Blog",
            "about_tech_stack_items": ["Vue", "React"],
            ...
        }
    
    格式 2（旧）：settings 数组
        {
            "settings": [
                {"key_name": "site_name", "key_value": "My Blog"},
                {"key_name": "about_tech_stack_items", "key_value": ["Vue", "React"]},
                ...
            ]
        }
    
    Returns:
        {
            "settings": {...updated settings...}
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    # 检测数据格式
    if 'settings' in data and isinstance(data['settings'], list):
        # 旧格式：从数组转换为对象
        flat_data = {}
        for setting in data['settings']:
            key_name = setting.get('key_name')
            key_value = setting.get('key_value')
            if key_name:
                # 特殊处理：tech_stack_items 可能是数组
                if key_name == 'about_tech_stack_items' and isinstance(key_value, str):
                    try:
                        key_value = json.loads(key_value)
                    except (json.JSONDecodeError, TypeError):
                        pass
                # 特殊处理：布尔值
                elif key_name in ['comment_require_review', 'comment_enabled']:
                    if isinstance(key_value, str):
                        key_value = key_value.lower() == 'true'
                
                flat_data[key_name] = key_value
        data = flat_data
    
    # 验证和更新设置
    try:
        update_data = SiteSettingUpdate(**data)
    except Exception as e:
        return jsonify({'error': f'Invalid data: {str(e)}'}), 400
    
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for key, value in update_dict.items():
        if key == 'about_tech_stack_items' and isinstance(value, list):
            value = json.dumps(value)
        elif key in ['comment_require_review', 'comment_enabled'] and isinstance(value, bool):
            value = str(value).lower()
        
        SiteSetting.set_value(key, value)
    
    return get_settings()


@bp.route('/reset', methods=['POST'])
@jwt_required()
@limiter.limit("3 per hour")
def reset_settings():
    """
    Reset all settings to defaults (requires authentication)
    
    Returns:
        {
            "settings": {...default settings...}
        }
    """
    SiteSetting.query.delete()
    
    initialize_default_settings()
    
    return get_settings()
