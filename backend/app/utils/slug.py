"""
Slug Utilities
生成 URL 友好的 slug
"""
import re
import unicodedata
from datetime import datetime


def generate_slug(title: str, use_timestamp: bool = False) -> str:
    """
    从标题生成 slug
    
    Args:
        title: 文章标题
        use_timestamp: 是否添加时间戳
        
    Returns:
        URL 友好的 slug
    """
    # 转换为小写
    slug = title.lower()
    
    # 移除特殊字符，保留中文、英文、数字
    slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', slug)
    
    # 中文转拼音（可选，这里简化处理，直接保留中文）
    # 如果需要拼音，可以安装 pypinyin 库
    
    # 替换空格和多余字符为连字符
    slug = re.sub(r'[\s_]+', '-', slug)
    
    # 移除多余的连字符
    slug = re.sub(r'-+', '-', slug)
    
    # 移除首尾的连字符
    slug = slug.strip('-')
    
    # 限制长度
    if len(slug) > 200:
        slug = slug[:200]
    
    # 添加时间戳（如果需要）
    if use_timestamp:
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        slug = f"{slug}-{timestamp}"
    
    # 确保不为空
    if not slug:
        slug = f"article-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    return slug
