#!/usr/bin/env python3
"""
检查数据库中的抓取记录
"""
import sys
sys.path.insert(0, '/Users/luzengbiao/traeProjects/blog/blog/backend')

from app.extensions import db
from app import create_app
from app.models.crawler import CrawledURL, CrawledTitle

app = create_app()

with app.app_context():
    # 统计已抓取的 URL 数量
    url_count = CrawledURL.query.count()
    title_count = CrawledTitle.query.count()
    
    print("=" * 60)
    print("数据库抓取记录统计")
    print("=" * 60)
    print(f"已抓取的 URL 数量：{url_count}")
    print(f"已抓取的标题 MD5 数量：{title_count}")
    
    if url_count > 0:
        print("\n最近抓取的 10 个 URL:")
        urls = CrawledURL.query.order_by(CrawledURL.crawled_at.desc()).limit(10).all()
        for url in urls:
            print(f"  - {url.url[:80]} ({url.source})")
    
    print("=" * 60)
