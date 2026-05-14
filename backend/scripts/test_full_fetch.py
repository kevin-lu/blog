#!/usr/bin/env python3
"""
测试完整抓取流程
"""
import sys
sys.path.insert(0, '/Users/luzengbiao/traeProjects/blog/blog/backend')

from app import create_app
from app.extensions import db
from app.services.rss_crawler import RSSCrawler
from app.config import Config

app = create_app()

with app.app_context():
    print("=" * 60)
    print("测试完整抓取流程")
    print("=" * 60)
    
    # 获取 cnblogs 源配置
    cnblogs_source = None
    for src in Config.RSS_SOURCES:
        if src['name'] == 'cnblogs':
            cnblogs_source = src
            break
    
    if not cnblogs_source:
        print("❌ 找不到 cnblogs 源配置")
        sys.exit(1)
    
    print(f"\n源配置:")
    print(f"  名称：{cnblogs_source['name']}")
    print(f"  URL: {cnblogs_source['url']}")
    print(f"  启用：{cnblogs_source.get('enabled', True)}")
    print(f"  限制：{cnblogs_source.get('fetch_limit', 20)} 篇")
    
    print("\n开始抓取...")
    crawler = RSSCrawler(timeout=10, retry_times=2)
    
    try:
        result, articles = crawler.fetch_source(cnblogs_source)
        
        print("\n" + "=" * 60)
        print("抓取结果")
        print("=" * 60)
        print(f"发现：{result['found']} 篇")
        print(f"新增：{result['new']} 篇")
        print(f"重复：{result['duplicates']} 篇")
        print(f"错误：{result['errors']} 篇")
        
        if articles:
            print(f"\n前 3 篇文章:")
            for i, article in enumerate(articles[:3], 1):
                print(f"\n{i}. {article['title']}")
                print(f"   链接：{article['link']}")
                print(f"   作者：{article.get('author', 'N/A')}")
                print(f"   内容长度：{len(article.get('text_content', ''))} 字符")
        else:
            print("\n❌ 没有获取到任何文章！")
            
    except Exception as e:
        print(f"\n❌ 抓取失败：{e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
