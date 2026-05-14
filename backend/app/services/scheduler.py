"""
Scheduler Service
定时任务调度器
"""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.extensions import db
from app.models.crawler import ScheduledJobLog, CrawlerTask, AIQueue
from app.services.rss_crawler import RSSCrawler
from app.services.ai_queue import process_queue_batch
from app.config import Config

logger = logging.getLogger(__name__)

# 创建调度器
scheduler = BackgroundScheduler(timezone='Asia/Shanghai')


def log_job_execution(job_id: str, job_name: str, status: str, 
                     started_at: datetime, result: str = None, 
                     error_message: str = None):
    """记录任务执行日志"""
    completed_at = datetime.utcnow()
    duration = int((completed_at - started_at).total_seconds())
    
    log = ScheduledJobLog(
        job_id=job_id,
        job_name=job_name,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        duration_seconds=duration,
        result=result,
        error_message=error_message,
    )
    
    db.session.add(log)
    db.session.commit()


def daily_article_fetch():
    """每日文章抓取任务"""
    started_at = datetime.utcnow()
    job_id = 'daily_article_fetch'
    job_name = '每日文章抓取'
    
    logger.info("开始执行每日文章抓取任务")
    
    try:
        crawler = RSSCrawler(timeout=30, retry_times=3)
        
        # 获取所有启用的源
        sources = [
            src for src in Config.RSS_SOURCES 
            if src.get('enabled', True)
        ]
        
        total_found = 0
        total_new = 0
        all_articles = []
        
        for source in sources:
            try:
                result, articles = crawler.fetch_source(source)
                total_found += result['found']
                total_new += result['new']
                all_articles.extend(articles)
                
                logger.info(f"源 {source['name']}: 发现 {result['found']} 篇，新增 {result['new']} 篇")
                
            except Exception as e:
                logger.error(f"抓取源 {source['name']} 失败：{e}")
                continue
        
        # 将新文章加入 AI 队列
        articles_queued = 0
        for article in all_articles:
            try:
                from app.services.ai_queue import enqueue_article
                enqueue_article(
                    title=article['title'],
                    original_content=article['text_content'],
                    source_url=article['link'],
                    author=article.get('author'),
                    published_at=article.get('published'),
                )
                articles_queued += 1
            except Exception as e:
                logger.error(f"文章入队失败：{e}")
                continue
        
        result_msg = f"抓取完成：发现 {total_found} 篇，新增 {total_new} 篇，入队 {articles_queued} 篇"
        logger.info(result_msg)
        
        log_job_execution(
            job_id=job_id,
            job_name=job_name,
            status='success',
            started_at=started_at,
            result=result_msg,
        )
        
    except Exception as e:
        logger.error(f"每日文章抓取任务失败：{e}")
        log_job_execution(
            job_id=job_id,
            job_name=job_name,
            status='failed',
            started_at=started_at,
            error_message=str(e),
        )
        raise


def ai_queue_processor():
    """AI 队列处理任务"""
    started_at = datetime.utcnow()
    job_id = 'ai_queue_processor'
    job_name = 'AI 队列处理'
    
    logger.info("开始处理 AI 改写队列")
    
    try:
        # 处理队列中的所有任务
        result = process_queue_batch(batch_size=50)
        
        result_msg = f"队列处理完成：共处理 {result['processed']} 个，成功 {result['success']} 个，失败 {result['failed']} 个"
        logger.info(result_msg)
        
        log_job_execution(
            job_id=job_id,
            job_name=job_name,
            status='success',
            started_at=started_at,
            result=result_msg,
        )
        
    except Exception as e:
        logger.error(f"AI 队列处理任务失败：{e}")
        log_job_execution(
            job_id=job_id,
            job_name=job_name,
            status='failed',
            started_at=started_at,
            error_message=str(e),
        )
        raise


def cleanup_history():
    """清理历史数据（使用优化后的清理管理器）"""
    started_at = datetime.utcnow()
    job_id = 'cleanup_history'
    job_name = '清理历史数据'
    
    logger.info("开始清理历史数据")
    
    try:
        # 使用优化后的清理管理器
        from app.utils.db_optimization import CleanupManager
        
        # 清理 30 天前的记录
        CleanupManager.cleanup_old_records(days=30)
        
        # 数据库碎片整理（仅 SQLite）
        CleanupManager.vacuum_database()
        
        result_msg = "清理完成"
        logger.info(result_msg)
        
        log_job_execution(
            job_id=job_id,
            job_name=job_name,
            status='success',
            started_at=started_at,
            result=result_msg,
        )
        
    except Exception as e:
        logger.error(f"清理历史数据失败：{e}")
        log_job_execution(
            job_id=job_id,
            job_name=job_name,
            status='failed',
            started_at=started_at,
            error_message=str(e),
        )
        raise


def job_error_listener(event):
    """任务错误监听器"""
    if event.exception:
        logger.error(f"任务 {event.job_id} 执行失败：{event.traceback}")


def init_scheduler(app=None):
    """初始化定时任务调度器"""
    
    # 添加错误监听器
    from apscheduler.events import EVENT_JOB_ERROR
    scheduler.add_listener(job_error_listener, EVENT_JOB_ERROR)
    
    # 注册定时任务
    register_scheduled_jobs()
    
    # 启动调度器
    if not scheduler.running:
        scheduler.start()
        logger.info("定时任务调度器已启动")


def register_scheduled_jobs():
    """注册所有定时任务"""
    
    # 每日文章抓取 - 每天凌晨 2:00
    scheduler.add_job(
        func=daily_article_fetch,
        trigger=CronTrigger(hour=2, minute=0),
        id='daily_article_fetch',
        name='每日文章抓取',
        replace_existing=True,
        max_execution_time=3600,  # 最大执行时间 1 小时
    )
    
    # AI 队列处理 - 每天凌晨 2:30
    scheduler.add_job(
        func=ai_queue_processor,
        trigger=CronTrigger(hour=2, minute=30),
        id='ai_queue_processor',
        name='AI 队列处理',
        replace_existing=True,
        max_execution_time=7200,  # 最大执行时间 2 小时
    )
    
    # 清理历史数据 - 每周日凌晨 3:00
    scheduler.add_job(
        func=cleanup_history,
        trigger=CronTrigger(hour=3, minute=0, day_of_week='sun'),
        id='cleanup_history',
        name='清理历史数据',
        replace_existing=True,
        max_execution_time=1800,  # 最大执行时间 30 分钟
    )
    
    logger.info("定时任务已注册")


def get_jobs_status():
    """获取所有任务状态"""
    jobs = []
    
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
            'enabled': True,
        })
    
    return jobs


def trigger_job(job_id: str):
    """手动触发任务"""
    try:
        scheduler.get_job(job_id).modify()
        logger.info(f"手动触发任务：{job_id}")
        return True
    except Exception as e:
        logger.error(f"触发任务失败：{e}")
        return False


def enable_job(job_id: str):
    """启用任务"""
    try:
        scheduler.resume_job(job_id)
        return True
    except Exception as e:
        logger.error(f"启用任务失败：{e}")
        return False


def disable_job(job_id: str):
    """禁用任务"""
    try:
        scheduler.pause_job(job_id)
        return True
    except Exception as e:
        logger.error(f"禁用任务失败：{e}")
        return False
