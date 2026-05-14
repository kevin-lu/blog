#!/bin/bash
# 测试 RSS 抓取功能

echo "=== 测试 RSS 抓取功能 ==="

# 获取 token
TOKEN=$(curl -s -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin2","password":"admin123"}' | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('access_token', ''))")

if [ -z "$TOKEN" ]; then
  echo "✗ 登录失败"
  exit 1
fi

echo "✓ 登录成功"
echo ""

# 测试 1: 抓取 cnblogs（应该成功）
echo "测试 1: 抓取 cnblogs（超时 10 秒）..."
RESULT=$(curl -s -X POST http://localhost:5001/api/v1/crawler/fetch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sources": ["cnblogs"], "limit": 1}')

echo "$RESULT" | python3 -m json.tool
echo ""

# 测试 2: 抓取 solidot（应该成功）
echo "测试 2: 抓取 solidot（超时 10 秒）..."
RESULT=$(curl -s -X POST http://localhost:5001/api/v1/crawler/fetch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sources": ["solidot"], "limit": 1}')

echo "$RESULT" | python3 -m json.tool
echo ""

echo "=== 测试完成 ==="
