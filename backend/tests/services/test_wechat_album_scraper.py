"""Tests for WechatAlbumScraper"""
import pytest
from app.services.wechat_album_scraper import WechatAlbumScraper


class TestWechatAlbumScraper:
    
    def test_fetch_album_info(self):
        """测试抓取合集信息"""
        scraper = WechatAlbumScraper()
        album_url = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkzMDI1NjcyOQ==&action=getalbum&album_id=3022691668057276419"
        
        info = scraper.fetch_album_info(album_url)
        
        assert info is not None
        assert 'name' in info
        assert 'total_count' in info
        assert info['name'] == 'AI'
        assert info['total_count'] > 0
    
    def test_fetch_article_list(self):
        """测试抓取文章列表"""
        scraper = WechatAlbumScraper()
        album_url = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkzMDI1NjcyOQ==&action=getalbum&album_id=3022691668057276419"
        
        articles = scraper.fetch_article_list(album_url)
        
        assert len(articles) > 0
        assert all('title' in a and 'url' in a for a in articles)
    
    def test_decode_html_entities(self):
        """测试 HTML 实体解码"""
        scraper = WechatAlbumScraper()
        
        text = "测试 &amp; &lt; &gt; &quot; &#39;"
        decoded = scraper._decode_html_entities(text)
        
        assert decoded == "测试 & < > \" '"
    
    def test_clean_url(self):
        """测试 URL 清理"""
        scraper = WechatAlbumScraper()
        
        url = "http://example.com?a=1&amp;b=2"
        cleaned = scraper._clean_url(url)
        
        assert cleaned == "http://example.com?a=1&b=2"
