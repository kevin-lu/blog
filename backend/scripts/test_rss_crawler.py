#!/usr/bin/env python3
"""
Test RSS Crawler
测试 RSS 抓取功能
"""
import sys
sys.path.insert(0, '/Users/luzengbiao/traeProjects/blog/blog/backend')

from app import create_app
from app.extensions import db
from app.services.rss_crawler import RSSCrawler
from app.services.ai_queue import get_queue_status, process_queue_batch
from app.config import Config

def test_rss_crawler():
    """测试 RSS 抓取"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("测试 RSS 抓取功能")
        print("=" * 60)
        
        crawler = RSSCrawler(timeout=30, retry_times=3)
        
        # 测试抓取博客园
        print("\n1. 测试抓取博客园 RSS...")
        try:
            cnblogs_source = [src for src in Config.RSS_SOURCES if src['name'] == 'cnblogs' and src.get('enabled', True)][0]
            result, articles = crawler.fetch_source(cnblogs_source)
            
            print(f"   发现：{result.get('found', 0)} 篇")
            print(f"   新增：{result.get('new', 0)} 篇")
            print(f"   重复：{result.get('duplicates', 0)} 篇")
            print(f"   错误：{result.get('errors', 0)} 篇")
            
            if articles:
                print(f"\n   前 3 篇文章:")
                for i, article in enumerate(articles[:3], 1):
                    print(f"   {i}. {article['title'][:60]}...")
            
        except Exception as e:
            print(f"   抓取失败：{e}")
            import traceback
            traceback.print_exc()
        
        # 测试队列状态
        print("\n2. 检查 AI 队列状态...")
        try:
            status = get_queue_status()
            print(f"   待处理：{status.get('pending', 0)}")
            print(f"   处理中：{status.get('processing', 0)}")
            print(f"   已完成：{status.get('completed', 0)}")
            print(f"   失败：{status.get('failed', 0)}")
        except Exception as e:
            print(f"   查询失败：{e}")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

if __name__ == '__main__':
    test_rss_crawler()
