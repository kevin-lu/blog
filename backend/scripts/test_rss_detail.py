#!/usr/bin/env python3
"""
测试 RSS 抓取详细日志
"""
import sys
sys.path.insert(0, '/Users/luzengbiao/traeProjects/blog/blog/backend')

import feedparser
import requests

def test_rss_source(name, url):
    print(f"\n{'='*60}")
    print(f"测试 RSS 源：{name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        # 1. 获取 RSS
        print("\n[1] 获取 RSS Feed...")
        response = requests.get(url, timeout=10)
        print(f"    状态码：{response.status_code}")
        print(f"    内容长度：{len(response.content)} bytes")
        
        if response.status_code != 200:
            print(f"    ❌ HTTP 错误：{response.status_code}")
            return
        
        # 2. 解析 RSS
        print("\n[2] 解析 RSS Feed...")
        feed = feedparser.parse(response.content)
        
        print(f"    Feed 标题：{feed.feed.get('title', 'Unknown')}")
        print(f"    Feed 链接：{feed.feed.get('link', 'N/A')}")
        print(f"    条目数量：{len(feed.entries)}")
        
        if feed.bozo:
            print(f"    ⚠️  解析警告：{feed.bozo_exception}")
        
        # 3. 检查条目
        if not feed.entries:
            print(f"    ❌ 没有条目！")
            return
        
        # 4. 显示前 3 个条目详情
        print(f"\n[3] 前 3 个条目详情:")
        for i, entry in enumerate(feed.entries[:3], 1):
            print(f"\n    条目 {i}:")
            print(f"        标题：{entry.get('title', 'N/A')[:80]}")
            print(f"        链接：{entry.get('link', 'N/A')[:80]}")
            print(f"        作者：{entry.get('author', 'N/A')}")
            print(f"        发布时间：{entry.get('published', 'N/A')}")
            
            # 检查内容字段
            content = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
            summary = entry.get('summary', '')
            description = entry.get('description', '')
            
            print(f"        内容长度：content={len(content)}, summary={len(summary)}, description={len(description)}")
            
    except Exception as e:
        print(f"    ❌ 错误：{e}")

# 测试多个 RSS 源
sources = [
    ('cnblogs', 'https://www.cnblogs.com/cmt/rss'),
    ('solidot', 'https://www.solidot.org/index.rss'),
    ('v2ex', 'https://www.v2ex.com/index.xml'),
]

for name, url in sources:
    test_rss_source(name, url)

print(f"\n{'='*60}")
print("测试完成")
print(f"{'='*60}")
