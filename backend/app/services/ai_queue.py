"""
AI Queue Service
管理 AI 改写任务队列，串行处理改写请求
"""
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from app.extensions import db
from app.models.crawler import AIQueue, CrawlerTask
from app.models.article import Article
from app.services.ai_rewrite import MiniMaxClient, PROMPTS
from app.config import Config

logger = logging.getLogger(__name__)


def generate_queue_id() -> str:
    """生成队列 ID"""
    return f"ai_{uuid4().hex[:12]}"


def enqueue_article(
    title: str,
    original_content: str,
    source_url: str,
    author: str = None,
    published_at: datetime = None,
    priority: int = 0,
    rewrite_strategy: str = 'standard',
    template_type: str = 'tutorial',
    auto_publish: bool = False
) -> AIQueue:
    """
    将文章加入 AI 改写队列
    
    Args:
        title: 文章标题
        original_content: 原始内容
        source_url: 原文链接
        author: 作者
        published_at: 发布时间
        priority: 优先级
        rewrite_strategy: 改写策略
        template_type: 模板类型
        auto_publish: 是否自动发布
        
    Returns:
        队列项
    """
    queue_item = AIQueue(
        queue_id=generate_queue_id(),
        title=title,
        original_content=original_content,
        source_url=source_url,
        author=author,
        published_at=published_at,
        status='pending',
        priority=priority,
        max_retries=2,
        rewrite_strategy=rewrite_strategy,
    )
    
    # 保存模板类型和自动发布标志到 extra_data (如果需要)
    # 注意：AIQueue 模型目前没有 template_type 和 auto_publish 字段
    # 如果需要在队列处理时使用这些参数，需要添加到模型或者在处理时从其他地方获取
    
    db.session.add(queue_item)
    db.session.commit()
    
    logger.info(f"文章加入队列：{queue_item.queue_id}, 标题：{title[:50]}..., 策略：{rewrite_strategy}")
    
    # 检查队列是否积压
    check_queue_accumulation()
    
    return queue_item


def get_next_queue_task() -> Optional[AIQueue]:
    """
    获取下一个待处理的队列任务（优先级最高，时间最早）
    
    Returns:
        队列项，队列为空返回 None
    """
    task = AIQueue.query.filter_by(status='pending') \
        .order_by(AIQueue.priority.desc(), AIQueue.queued_at.asc()) \
        .first()
    
    return task


def process_ai_task(queue_item: AIQueue) -> bool:
    """
    处理单个 AI 改写任务
    
    Args:
        queue_item: 队列项
        
    Returns:
        True 表示成功，False 表示失败
    """
    try:
        # 更新状态
        queue_item.status = 'processing'
        queue_item.started_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"开始处理 AI 任务：{queue_item.queue_id}")
        
        # 调用 MiniMax AI 改写（串行，带延迟）
        # 使用队列中保存的改写策略
        strategy = queue_item.rewrite_strategy or 'standard'
        
        rewritten_content = call_minimax_ai_with_delay(
            title=queue_item.title,
            content=queue_item.original_content,
            strategy=strategy
        )
        
        if not rewritten_content:
            raise Exception("AI 改写返回空内容")
        
        # 创建文章并保存为草稿（不直接发布）
        article = create_and_save_draft(
            title=queue_item.title,
            content=rewritten_content,
            source_url=queue_item.source_url,
            author=queue_item.author,
            published_at=queue_item.published_at,
            ai_model='minimax-abab6.5',
            rewrite_strategy=strategy,
        )
        
        # 更新队列状态
        queue_item.status = 'completed'
        queue_item.article_id = article.id
        queue_item.rewritten_content = rewritten_content
        queue_item.ai_model = 'minimax-abab6.5'
        queue_item.rewrite_strategy = strategy
        queue_item.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"AI 任务完成：{queue_item.queue_id}, 文章 ID: {article.id}, 状态：草稿")
        
        return True
        
    except Exception as e:
        logger.error(f"AI 任务失败：{queue_item.queue_id}, 错误：{e}")
        
        # 失败重试逻辑
        queue_item.retry_count += 1
        if queue_item.retry_count >= queue_item.max_retries:
            queue_item.status = 'failed'
            queue_item.error_message = str(e)
            logger.error(f"AI 任务达到最大重试次数，标记为失败：{queue_item.queue_id}")
            
            # 发送告警
            from app.services.alert import send_ai_rewrite_error
            send_ai_rewrite_error(queue_item.queue_id, str(e), queue_item.retry_count)
        else:
            queue_item.status = 'pending'  # 重新加入队列
            logger.info(f"AI 任务失败，将重新加入队列（重试 {queue_item.retry_count}/{queue_item.max_retries}）: {queue_item.queue_id}")
        
        db.session.commit()
        return False


