"""
Donation Settings API v1
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db, limiter
from app.models.donation import DonationSetting
from app.utils.upload import save_uploaded_file
import os

bp = Blueprint('donations', __name__, url_prefix='/api/v1/donations')


@bp.route('', methods=['GET'])
def get_donation_settings():
    """
    Get donation settings (public)
    
    Returns:
        {
            "settings": { ...donation settings... }
        }
    """
    settings = DonationSetting.get_current()
    
    if not settings:
        return jsonify({'settings': None}), 404
    
    return jsonify({
        'settings': settings.to_dict()
    }), 200


@bp.route('', methods=['PUT'])
@jwt_required()
@limiter.limit("5 per hour")
def update_donation_settings():
    """
    Update donation settings (requires authentication)
    
    Request JSON:
        {
            "title": "支持博主",
            "description": "文案...",
            "enabled": true
        }
    
    Returns:
        {
            "settings": { ...updated settings... }
        }
    """
    settings = DonationSetting.get_current()
    
    if not settings:
        # Create new if not exists
        settings = DonationSetting()
        db.session.add(settings)
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    if 'title' in data:
        settings.title = data['title']
    if 'description' in data:
        settings.description = data['description']
    if 'enabled' in data:
        settings.enabled = data['enabled']
    
    db.session.commit()
    
    return jsonify({
        'settings': settings.to_dict()
    }), 200


@bp.route('/upload-qr', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def upload_qr_code():
    """
    Upload QR code image
    
    Form Data:
        type: 'wechat' or 'alipay'
        file: image file
    
    Returns:
        {
            "url": "file url"
        }
    """
    data = request.form
    
    qr_type = data.get('type')
    if not qr_type or qr_type not in ['wechat', 'alipay']:
        return jsonify({'error': 'Invalid QR code type'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file
    filename = save_uploaded_file(file, 'donation/qrcodes')
    file_url = f'/uploads/{filename}'
    
    # Update donation settings
    settings = DonationSetting.get_current()
    if not settings:
        settings = DonationSetting()
        db.session.add(settings)
        db.session.commit()
    
    if qr_type == 'wechat':
        settings.wechat_qr = file_url
    else:
        settings.alipay_qr = file_url
    
    db.session.commit()
    
    return jsonify({
        'url': file_url,
        'type': qr_type
    }), 200
