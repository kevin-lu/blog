"""
Scheduler API Routes
定时任务管理相关接口
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services import scheduler as scheduler_service

bp = Blueprint('scheduler', __name__)


@bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    """
    获取所有定时任务列表
    
    Returns:
        定时任务列表
    """
    try:
        jobs = scheduler_service.scheduler.get_jobs()
        
        job_list = []
        for job in jobs:
            job_info = {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'enabled': job.next_run_time is not None,
            }
            
            job_list.append(job_info)
        
        return jsonify(job_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/trigger/<job_id>', methods=['POST'])
@jwt_required()
def trigger_job(job_id):
    """
    手动触发定时任务
    
    Args:
        job_id: 任务 ID
        
    Returns:
        触发结果
    """
    try:
        # 检查任务是否存在
        job = scheduler_service.scheduler.get_job(job_id)
        
        if not job:
            return jsonify({'error': f'任务不存在：{job_id}'}), 404
        
        # 手动触发任务
        job.modify(next_run_time=None)  # 清除下次运行时间，立即执行
        
        # 直接调用任务函数
        if job_id == 'daily_article_fetch':
            from app.services.rss_crawler import RSSCrawler, create_crawler_task
            from app.services.ai_queue import enqueue_article
            from app.config import Config
            
            crawler = RSSCrawler(timeout=30, retry_times=3)
            sources = [src for src in Config.RSS_SOURCES if src.get('enabled', True)]
            
            total_found = 0
            total_new = 0
            all_articles = []
            
            for source in sources:
                try:
                    result, articles = crawler.fetch_source(source)
                    total_found += result['found']
                    total_new += result['new']
                    all_articles.extend(articles)
                except Exception as e:
                    continue
            
            # 创建任务记录
            task_id = create_crawler_task('manual', total_found, total_new)
            
            # 将文章加入 AI 队列
            articles_queued = 0
            for article in all_articles:
                try:
                    enqueue_article(
                        title=article['title'],
                        original_content=article['text_content'],
                        source_url=article['link'],
                        author=article.get('author'),
                        published_at=article.get('published'),
                    )
                    articles_queued += 1
                except Exception as e:
                    continue
            
            return jsonify({
                'message': '任务执行成功',
                'stats': {
                    'found': total_found,
                    'new': total_new,
                    'queued': articles_queued,
                }
            }), 200
            
        elif job_id == 'ai_queue_processor':
            from app.services.ai_queue import process_queue_batch
            
            # 处理所有待处理的队列项
            result = process_queue_batch(count=100)
            
            return jsonify({
                'message': '队列处理成功',
                'processed': result.get('processed', 0),
                'success': result.get('success', 0),
                'failed': result.get('failed', 0),
            }), 200
            
        elif job_id == 'cleanup_history':
            from app.models.crawler import CrawlerTask
            from app.extensions import db
            from datetime import datetime, timedelta
            
            # 清理 30 天前的历史记录
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            deleted = CrawlerTask.query.filter(
                CrawlerTask.created_at < cutoff_date
            ).delete(synchronize_session=False)
            
            db.session.commit()
            
            return jsonify({
                'message': '清理成功',
                'deleted': deleted,
            }), 200
        
        else:
            return jsonify({'error': f'不支持的任务类型：{job_id}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/toggle/<job_id>', methods=['POST'])
@jwt_required()
def toggle_job(job_id):
    """
    切换定时任务启用状态
    
    Args:
        job_id: 任务 ID
        
    Request Body:
        enabled: bool - 是否启用
        
    Returns:
        操作结果
    """
    try:
        data = request.get_json() or {}
        enabled = data.get('enabled', True)
        
        job = scheduler.get_job(job_id)
        
        if not job:
            return jsonify({'error': f'任务不存在：{job_id}'}), 404
        
        if enabled:
            # 启用任务 - 恢复原来的调度
            from apscheduler.triggers.cron import CronTrigger
            
            if job_id == 'daily_article_fetch':
                trigger = CronTrigger(hour=2, minute=0)
            elif job_id == 'ai_queue_processor':
                trigger = CronTrigger(hour=2, minute=30)
            elif job_id == 'cleanup_history':
                trigger = CronTrigger(day_of_week='sun', hour=3, minute=0)
            else:
                return jsonify({'error': f'未知的任务：{job_id}'}), 404
            
            scheduler_service.scheduler.reschedule_job(job_id, trigger=trigger)
            message = '任务已启用'
        else:
            # 禁用任务 - 暂停执行
            scheduler_service.scheduler.pause_job(job_id)
            message = '任务已禁用'
        
        return jsonify({
            'message': message,
            'job_id': job_id,
            'enabled': enabled,
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
