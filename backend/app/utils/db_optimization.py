"""
Database Optimization Utilities
数据库性能优化工具 - 批量操作、查询优化、索引管理
"""
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import text
from app.extensions import db
from app.models.crawler import CrawledURL, CrawledTitle, AIQueue, CrawlerTask

logger = logging.getLogger(__name__)


class BatchInserter:
    """批量插入工具类"""
    
    @staticmethod
    def bulk_insert_crawled_urls(urls: List[Dict[str, Any]], batch_size: int = 100):
        """
        批量插入已抓取 URL 记录
        
        Args:
            urls: URL 数据列表 [{'url': '...', 'title_md5': '...', 'source': '...'}]
            batch_size: 每批次数量
        """
        if not urls:
            return
        
        logger.info(f"开始批量插入 {len(urls)} 条 URL 记录...")
        
        # 分批插入
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            
            # 构建插入数据
            insert_data = []
            for item in batch:
                insert_data.append({
                    'url': item['url'],
                    'title_md5': item['title_md5'],
                    'source': item.get('source', 'unknown'),
                    'crawled_at': datetime.utcnow(),
                })
            
            # 批量插入
            if insert_data:
                db.session.bulk_insert_mappings(CrawledURL, insert_data)
                db.session.commit()
                logger.info(f"已插入 {i + len(batch)}/{len(urls)} 条记录")
        
        logger.info(f"批量插入完成，共 {len(urls)} 条记录")
    
    @staticmethod
    def bulk_insert_crawled_titles(titles: List[Dict[str, Any]], batch_size: int = 100):
        """
        批量插入已抓取标题 MD5
        
        Args:
            titles: 标题数据列表 [{'title': '...', 'title_md5': '...'}]
            batch_size: 每批次数量
        """
        if not titles:
            return
        
        logger.info(f"开始批量插入 {len(titles)} 条标题记录...")
        
        for i in range(0, len(titles), batch_size):
            batch = titles[i:i + batch_size]
            
            insert_data = []
            for item in batch:
                insert_data.append({
                    'title': item['title'],
                    'title_md5': item['title_md5'],
                    'created_at': datetime.utcnow(),
                })
            
            if insert_data:
                db.session.bulk_insert_mappings(CrawledTitle, insert_data)
                db.session.commit()
                logger.info(f"已插入 {i + len(batch)}/{len(titles)} 条记录")
        
        logger.info(f"批量插入完成，共 {len(titles)} 条记录")


class QueryOptimizer:
    """查询优化工具类"""
    
    @staticmethod
    def check_duplicate_batch(url_title_pairs: List[tuple]) -> Dict[str, bool]:
        """
        批量检查重复（URL + 标题）
        
        Args:
            url_title_pairs: [(url, title_md5), ...]
            
        Returns:
            {'url_md5': True/False, ...}  True 表示重复
        """
        if not url_title_pairs:
            return {}
        
        # 提取所有 URL 和 MD5
        urls = [pair[0] for pair in url_title_pairs]
        title_md5s = [pair[1] for pair in url_title_pairs]
        
        # 批量查询已存在的 URL
        existing_urls = set()
        if urls:
            result = db.session.query(CrawledURL.url).filter(
                CrawledURL.url.in_(urls)
            ).all()
            existing_urls = {row[0] for row in result}
        
        # 批量查询已存在的标题 MD5
        existing_titles = set()
        if title_md5s:
            result = db.session.query(CrawledTitle.title_md5).filter(
                CrawledTitle.title_md5.in_(title_md5s)
            ).all()
            existing_titles = {row[0] for row in result}
        
        # 构建结果
        duplicates = {}
        for url, title_md5 in url_title_pairs:
            key = url
            is_duplicate = url in existing_urls or title_md5 in existing_titles
            duplicates[key] = is_duplicate
        
        return duplicates
    
    @staticmethod
    def get_queue_items_by_status(status: str, limit: int = 100, offset: int = 0) -> List[AIQueue]:
        """
        分页获取队列项（带索引优化）
        
        Args:
            status: 状态
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            队列项列表
        """
        items = AIQueue.query.filter_by(status=status) \
            .order_by(AIQueue.priority.desc(), AIQueue.queued_at.asc()) \
            .limit(limit) \
            .offset(offset) \
            .all()
        
        return items
    
    @staticmethod
    def get_queue_statistics() -> Dict:
        """
        获取队列统计信息（使用聚合查询）
        
        Returns:
            统计信息字典
        """
        from sqlalchemy import func
        
        # 按状态分组统计
        status_stats = db.session.query(
            AIQueue.status,
            func.count(AIQueue.id).label('count'),
            func.sum(AIQueue.token_usage).label('total_tokens'),
        ).group_by(AIQueue.status).all()
        
        stats = {
            'total': 0,
            'pending': 0,
            'processing': 0,
            'completed': 0,
            'failed': 0,
            'total_tokens': 0,
        }
        
        for row in status_stats:
            status = row[0]
            count = row[1]
            tokens = row[2] or 0
            
            stats['total'] += count
            stats[status] = count
            if status == 'completed':
                stats['total_tokens'] += tokens
        
        # 获取最近处理时间
        last_processed = db.session.query(AIQueue.completed_at).filter_by(
            status='completed'
        ).order_by(AIQueue.completed_at.desc()).first()
        
        stats['last_processed_at'] = last_processed[0] if last_processed else None
        
        return stats


