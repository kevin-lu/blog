"""
Crawler Models
"""
from datetime import datetime
from app.extensions import db


class CrawledURL(db.Model):
    """已抓取的 URL 记录"""
    
    __tablename__ = 'crawled_urls'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(500), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200))
    source = db.Column(db.String(50))  # 来源：juejin, cnblogs
    crawled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CrawledURL {self.url}>'


class CrawledTitle(db.Model):
    """已抓取的文章标题 MD5 记录"""
    
    __tablename__ = 'crawled_titles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title_md5 = db.Column(db.String(32), unique=True, nullable=False, index=True)
    original_title = db.Column(db.String(200))
    crawled_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CrawledTitle {self.title_md5}>'


class CrawlerTask(db.Model):
    """抓取任务记录"""
    
    __tablename__ = 'crawler_tasks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    source = db.Column(db.String(50))  # 来源：juejin, cnblogs, all
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    articles_found = db.Column(db.Integer, default=0)
    articles_new = db.Column(db.Integer, default=0)
    articles_queued = db.Column(db.Integer, default=0)  # 加入 AI 队列的数量
    articles_processed = db.Column(db.Integer, default=0)  # AI 处理完成的数量
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CrawlerTask {self.task_id}>'


class AIQueue(db.Model):
    """AI 改写队列"""
    
    __tablename__ = 'ai_queue'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    queue_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article_meta.id', ondelete='CASCADE'))
    
    # 文章原始数据
    title = db.Column(db.String(200), nullable=False)
    original_content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.Text)
    author = db.Column(db.String(100))
    published_at = db.Column(db.DateTime)
    
    # 队列状态
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    priority = db.Column(db.Integer, default=0)
    retry_count = db.Column(db.Integer, default=0)
    max_retries = db.Column(db.Integer, default=2)
    
    # AI 改写结果
    rewritten_content = db.Column(db.Text)
    ai_model = db.Column(db.String(100))
    rewrite_strategy = db.Column(db.String(20))
    
    # 时间戳
    queued_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<AIQueue {self.queue_id}>'


class ScheduledJobLog(db.Model):
    """定时任务执行日志"""
    
    __tablename__ = 'scheduled_job_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.String(50), nullable=False, index=True)
    job_name = db.Column(db.String(100))
    status = db.Column(db.String(20))  # success, failed, timeout
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    result = db.Column(db.Text)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ScheduledJobLog {self.job_id}>'
