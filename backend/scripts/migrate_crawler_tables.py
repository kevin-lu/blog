#!/usr/bin/env python3
"""
Database Migration for Crawler Tables
创建爬虫相关数据库表
"""
import sys
sys.path.insert(0, '/Users/luzengbiao/traeProjects/blog/blog/backend')

from app import create_app, db
from app.models.crawler import CrawledURL, CrawledTitle, CrawlerTask, AIQueue, ScheduledJobLog

def migrate():
    """创建爬虫相关数据库表"""
    app = create_app()
    
    with app.app_context():
        print("正在创建数据库表...")
        
        # 创建所有爬虫相关表
        db.create_all()
        
        print("✓ 数据库表创建成功！")
        print("\n已创建的表:")
        print("  - crawled_urls (已抓取 URL 记录)")
        print("  - crawled_titles (已抓取标题 MD5 记录)")
        print("  - crawler_tasks (抓取任务记录)")
        print("  - ai_queue (AI 改写队列)")
        print("  - scheduled_job_logs (定时任务执行日志)")

if __name__ == '__main__':
    migrate()