class IndexManager:
    """索引管理工具类"""
    
    @staticmethod
    def check_missing_indexes():
        """检查缺失的索引"""
        inspector = db.inspect(db.engine)
        
        # 预期索引列表
        expected_indexes = {
            'crawled_url': ['url', 'title_md5', 'source'],
            'crawled_title': ['title_md5'],
            'ai_queue': ['status', 'priority', 'queued_at', 'queue_id'],
            'crawler_task': ['task_id', 'created_at'],
        }
        
        missing_indexes = []
        
        for table_name, columns in expected_indexes.items():
            if table_name not in inspector.get_table_names():
                continue
            
            indexes = inspector.get_indexes(table_name)
            indexed_columns = set()
            for idx in indexes:
                for col in idx.get('column_names', []):
                    indexed_columns.add(col)
            
            for col in columns:
                if col not in indexed_columns:
                    missing_indexes.append(f"{table_name}.{col}")
        
        if missing_indexes:
            logger.warning(f"发现缺失的索引：{missing_indexes}")
        else:
            logger.info("所有预期索引都存在")
        
        return missing_indexes
    
    @staticmethod
    def create_recommend_indexes():
        """创建推荐的索引"""
        logger.info("创建推荐索引...")
        
        # 执行索引创建 SQL（MySQL 不支持 IF NOT EXISTS，需要捕获异常）
        indexes_sql = [
            "CREATE INDEX idx_crawled_url_url ON crawled_url(url)",
            "CREATE INDEX idx_crawled_url_title_md5 ON crawled_url(title_md5)",
            "CREATE INDEX idx_crawled_url_source ON crawled_url(source)",
            "CREATE INDEX idx_crawled_title_md5 ON crawled_title(title_md5)",
            "CREATE INDEX idx_ai_queue_status ON ai_queue(status)",
            "CREATE INDEX idx_ai_queue_priority ON ai_queue(priority)",
            "CREATE INDEX idx_ai_queue_queued_at ON ai_queue(queued_at)",
            "CREATE INDEX idx_ai_queue_queue_id ON ai_queue(queue_id)",
            "CREATE INDEX idx_crawler_task_task_id ON crawler_task(task_id)",
            "CREATE INDEX idx_crawler_task_created_at ON crawler_task(created_at)",
        ]
        
        for sql in indexes_sql:
            try:
                db.session.execute(text(sql))
                db.session.commit()
                logger.info(f"索引创建成功：{sql}")
            except Exception as e:
                # 如果索引已存在，忽略错误
                if 'Duplicate key name' in str(e) or 'already exists' in str(e):
                    logger.debug(f"索引已存在：{sql}")
                else:
                    logger.error(f"索引创建失败：{sql}, 错误：{e}")
                    db.session.rollback()
        
        logger.info("索引创建完成")
    
    @staticmethod
    def analyze_table_sizes():
        """分析表大小"""
        inspector = db.inspect(db.engine)
        
        table_sizes = {}
        for table_name in inspector.get_table_names():
            if table_name.startswith('alembic'):
                continue
            
            count = db.session.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar()
            
            table_sizes[table_name] = count
        
        # 按大小排序
        sorted_tables = sorted(table_sizes.items(), key=lambda x: x[1], reverse=True)
        
        logger.info("表大小统计:")
        for table_name, count in sorted_tables:
            logger.info(f"  {table_name}: {count} 条记录")
        
        return table_sizes


class CleanupManager:
    """数据清理工具类"""
    
    @staticmethod
    def cleanup_old_records(days: int = 30):
        """
        清理旧记录
        
        Args:
            days: 保留天数
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        logger.info(f"开始清理 {days} 天前的数据...")
        
        # 清理 CrawledURL
        deleted = db.session.query(CrawledURL).filter(
            CrawledURL.crawled_at < cutoff_date
        ).delete(synchronize_session=False)
        logger.info(f"清理 CrawledURL: {deleted} 条")
        
        # 清理 CrawledTitle
        deleted = db.session.query(CrawledTitle).filter(
            CrawledTitle.created_at < cutoff_date
        ).delete(synchronize_session=False)
        logger.info(f"清理 CrawledTitle: {deleted} 条")
        
        # 清理已完成的队列项（保留最近 7 天）
        deleted = db.session.query(AIQueue).filter(
            AIQueue.status == 'completed',
            AIQueue.completed_at < datetime.utcnow() - timedelta(days=7)
        ).delete(synchronize_session=False)
        logger.info(f"清理 AIQueue: {deleted} 条")
        
        # 清理旧的任务记录（保留最近 30 天）
        deleted = db.session.query(CrawlerTask).filter(
            CrawlerTask.created_at < cutoff_date
        ).delete(synchronize_session=False)
        logger.info(f"清理 CrawlerTask: {deleted} 条")
        
        db.session.commit()
        
        logger.info("数据清理完成")
    
    @staticmethod
    def vacuum_database():
        """数据库碎片整理（仅 SQLite）"""
        try:
            db.session.execute(text("VACUUM"))
            db.session.commit()
            logger.info("数据库碎片整理完成")
        except Exception as e:
            logger.error(f"数据库碎片整理失败：{e}")
            db.session.rollback()
