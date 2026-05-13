"""
Site Setting Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class SiteSettingBase(BaseModel):
    """Base schema for site settings"""
    pass


class SiteSettingUpdate(BaseModel):
    """Schema for updating site settings"""
    # Basic Settings
    site_name: Optional[str] = Field(None, max_length=100)
    site_description: Optional[str] = None
    site_logo: Optional[str] = None
    site_url: Optional[str] = None
    site_keywords: Optional[str] = None
    og_image: Optional[str] = None
    site_avatar: Optional[str] = None
    
    # Social Links
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    weibo_url: Optional[str] = None
    email: Optional[str] = None
    
    # About Page Settings
    about_welcome_title: Optional[str] = Field(None, max_length=200)
    about_welcome_content: Optional[str] = None
    about_author_title: Optional[str] = Field(None, max_length=200)
    about_author_content: Optional[str] = None
    about_tech_stack_title: Optional[str] = Field(None, max_length=200)
    about_tech_stack_items: Optional[List[str]] = None
    about_contact_title: Optional[str] = Field(None, max_length=200)
    about_contact_email: Optional[str] = None
    about_contact_github: Optional[str] = None
    about_contact_github_label: Optional[str] = None
    
    # Comment Settings
    comment_require_review: Optional[bool] = None
    comment_enabled: Optional[bool] = None


class SiteSettingResponse(BaseModel):
    """Schema for site settings response"""
    # Basic Settings
    site_name: str = ""
    site_description: str = ""
    site_logo: str = ""
    site_url: str = ""
    site_keywords: str = ""
    og_image: str = ""
    site_avatar: str = ""
    
    # Social Links
    github_url: str = ""
    twitter_url: str = ""
    weibo_url: str = ""
    email: str = ""
    
    # About Page Settings
    about_welcome_title: str = "欢迎来到我的博客"
    about_welcome_content: str = ""
    about_author_title: str = "关于博主"
    about_author_content: str = ""
    about_tech_stack_title: str = "技术栈"
    about_tech_stack_items: List[str] = []
    about_contact_title: str = "联系方式"
    about_contact_email: str = ""
    about_contact_github: str = ""
    about_contact_github_label: str = "GitHub"
    
    # Comment Settings
    comment_require_review: bool = True
    comment_enabled: bool = True
    
    class Config:
        from_attributes = True
