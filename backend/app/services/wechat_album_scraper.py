"""
Wechat Album Scraper
抓取微信公众号文章合集列表
"""
import re
from typing import Dict, List, Optional
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup


class WechatAlbumScraper:
    """微信公众号合集抓取器"""
    
    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48'
        ),
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://mp.weixin.qq.com/',
    }
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def fetch_album_info(self, album_url: str) -> Optional[Dict]:
        """
        抓取合集基本信息
        
        Args:
            album_url: 合集链接
            
        Returns:
            合集信息：{name, total_count, description, cover_image}
        """
        try:
            response = self.session.get(album_url, timeout=self.timeout)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取合集名称
            name_elem = soup.find('div', {'id': 'js_tag_name'})
            name = name_elem.get_text(strip=True) if name_elem else '未知合集'
            
            # 提取文章总数
            count_text = soup.find('span', string=re.compile(r'\d+\s*篇'))
            total_count = 0
            if count_text:
                match = re.search(r'(\d+)', count_text.get_text())
                if match:
                    total_count = int(match.group(1))
            
            # 提取描述
            desc_elem = soup.find('meta', {'name': 'description'})
            description = desc_elem.get('content', '') if desc_elem else ''
            
            # 提取封面图
            cover_elem = soup.find('img', {'id': 'js_header_image'})
            cover_image = cover_elem.get('src', '') if cover_elem else ''
            
            return {
                'name': name,
                'total_count': total_count,
                'description': description,
                'cover_image': cover_image,
            }
            
        except Exception as e:
            print(f"抓取合集信息失败：{e}")
            return None
    
    def fetch_article_list(self, album_url: str) -> List[Dict]:
        """
        抓取合集文章列表
        
        Args:
            album_url: 合集链接
            
        Returns:
            文章列表：[{title, url, digest, cover_image}]
        """
        try:
            response = self.session.get(album_url, timeout=self.timeout)
            response.raise_for_status()
            
            html = response.text
            
            # 使用正则提取文章列表
            pattern = r'<li[^>]*class="[^"]*album__list-item[^"]*"[^>]*' \
                     r'data-msgid="(\d+)"[^>]*data-itemidx="(\d+)"[^>]*' \
                     r'data-link="([^"]*)"[^>]*data-title="([^"]*)"'
            
            matches = re.findall(pattern, html, re.DOTALL)
            
            articles = []
            for msgid, itemidx, url, title in matches:
                articles.append({
                    'index': int(itemidx),
                    'title': self._decode_html_entities(title),
                    'url': self._clean_url(url),
                    'msgid': msgid,
                })
            
            # 按索引排序
            articles.sort(key=lambda x: x['index'])
            
            return articles
            
        except Exception as e:
            print(f"抓取文章列表失败：{e}")
            return []
    
    def fetch_single_article_info(self, url: str) -> Dict:
        """
        抓取单篇文章信息
        
        Args:
            url: 文章链接
            
        Returns:
            {title, content, description, cover_image}
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取标题
            title_elem = soup.find('h1', {'id': 'activity-name'})
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # 提取描述
            desc_elem = soup.find('meta', {'name': 'description'})
            description = desc_elem.get('content', '') if desc_elem else ''
            
            # 提取封面图
            cover_elem = soup.find('meta', {'property': 'og:image'})
            cover_image = cover_elem.get('content', '') if cover_elem else ''
            
            # 提取正文
            content_elem = soup.find('div', {'id': 'js_content'})
            if not content_elem:
                content_elem = soup.find('div', class_='rich_media_content')
            
            content = content_elem.prettify() if content_elem else ''
            
            return {
                'title': title,
                'content': content,
                'description': description,
                'cover_image': cover_image,
            }
            
        except Exception as e:
            print(f"抓取单篇文章失败：{e}")
            return {'title': '', 'content': '', 'description': '', 'cover_image': ''}
    
    def _decode_html_entities(self, text: str) -> str:
        """解码 HTML 实体"""
        return unquote(text.replace('&amp;', '&')
                           .replace('&lt;', '<')
                           .replace('&gt;', '>')
                           .replace('&quot;', '"')
                           .replace('&#39;', "'"))
    
    def _clean_url(self, url: str) -> str:
        """清理 URL"""
        return url.replace('&amp;', '&')
