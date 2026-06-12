from app.schemas.site_setting import SiteSettingUpdate
import json

# 测试旧格式数据
old_format_data = {
    "settings": [
        {"key_name": "site_name", "key_value": ""},
        {"key_name": "about_welcome_title", "key_value": "欢迎来到我的博客"},
        {"key_name": "about_welcome_content", "key_value": "你好"},
        {"key_name": "about_author_title", "key_value": "关于博主"},
        {"key_name": "about_author_content", "key_value": "技术"},
        {"key_name": "about_tech_stack_title", "key_value": "技术栈"},
        {"key_name": "about_tech_stack_items", "key_value": ["Java", "大数据", " AI", " Python", "爬虫"]},
        {"key_name": "about_contact_title", "key_value": ""},
        {"key_name": "about_contact_email", "key_value": ""},
        {"key_name": "about_contact_github", "key_value": ""},
        {"key_name": "about_contact_github_label", "key_value": ""},
        {"key_name": "comment_require_review", "key_value": "true"},
        {"key_name": "comment_enabled", "key_value": "true"}
    ]
}

# 模拟后端转换逻辑
def convert_old_to_new_format(data):
    if 'settings' in data and isinstance(data['settings'], list):
        flat_data = {}
        for setting in data['settings']:
            key_name = setting.get('key_name')
            key_value = setting.get('key_value')
            if key_name:
                if key_name == 'about_tech_stack_items' and isinstance(key_value, str):
                    try:
                        key_value = json.loads(key_value)
                    except (json.JSONDecodeError, TypeError):
                        pass
                elif key_name in ['comment_require_review', 'comment_enabled']:
                    if isinstance(key_value, str):
                        key_value = key_value.lower() == 'true'
                
                flat_data[key_name] = key_value
        return flat_data
    return data

print("=== 测试旧格式转换 ===")
new_data = convert_old_to_new_format(old_format_data)
print(f"转换后字段：{list(new_data.keys())}")
print(f"tech_stack_items: {new_data.get('about_tech_stack_items')}")
print(f"comment_require_review: {new_data.get('comment_require_review')} (type: {type(new_data.get('comment_require_review'))})")

print("\n=== 验证 Schema ===")
try:
    update_data = SiteSettingUpdate(**new_data)
    print('✓ Schema 验证通过')
except Exception as e:
    print(f'✗ 错误：{e}')

print("\n测试完成！")
