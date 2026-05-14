#!/bin/bash
# 测试 RSS 源列表 API

echo "=== 测试 RSS 源列表 API ==="

# 1. 登录获取 token
echo "1. 登录获取 token..."
TOKEN=$(curl -s -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | \
  python -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "登录失败，尝试创建测试用户..."
  
  # 创建测试用户
  cd /Users/luzengbiao/traeProjects/blog/blog/backend
  source venv/bin/activate
  python -c "
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    # 检查用户是否存在
    user = User.query.filter_by(username='admin').first()
    if not user:
        user = User(
            username='admin',
            email='admin@example.com',
            password_hash=User.set_password('admin123')
        )
        db.session.add(user)
        db.session.commit()
        print('已创建 admin 用户')
    else:
        print('admin 用户已存在')
        # 重置密码
        user.set_password('admin123')
        db.session.commit()
        print('已重置 admin 用户密码')
"
  
  # 重新登录
  echo "重新登录..."
  TOKEN=$(curl -s -X POST http://localhost:5001/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}' | \
    python -c "import sys, json; d=json.load(sys.stdin); print(d.get('access_token', ''))" 2>/dev/null)
fi

if [ -n "$TOKEN" ]; then
  echo "✓ 登录成功"
  
  # 2. 获取 RSS 源列表
  echo "2. 获取 RSS 源列表..."
  curl -s -X GET http://localhost:5001/api/v1/crawler/sources \
    -H "Authorization: Bearer $TOKEN" | python -m json.tool
  
  echo ""
  echo "=== 测试完成 ==="
else
  echo "✗ 登录失败，无法获取 token"
  exit 1
fi
