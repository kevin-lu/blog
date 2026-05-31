"""
File Upload Utilities
"""
import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', 
                                                     {'jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, subfolder='uploads'):
    """
    Save uploaded file to disk
    
    Args:
        file: FileStorage object
        subfolder: Subfolder under uploads directory
    
    Returns:
        Relative path to saved file
    """
    # Get upload folder
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    # Create subfolder path
    folder_path = os.path.join(upload_folder, subfolder)
    os.makedirs(folder_path, exist_ok=True)
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    if not filename:
        filename = 'unnamed'
    
    # Add UUID prefix to avoid conflicts
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(folder_path, unique_filename)
    
    # Save file
    file.save(file_path)
    
    # Return relative path
    return os.path.join(subfolder, unique_filename)
