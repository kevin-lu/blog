#!/bin/bash
# 测试设置 API

cd /Users/luzengbiao/traeProjects/blog/blog/backend
source venv/bin/activate

echo "=== 测试设置保存 ==="

# 使用 Python 测试
python << 'PYEOF'
import json
import sys
sys.path.insert(0, '.')

# 模拟请求数据
data = {
    "settings": [
        {"key_name": "site_name", "key_value": ""},
        {"key_name": "about_tech_stack_items", "key_value": ["Java", "Python"]},
        {"key_name": "comment_require_review", "key_value": "true"}
    ]
}

print("旧格式数据（数组）:")
print(json.dumps(data, indent=2, ensure_ascii=False))

# 新格式数据
new_data = {
    "site_name": "",
    "about_tech_stack_items": ["Java", "Python"],
    "comment_require_review": True
}

print("\n新格式数据（对象）:")
print(json.dumps(new_data, indent=2, ensure_ascii=False))
PYEOF

echo ""
echo "=== 请确认前端发送的是哪种格式 ==="