def call_minimax_ai_with_delay(title: str, content: str, strategy: str = 'standard', delay_seconds: int = 5) -> Optional[str]:
    """
    串行调用 MiniMax AI 进行文章改写（带延迟避免限流）
    
    Args:
        title: 文章标题
        content: 文章内容
        strategy: 改写策略
        delay_seconds: 延迟秒数
        
    Returns:
        改写后的内容，失败返回 None
    """
    # 添加延迟，避免触发 API 限流
    logger.info(f"延迟 {delay_seconds} 秒后调用 MiniMax AI...")
    time.sleep(delay_seconds)
    
    try:
        # 使用 MiniMaxClient 直接调用
        client = MiniMaxClient(
            api_key=Config.MINIMAX_API_KEY,
            model=Config.MINIMAX_MODEL,
            base_url=Config.MINIMAX_API_HOST,
            request_timeout=Config.MINIMAX_REQUEST_TIMEOUT,
            max_retries=Config.MINIMAX_MAX_RETRIES,
        )
        
        prompts = PROMPTS.get(strategy) or PROMPTS['standard']
        result = client.rewrite_article(
            content=content,
            prompts=prompts,
            original_title=title,
        )
        
        rewritten = result.get('rewritten_content', '')
        logger.info(f"MiniMax AI 改写成功，字数：{len(rewritten)}")
        return rewritten
            
    except Exception as e:
        logger.error(f"调用 MiniMax AI 异常：{e}")
        return None


def create_and_save_draft(
    title: str,
    content: str,
    source_url: str,
    author: str = None,
    published_at: datetime = None,
    ai_model: str = 'minimax-abab6.5',
    rewrite_strategy: str = 'standard',
) -> Article:
    """
    创建文章并保存为草稿（不直接发布）
    
    Args:
        title: 文章标题
        content: 文章内容
        source_url: 原文链接
        author: 作者
        published_at: 发布时间
        ai_model: AI 模型
        rewrite_strategy: 改写策略
        
    Returns:
        创建的文章（草稿状态）
    """
    from app.utils.slug import generate_slug
    
    # 生成 slug
    slug = generate_slug(title)
    
    # 检查 slug 是否已存在，如果存在则添加时间戳
    existing = Article.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # 创建文章（保存为草稿）
    article = Article(
        slug=slug,
        title=title,
        content=content,
        source_url=source_url,
        ai_generated=1,
        ai_model=ai_model,
        rewrite_strategy=rewrite_strategy,
        template_type='tutorial',
        word_count=len(content),
        status='draft',  # 保存为草稿，不直接发布
        published_at=None,  # 草稿不设置发布时间
    )
    
    db.session.add(article)
    db.session.commit()
    
    logger.info(f"文章已创建并保存为草稿：{article.id}, slug: {slug}, 标题：{title}")
    
    return article


def process_queue_batch(batch_size: int = 10) -> Dict:
    """
    批量处理队列中的任务
    
    Args:
        batch_size: 处理数量
        
    Returns:
        处理结果统计
    """
    result = {
        'processed': 0,
        'success': 0,
        'failed': 0,
    }
    
    for i in range(batch_size):
        task = get_next_queue_task()
        if not task:
            logger.info("队列为空，停止处理")
            break
        
        result['processed'] += 1
        
        if process_ai_task(task):
            result['success'] += 1
        else:
            result['failed'] += 1
    
    logger.info(f"批量处理完成：共处理 {result['processed']} 个，成功 {result['success']} 个，失败 {result['failed']} 个")
    
    return result


def get_queue_status() -> Dict:
    """
    获取队列状态
    
    Returns:
        队列统计信息
    """
    pending_count = AIQueue.query.filter_by(status='pending').count()
    processing_count = AIQueue.query.filter_by(status='processing').count()
    completed_count = AIQueue.query.filter_by(status='completed').count()
    failed_count = AIQueue.query.filter_by(status='failed').count()
    
    # 估算处理时间（假设每个任务平均 10 秒）
    estimated_time_minutes = pending_count * 10 / 60
    
    return {
        'pending': pending_count,
        'processing': processing_count,
        'completed': completed_count,
        'failed': failed_count,
        'estimated_time_minutes': round(estimated_time_minutes, 1),
    }


def retry_failed_task(queue_id: str) -> bool:
    """
    重试失败的任务
    
    Args:
        queue_id: 队列 ID
        
    Returns:
        True 表示成功重新加入队列
    """
    task = AIQueue.query.filter_by(queue_id=queue_id).first()
    if not task:
        logger.error(f"未找到队列任务：{queue_id}")
        return False
    
    if task.status != 'failed':
        logger.warning(f"任务状态不是 failed：{queue_id}, 当前状态：{task.status}")
        return False
    
    # 重置状态
    task.status = 'pending'
    task.retry_count = 0
    task.error_message = None
    task.started_at = None
    
    db.session.commit()
    
    logger.info(f"失败任务已重新加入队列：{queue_id}")
    
    return True


def check_queue_accumulation():
    """检查队列是否积压，如积压发送告警"""
    try:
        pending_count = AIQueue.query.filter_by(status='pending').count()
        
        # 获取配置阈值
        from app.config import Config
        threshold = Config.ALERT_QUEUE_THRESHOLD or 10
        
        if pending_count > threshold:
            # 估算处理时间（每篇 5 分钟）
            estimated_time = pending_count * 5.0 / 60.0
            
            from app.services.alert import send_queue_accumulation
            send_queue_accumulation(pending_count, estimated_time)
            
    except Exception as e:
        logger.error(f"检查队列积压失败：{e}")
