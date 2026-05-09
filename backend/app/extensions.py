"""
Flask Extensions Initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restx import Api, Namespace

# Database
db = SQLAlchemy()

# JWT Authentication
jwt = JWTManager()

# CORS
cors = CORS()

# Cache
cache = Cache()

# Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Swagger API Documentation
api = Api(
    title='Blog API',
    version='1.0.0',
    description='Blog backend API with RESTful endpoints',
    doc='/docs',
    prefix='/api/v1',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Bearer token'
        }
    },
    security='Bearer'
)

# API Namespaces
auth_ns = Namespace('auth', description='Authentication operations')
articles_ns = Namespace('articles', description='Article management operations')
categories_ns = Namespace('categories', description='Category management operations')
tags_ns = Namespace('tags', description='Tag management operations')
comments_ns = Namespace('comments', description='Comment management operations')
settings_ns = Namespace('settings', description='Site settings operations')
upload_ns = Namespace('upload', description='File upload operations')
