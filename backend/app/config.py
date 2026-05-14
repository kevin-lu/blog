"""
Application Configuration
"""
import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_APP = os.environ.get('FLASK_APP', 'app')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
    }
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_COOKIE_SECURE = os.environ.get('FLASK_ENV', 'development') == 'production'
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_QUERY_STRING_ENABLED = False
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))  # 10MB default
    
    # Rate Limiting
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100 per hour')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')

    # AI Rewrite
    MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
    MINIMAX_MODEL = os.environ.get('MINIMAX_MODEL', 'MiniMax-M2.7')
    MINIMAX_API_HOST = os.environ.get('MINIMAX_API_HOST', 'https://api.minimaxi.com/v1/chat/completions')
    MINIMAX_REQUEST_TIMEOUT = int(os.environ.get('MINIMAX_REQUEST_TIMEOUT', '300'))
    MINIMAX_MAX_RETRIES = int(os.environ.get('MINIMAX_MAX_RETRIES', '2'))
    AI_SOURCE_MAX_CHARS = int(os.environ.get('AI_SOURCE_MAX_CHARS', '12000'))
    AI_REWRITE_RATE_LIMIT = os.environ.get(
        'AI_REWRITE_RATE_LIMIT',
        '30 per minute' if os.environ.get('FLASK_ENV', 'development') == 'development' else '5 per hour'
    )
    
    # AI Queue Configuration
    AI_CONCURRENT_LIMIT = int(os.environ.get('AI_CONCURRENT_LIMIT', '2'))  # 最大并发数
    AI_REQUEST_DELAY = int(os.environ.get('AI_REQUEST_DELAY', '2'))        # 请求间隔 (秒)
    AI_MAX_RETRIES = int(os.environ.get('AI_MAX_RETRIES', '2'))            # 最大重试次数
    AI_TIMEOUT = int(os.environ.get('AI_TIMEOUT', '300'))                  # 超时时间 (秒)
    AI_BATCH_RATE_LIMIT = os.environ.get('AI_BATCH_RATE_LIMIT', '5 per hour')
    
    # Swagger
    SWAGGER_UI_DOC_EXPANSION = 'list'
    
    # Pagination
    ARTICLES_PER_PAGE = 10
    COMMENTS_PER_PAGE = 20
    
    # RSS Crawler - 配置多个稳定的 RSS 源
    RSS_SOURCES = [
        # 技术社区 - 使用正确的 RSS 源，直接返回具体技术文章
        {
            'name': 'cnblogs',
            'url': 'http://feed.cnblogs.com/blog/sitehome/rss',
            'enabled': True,
            'fetch_limit': 20,
            'category': '技术社区',
        },
        {
            'name': 'oschina',
            'url': 'https://www.oschina.net/news/rss',
            'enabled': True,  # 开源中国技术新闻
            'fetch_limit': 20,
            'category': '技术社区',
        },
        {
            'name': 'juejin',
            'url': 'https://rsshub.app/juejin/category/frontend',
            'enabled': False,  # RSSHub 服务器可能不稳定，需要代理
            'fetch_limit': 20,
            'category': '技术社区',
        },
        # 科技媒体
        {
            'name': 'solidot',
            'url': 'https://www.solidot.org/index.rss',
            'enabled': True,
            'fetch_limit': 15,
            'category': '科技媒体',
        },
        {
            'name': 'v2ex',
            'url': 'https://www.v2ex.com/index.xml',
            'enabled': False,  # 网络超时，已禁用
            'fetch_limit': 20,
            'category': '技术社区',
        },
        # 大厂技术博客
        {
            'name': 'meituan',
            'url': 'https://tech.meituan.com/feed/',  # 美团技术团队博客
            'enabled': True,
            'fetch_limit': 10,
            'category': '大厂博客',
        },
        {
            'name': 'ruanyifeng',
            'url': 'http://www.ruanyifeng.com/blog/atom.xml',  # 阮一峰的网络日志
            'enabled': True,
            'fetch_limit': 10,
            'category': '技术博客',
        },
        # 综合资讯
        {
            'name': 'zhihu_daily',
            'url': 'https://rsshub.app/zhihu/daily',
            'enabled': False,  # 需要代理
            'fetch_limit': 10,
            'category': '综合资讯',
        },
    ]
    
    CRAWLER_CONFIG = {
        'timeout': 30,
        'retry_times': 3,
        'retry_delay': 5,
        'user_agent': 'BlogCrawler/1.0',
    }
    
    # AI Queue
    AI_QUEUE_CONFIG = {
        'batch_size': 1,
        'delay_between_tasks': 5,
        'max_retries': 2,
        'timeout': 60,
    }
    
    # Scheduler
    SCHEDULER_CONFIG = {
        'timezone': 'Asia/Shanghai',
        'job_defaults': {
            'coalesce': True,
            'max_instances': 1,
            'misfire_grace_time': 3600,
        },
    }
    
    ENABLED_JOBS = {
        'daily_article_fetch': True,
        'ai_queue_processor': True,
        'cleanup_history': True,
    }
    
    # Alert Service
    DINGTALK_WEBHOOK = None  # 钉钉机器人 Webhook URL
    WECHAT_WORK_WEBHOOK = None  # 企业微信机器人 Webhook URL
    ALERT_QUEUE_THRESHOLD = 10  # 队列积压告警阈值（篇）
    ENABLE_DAILY_REPORT = False  # 是否启用每日报告


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = False  # Set to True to log SQL queries


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    JWT_COOKIE_CSRF_PROTECT = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
