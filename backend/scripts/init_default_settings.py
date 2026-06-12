#!/usr/bin/env python
"""
Initialize default site settings
"""
from app import create_app
from app.extensions import db
from app.models.site_setting import SiteSetting
import json

app = create_app()

DEFAULT_SETTINGS = {
    'site_name': '我的博客',
    'site_description': '技术分享平台',
    'site_logo': '',
    'site_url': '',
    'site_keywords': '',
    'og_image': '',
    'github_url': '',
    'twitter_url': '',
    'weibo_url': '',
    'email': '',
    'about_welcome_title': '欢迎来到我的博客',
    'about_welcome_content': '这是一个技术分享平台，主要记录我在学习和工作中的技术心得和经验总结。',
    'about_author_title': '关于博主',
    'about_author_content': '一名热爱技术的开发者，专注于 Web 开发领域。',
    'about_tech_stack_title': '技术栈',
    'about_tech_stack_items': json.dumps(['Vue.js', 'React', 'TypeScript', 'Node.js']),
    'about_contact_title': '联系方式',
    'about_contact_email': '',
    'about_contact_github': '',
    'about_contact_github_label': 'GitHub',
    'comment_require_review': 'true',
    'comment_enabled': 'true',
}

with app.app_context():
    print('开始初始化默认设置...')
    
    # 检查是否已有数据
    count_result = db.session.execute(db.text('SELECT COUNT(*) FROM site_settings'))
    count = count_result.scalar()
    print(f'当前 site_settings 表中有 {count} 条数据')
    
    if count > 0:
        print('已有数据，跳过初始化')
    else:
        print('插入默认设置...')
        for key, value in DEFAULT_SETTINGS.items():
            try:
                SiteSetting.set_value(key, value, f'Default {key}')
                print(f'  ✓ {key}')
            except Exception as e:
                print(f'  ✗ {key}: {e}')
        
        db.session.commit()
        print('\n默认设置初始化完成！')
    
    # 验证
    result = db.session.execute(db.text('SELECT COUNT(*) FROM site_settings'))
    final_count = result.scalar()
    print(f'\n最终 site_settings 表中有 {final_count} 条数据')
