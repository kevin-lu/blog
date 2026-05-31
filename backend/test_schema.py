from app.schemas.site_setting import SiteSettingUpdate
import json

data = {
    "site_name": "测试博客",
    "about_tech_stack_items": ["Java", "Python"],
    "comment_require_review": True,
}

update_data = SiteSettingUpdate(**data)
print('Schema 验证通过')

update_dict = update_data.model_dump(exclude_unset=True)
print(f'字段：{list(update_dict.keys())}')

for key, value in update_dict.items():
    if key == 'about_tech_stack_items' and isinstance(value, list):
        value = json.dumps(value)
        print(f'{key}: JSON={value}')
    elif key in ['comment_require_review', 'comment_enabled'] and isinstance(value, bool):
        value = str(value).lower()
        print(f'{key}: str={value}')
    else:
        print(f'{key}: {value}')

print('测试完成！')
