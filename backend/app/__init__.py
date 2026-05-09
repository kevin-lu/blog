"""
Flask Application Factory
"""
from flask import Flask

from .config import config
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
    from .api.v1 import auth, articles, categories, tags, comments, settings, upload
    
    app.register_blueprint(auth.bp, url_prefix='/api/v1/auth')
    app.register_blueprint(articles.bp, url_prefix='/api/v1/articles')
    app.register_blueprint(categories.bp, url_prefix='/api/v1/categories')
    app.register_blueprint(tags.bp, url_prefix='/api/v1/tags')
    app.register_blueprint(comments.bp, url_prefix='/api/v1/comments')
    app.register_blueprint(settings.bp, url_prefix='/api/v1/settings')
    app.register_blueprint(upload.bp, url_prefix='/api/v1/upload')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
