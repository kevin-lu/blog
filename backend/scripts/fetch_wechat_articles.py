#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章列表抓取脚本
用于抓取"码哥跳动"公众号的文章列表
"""

import requests
import json
import re
from typing import List, Dict

def fetch_wechat_album():
    """
    抓取微信公众号文章合集
    """
    # 基础 URL
    base_url = "https://mp.weixin.qq.com/mp/appmsgalbum"
    
    params = {
        '__biz': 'MzkzMDI1NjcyOQ==',
        'action': 'getalbum',
        'album_id': '3022691668057276419',
        'scene': '126'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090923) XWEB/6945 Flue',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 保存 HTML 用于分析
        with open('wechat_album.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("✅ HTML 页面已保存到 wechat_album.html")
        
        # 尝试提取文章数据
        html_content = response.text
        
        # 查找文章列表
        articles = []
        
        # 方法 1: 尝试从 JSON 数据中提取
        json_pattern = r'var\s+msgList\s*=\s*({.*?});'
        matches = re.findall(json_pattern, html_content, re.DOTALL)
        
        if matches:
            print(f"\n找到 {len(matches)} 个 JSON 数据块")
            for i, match in enumerate(matches):
                try:
                    data = json.loads(match)
                    print(f"\n数据块 {i+1}:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
                except:
                    pass
        
        # 方法 2: 查找文章标题和链接
        article_pattern = r'<a[^>]*href="([^"]*mp\.weixin\.qq\.com/s/[^"]*)"[^>]*>\s*<span[^>]*>([^<]+)</span>'
        article_matches = re.findall(article_pattern, html_content, re.DOTALL)
        
        if article_matches:
            print(f"\n找到 {len(article_matches)} 篇文章:")
            for url, title in article_matches:
                articles.append({
                    'title': title.strip(),
                    'url': url
                })
                print(f"  - {title.strip()}")
        
        # 方法 3: 查找所有包含文章信息的 li 标签
        li_pattern = r'<li[^>]*class="[^"]*album__list-item[^"]*"[^>]*data-msgid="(\d+)"[^>]*data-itemidx="(\d+)"[^>]*data-link="([^"]*)"[^>]*data-title="([^"]*)"'
        li_matches = re.findall(li_pattern, html_content, re.DOTALL)
        
        if li_matches:
            print(f"\n找到 {len(li_matches)} 篇文章:")
            for msgid, itemidx, url, title in li_matches:
                articles.append({
                    'index': int(itemidx),
                    'title': title.strip(),
                    'url': url.replace('&amp;', '&'),
                    'msgid': msgid
                })
                print(f"  {itemidx}. {title.strip()}")
        
        # 按索引排序
        articles.sort(key=lambda x: x['index'])
        
        return articles
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败：{e}")
        return []
    except Exception as e:
        print(f"❌ 错误：{e}")
        return []

def main():
    print("开始抓取微信公众号文章列表...")
    print("=" * 60)
    
    articles = fetch_wechat_album()
    
    print("\n" + "=" * 60)
    print(f"共抓取到 {len(articles)} 篇文章")
    
    if articles:
        # 保存为 JSON
        with open('articles.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print("✅ 文章列表已保存到 articles.json")
        
        # 保存为 Markdown
        with open('articles.md', 'w', encoding='utf-8') as f:
            f.write("# 码哥跳动 - 文章列表\n\n")
            for i, article in enumerate(articles, 1):
                f.write(f"{i}. [{article['title']}]({article['url']})\n")
        print("✅ 文章列表已保存到 articles.md")

if __name__ == '__main__':
    main()
