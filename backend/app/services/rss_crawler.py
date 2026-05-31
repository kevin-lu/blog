"""
RSS Crawler Service
从 RSS 源抓取技术文章
"""
import hashlib
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

import feedparser
from app.extensions import db
from app.models.crawler import CrawledURL, CrawledTitle, CrawlerTask
from app.models.article import Article

logger = logging.getLogger(__name__)


class RSSCrawler:
    """RSS 爬虫服务"""
    
    def __init__(self, timeout: int = 10, retry_times: int = 2):
        self.timeout = timeout
        self.retry_times = retry_times
    
    def fetch_feed(self, url: str) -> Optional[Dict]:
        """
        获取并解析 RSS Feed
        
        Args:
            url: RSS Feed URL
            
        Returns:
            解析后的 Feed 数据，失败返回 None
        """
        import requests
        
        for attempt in range(self.retry_times):
            try:
                logger.info(f"获取 RSS Feed: {url} (尝试 {attempt + 1}/{self.retry_times})")
                
                # 先使用 requests 获取（支持 timeout）
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # 再使用 feedparser 解析
                feed = feedparser.parse(response.content)
                
                if feed.bozo:
                    logger.warning(f"RSS 解析警告：{feed.bozo_exception}")
                
                if not feed.entries:
                    logger.warning(f"RSS Feed 没有条目：{url}")
                    return None
                
                return {
                    'title': feed.feed.get('title', 'Unknown'),
                    'link': feed.feed.get('link', url),
                    'description': feed.feed.get('description', ''),
                    'entries': feed.entries
                }
                
            except Exception as e:
                logger.error(f"获取 RSS Feed 失败 (尝试 {attempt + 1}): {e}")
                if attempt == self.retry_times - 1:
                    return None
        
        return None
    
    def clean_content(self, html_content: str) -> str:
        """
        清洗 HTML 内容
        
        Args:
            html_content: 原始 HTML 内容
            
        Returns:
            清洗后的内容
        """
        if not html_content:
            return ''
        
        # 移除 script 和 style 标签
        content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # 移除其他不需要的标签，保留 p, code, pre
        content = re.sub(r'<(?!/?(p|code|pre|br))[^>]+>', '', content, flags=re.IGNORECASE)
        
        # 移除 HTML 注释
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        # 解码 HTML 实体
        content = re.sub(r'&nbsp;', ' ', content)
        content = re.sub(r'&lt;', '<', content)
        content = re.sub(r'&gt;', '>', content)
        content = re.sub(r'&amp;', '&', content)
        content = re.sub(r'&quot;', '"', content)
        
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def extract_text_from_html(self, html_content: str) -> str:
        """
        从 HTML 提取纯文本（用于 AI 改写）
        
        Args:
            html_content: HTML 内容
            
        Returns:
            纯文本内容
        """
        if not html_content:
            return ''
        
        # 移除所有 HTML 标签
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # 解码 HTML 实体
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'&amp;', '&', text)
        
        # 清理空白
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def check_duplicate(self, url: str, title: str) -> bool:
        """
        检查文章是否重复
        
        Args:
            url: 文章 URL
            title: 文章标题
            
        Returns:
            True 表示重复，False 表示不重复
        """
        # URL 去重
        existing_url = CrawledURL.query.filter_by(url=url).first()
        if existing_url:
            logger.info(f"URL 重复，跳过：{url}")
            return True
        
        # 标题 MD5 去重
        title_md5 = hashlib.md5(title.encode('utf-8')).hexdigest()
        existing_title = CrawledTitle.query.filter_by(title_md5=title_md5).first()
        if existing_title:
            logger.info(f"标题重复，跳过：{title}")
            return True
        
        # 检查是否已存在于文章表
        existing_article = Article.query.filter_by(source_url=url).first()
        if existing_article:
            logger.info(f"文章已存在，跳过：{url}")
            return True
        
        return False
    
    def record_crawled(self, url: str, title: str, source: str):
        """
        记录已抓取的文章
        
        Args:
            url: 文章 URL
            title: 文章标题
            source: 来源名称
        """
        # 记录 URL
        crawled_url = CrawledURL(url=url, title=title, source=source)
        db.session.add(crawled_url)
        
        # 记录标题 MD5
        title_md5 = hashlib.md5(title.encode('utf-8')).hexdigest()
        crawled_title = CrawledTitle(title_md5=title_md5, original_title=title)
        db.session.add(crawled_title)
        
        db.session.commit()
    
    def record_crawled_batch(self, articles: List[Dict], source: str):
        """
        批量记录已抓取的文章（性能优化）
        
        Args:
            articles: 文章数据列表
            source: 来源名称
        """
        if not articles:
            return
        
        from app.utils.db_optimization import BatchInserter
        
        # 准备批量数据
        urls_data = []
        titles_data = []
        
        for article in articles:
            title_md5 = hashlib.md5(article['title'].encode('utf-8')).hexdigest()
            
            urls_data.append({
                'url': article['link'],
                'title_md5': title_md5,
                'source': source,
            })
            
            titles_data.append({
                'title': article['title'],
                'title_md5': title_md5,
            })
        
        # 批量插入
        BatchInserter.bulk_insert_crawled_urls(urls_data)
        BatchInserter.bulk_insert_crawled_titles(titles_data)
    
    def parse_entry(self, entry: Dict, source: str) -> Optional[Dict]:
        """
        解析 RSS 条目
        
        Args:
            entry: RSS 条目
            source: 来源名称
            
        Returns:
            标准化的文章数据，解析失败返回 None
        """
        try:
            # 获取标题
            title = entry.get('title', '').strip()
            if not title:
                logger.warning("文章缺少标题，跳过")
                return None
            
            # 获取链接
            link = entry.get('link', '').strip()
            if not link:
                logger.warning("文章缺少链接，跳过")
                return None
            
            # 获取内容（不同 RSS 源可能使用不同字段）
            content = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
            if not content:
                content = entry.get('summary', '')
            if not content:
                content = entry.get('description', '')
            
            # 获取作者
            author = entry.get('author', '')
            if not author:
                author = entry.get('dc_creator', '')
            
            # 获取发布时间
            published = None
            published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
            if published_parsed:
                try:
                    published = datetime(*published_parsed[:6])
                except:
                    published = datetime.utcnow()
            else:
                published = datetime.utcnow()
            
            # 获取标签
            tags = []
            for tag in entry.get('tags', []):
                tag_term = tag.get('term', '')
                if tag_term:
                    tags.append(tag_term)
            
            # 计算标题 MD5（用于去重）
            title_md5 = hashlib.md5(title.encode('utf-8')).hexdigest()
            
            return {
                'title': title,
                'title_md5': title_md5,
                'link': link,
                'content': content,
                'cleaned_content': self.clean_content(content),
                'text_content': self.extract_text_from_html(content),
                'author': author,
                'published': published,
                'tags': tags,
                'source': source,
            }
            
        except Exception as e:
            logger.error(f"解析 RSS 条目失败：{e}")
            return None
    
    def fetch_source(self, source_config: Dict) -> Dict:
        """
        抓取单个 RSS 源
        
        Args:
            source_config: 源配置 {'name': 'juejin', 'url': '...', 'enabled': True, 'fetch_limit': 20}
            
        Returns:
            抓取结果统计
        """
        source_name = source_config['name']
        source_url = source_config['url']
        fetch_limit = source_config.get('fetch_limit', 20)
        
        logger.info(f"开始抓取源：{source_name} ({source_url})")
        
        result = {
            'source': source_name,
            'found': 0,
            'new': 0,
            'duplicates': 0,
            'errors': 0,
        }
        
        # 获取 Feed
        feed_data = self.fetch_feed(source_url)
        if not feed_data:
            logger.error(f"抓取源失败：{source_name}")
            result['errors'] = 1
            
            # 发送告警
            from app.services.alert import send_crawler_error
            send_crawler_error(source_name, "无法获取 RSS Feed，请检查网络连接或 RSS 地址")
            
            return result
        
        logger.info(f"Feed 获取成功：{len(feed_data.get('entries', []))} 个条目")
        
        # 处理条目 - 性能优化：批量去重检查
        articles = []
        url_title_pairs = []
        
        # 先收集所有文章的 URL 和标题 MD5
        for entry in feed_data['entries'][:fetch_limit]:
            article_data = self.parse_entry(entry, source_name)
            
            if not article_data:
                result['errors'] += 1
                logger.debug(f"解析失败，跳过")
                continue
            
            result['found'] += 1
            url_title_pairs.append((article_data['link'], article_data['title_md5']))
            articles.append(article_data)
        
        logger.info(f"解析完成：{result['found']} 篇有效文章")
        
        # 批量去重检查
        if url_title_pairs:
            from app.utils.db_optimization import QueryOptimizer
            duplicates = QueryOptimizer.check_duplicate_batch(url_title_pairs)
            logger.info(f"去重检查：{len(duplicates)} 篇重复")
            
            # 处理非重复文章
            new_articles = []
            for article_data in articles:
                is_duplicate = duplicates.get(article_data['link'], False)
                
                if is_duplicate:
                    result['duplicates'] += 1
                    logger.debug(f"URL 重复，跳过：{article_data['link']}")
                else:
                    result['new'] += 1
                    new_articles.append(article_data)
                    logger.info(f"抓取新文章：{article_data['title'][:50]}...")
            
            # 批量记录已抓取
            if new_articles:
                self.record_crawled_batch(new_articles, source_name)
        
        logger.info(f"源 {source_name} 抓取完成：发现 {result['found']} 篇，新增 {result['new']} 篇，重复 {result['duplicates']} 篇")
        
        return result, articles


def create_crawler_task(source: str, articles_found: int, articles_new: int) -> str:
    """
    创建抓取任务记录
    
    Args:
        source: 来源名称
        articles_found: 发现的文章数
        articles_new: 新增的文章数
        
    Returns:
        任务 ID
    """
    task_id = f"fetch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
    
    task = CrawlerTask(
        task_id=task_id,
        source=source,
        status='processing',
        articles_found=articles_found,
        articles_new=articles_new,
    )
    
    db.session.add(task)
    db.session.commit()
    
    return task_id


def update_crawler_task(task_id: str, status: str, articles_queued: int = None, error_message: str = None):
    """
    更新抓取任务状态
    
    Args:
        task_id: 任务 ID
        status: 新状态
        articles_queued: 加入队列的文章数
        error_message: 错误信息
    """
    task = CrawlerTask.query.filter_by(task_id=task_id).first()
    if not task:
        return
    
    task.status = status
    if articles_queued is not None:
        task.articles_queued = articles_queued
    if error_message:
        task.error_message = error_message
    
    if status in ['completed', 'failed']:
        task.completed_at = datetime.utcnow()
    
    db.session.commit()
