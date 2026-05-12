#!/bin/bash

# 测试设置 API

BASE_URL="http://localhost:5000/api/v1"

echo "=== 测试获取设置 ==="
curl -X GET "$BASE_URL/settings" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "=== 测试更新设置（需要登录）==="
# 先登录获取 token
echo "正在登录..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

echo "登录响应：$LOGIN_RESPONSE"

# 提取 token
TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "无法获取 access token，请检查登录凭据"
  exit 1
fi

echo "获取到 token: ${TOKEN:0:20}..."

# 测试更新设置
echo ""
echo "正在更新设置..."
curl -X PUT "$BASE_URL/settings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "site_name": "测试博客",
    "about_welcome_title": "欢迎来到我的博客",
    "about_welcome_content": "这是一个技术分享平台",
    "about_tech_stack_items": ["Vue.js", "React", "TypeScript"]
  }' \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "=== 再次获取设置验证 ==="
curl -X GET "$BASE_URL/settings" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n"
