"""
File Upload API v1
"""
import os
import uuid
from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import jwt_required
from app.extensions import limiter
from werkzeug.utils import secure_filename
from PIL import Image

bp = Blueprint('upload', __name__)


def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', 
                                                     {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def compress_image(file_path, max_size=(1920, 1080), quality=85):
    """
    Compress image if it exceeds max size
    
    Args:
        file_path: Path to image file
        max_size: Maximum dimensions
        quality: JPEG quality (1-100)
    
    Returns:
        Path to compressed image
    """
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if needed
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save compressed image
            img.save(file_path, 'JPEG', quality=quality, optimize=True)
            
    except Exception as e:
        current_app.logger.error(f"Error compressing image: {e}")
    
    return file_path


def generate_thumbnail(file_path, size=(300, 200)):
    """
    Generate thumbnail for image
    
    Args:
        file_path: Path to image file
        size: Thumbnail dimensions
    
    Returns:
        Path to thumbnail file
    """
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            base, ext = os.path.splitext(file_path)
            thumbnail_path = f"{base}_thumb{ext}"
            img.save(thumbnail_path, 'JPEG', quality=85)
            
            return thumbnail_path
            
    except Exception as e:
        current_app.logger.error(f"Error generating thumbnail: {e}")
        return None


@bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("20 per hour")
def upload_file():
    """
    Upload file (requires authentication)
    
    Form Data:
        file: File to upload
        type: File type (image, document)
    
    Returns:
        {
            "url": "file url",
            "thumbnail_url": "thumbnail url (for images)"
        }
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Secure filename and add UUID to avoid conflicts
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Determine upload folder
    file_type = request.form.get('type', 'document')
    if file_type == 'image':
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    else:
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents')
    
    # Create folder if not exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    # Process image if it's an image
    thumbnail_url = None
    if file_type == 'image':
        # Compress image
        compress_image(file_path)
        
        # Generate thumbnail
        thumbnail_path = generate_thumbnail(file_path)
        if thumbnail_path:
            thumbnail_url = f"/uploads/images/{os.path.basename(thumbnail_path)}"
    
    # Generate URL
    file_url = f"/{file_type}s/{os.path.basename(file_path)}"
    
    return jsonify({
        'url': file_url,
        'thumbnail_url': thumbnail_url
    }), 201
