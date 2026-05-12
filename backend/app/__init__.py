"""
Flask Application Factory
"""
import os
from flask import Flask, send_from_directory
from sqlalchemy import inspect, text
from dotenv import load_dotenv

from .extensions import db, jwt, cors, cache, limiter, api


def create_app(config_name=None):
    """
    Create and configure the Flask application
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Configured Flask application
    """
    if config_name is None:
        config_name = 'default'

    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    from .config import config
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, supports_credentials=True)
    cache.init_app(app)
    limiter.init_app(app)
    api.init_app(app)
    
    # Register blueprints
    from .api.v1 import auth, articles, categories, tags, comments, settings, upload, donations
    
    app.register_blueprint(auth.bp, url_prefix='/api/v1/auth')
    app.register_blueprint(articles.bp, url_prefix='/api/v1/articles')
    app.register_blueprint(categories.bp, url_prefix='/api/v1/categories')
    app.register_blueprint(tags.bp, url_prefix='/api/v1/tags')
    app.register_blueprint(comments.bp, url_prefix='/api/v1/comments')
    app.register_blueprint(settings.bp, url_prefix='/api/v1/settings')
    app.register_blueprint(upload.bp, url_prefix='/api/v1/upload')
    app.register_blueprint(donations.bp, url_prefix='/api/v1/donations')
    
    # Register route to serve uploaded files
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        return send_from_directory(upload_folder, filename)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        ensure_database_schema()

    return app


def ensure_database_schema():
    """Apply minimal additive schema updates for the SQLite dev database."""
    inspector = inspect(db.engine)

    if 'article_meta' in inspector.get_table_names():
        existing_columns = {column['name'] for column in inspector.get_columns('article_meta')}
        required_columns = {
            'content': 'TEXT',
            'source_url': 'TEXT',
            'ai_generated': 'INTEGER DEFAULT 0',
            'ai_model': 'VARCHAR(100)',
            'rewrite_strategy': 'VARCHAR(20)',
            'template_type': 'VARCHAR(20)',
            'word_count': 'INTEGER',
            'auto_published': 'INTEGER DEFAULT 0',
        }
        with db.engine.begin() as connection:
            for column_name, column_type in required_columns.items():
                if column_name not in existing_columns:
                    connection.execute(text(f'ALTER TABLE article_meta ADD COLUMN {column_name} {column_type}'))

    if 'tags' in inspector.get_table_names():
        existing_columns = {column['name'] for column in inspector.get_columns('tags')}
        if 'color' not in existing_columns:
            with db.engine.begin() as connection:
                connection.execute(text("ALTER TABLE tags ADD COLUMN color VARCHAR(20) DEFAULT '#18a058'"))
