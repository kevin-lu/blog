#!/bin/bash
# Kimi 配置助手
# 帮助你快速配置 Kimi AI 代码审查

set -e

echo "======================================"
echo "Kimi AI 代码审查配置助手"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}步骤 1: 获取 Kimi API Key${NC}"
echo ""
echo "请访问：https://platform.moonshot.cn/console/api-keys"
echo "1. 登录/注册 Kimi 开放平台"
echo "2. 完成实名认证"
echo "3. 点击 '创建 API Key'"
echo "4. 复制密钥（格式：sk-moonshot-xxxxx）"
echo ""
read -p "按回车继续..."

echo ""
echo -e "${YELLOW}步骤 2: 配置 GitHub Secrets${NC}"
echo ""
echo "请访问："
echo "https://github.com/${GITHUB_REPOSITORY:-YOUR-REPO}/settings/secrets/actions"
echo ""
echo "添加以下 3 个 Secrets："
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│ 1. Name:  LLM_API_KEY                                   │"
echo "│    Value: [粘贴你的 Kimi API Key]                       │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 2. Name:  LLM_API_URL                                   │"
echo "│    Value: https://api.moonshot.cn/v1/chat/completions  │"
echo "├─────────────────────────────────────────────────────────┤"
echo "│ 3. Name:  LLM_MODEL                                     │"
echo "│    Value: moonshot-v1-8k                                │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""
read -p "按回车继续..."

echo ""
echo -e "${YELLOW}步骤 3: 验证配置${NC}"
echo ""

# 检查是否在 GitHub Actions 环境
if [ -n "$GITHUB_ACTIONS" ]; then
    echo "✅ 当前在 GitHub Actions 环境中"
    
    # 测试环境变量
    if [ -n "$LLM_API_KEY" ]; then
        echo "✅ LLM_API_KEY 已设置"
        echo "   前缀：${LLM_API_KEY:0:15}..."
    else
        echo -e "${RED}❌ LLM_API_KEY 未设置${NC}"
    fi
    
    if [ -n "$LLM_API_URL" ]; then
        echo "✅ LLM_API_URL 已设置：$LLM_API_URL"
    else
        echo -e "${RED}❌ LLM_API_URL 未设置${NC}"
    fi
    
    if [ -n "$LLM_MODEL" ]; then
        echo "✅ LLM_MODEL 已设置：$LLM_MODEL"
    else
        echo "⚠️  LLM_MODEL 未设置，使用默认值：moonshot-v1-8k"
    fi
else
    echo "⚠️  当前不在 GitHub Actions 环境中"
    echo ""
    echo "请在 GitHub 上运行测试工作流来验证："
    echo ""
    echo "1. 打开 Actions 标签"
    echo "2. 选择 'Test Kimi Configuration'"
    echo "3. 点击 'Run workflow'"
    echo "4. 查看运行结果"
fi

echo ""
echo -e "${YELLOW}步骤 4: 测试 Kimi API${NC}"
echo ""

# 创建测试脚本
cat > /tmp/test_kimi.sh << 'EOF'
#!/bin/bash

if [ -z "$LLM_API_KEY" ]; then
    echo "❌ LLM_API_KEY 未设置"
    exit 1
fi

if [ -z "$LLM_API_URL" ]; then
    echo "❌ LLM_API_URL 未设置"
    exit 1
fi

MODEL=${LLM_MODEL:-moonshot-v1-8k}

echo "测试 Kimi API..."
echo "模型：$MODEL"
echo ""

RESPONSE=$(curl -s -X POST "$LLM_API_URL" \
  -H "Authorization: Bearer $LLM_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": \"你好，请介绍一下你自己\"
      }
    ]
  }")

if echo "$RESPONSE" | grep -q "error"; then
    echo "❌ API 调用失败"
    echo "$RESPONSE" | jq .
    exit 1
else
    echo "✅ API 调用成功"
    echo "响应：$(echo "$RESPONSE" | jq -r '.choices[0].message.content' | head -c 100)..."
fi
EOF

chmod +x /tmp/test_kimi.sh

# 如果在 Actions 环境中，运行测试
if [ -n "$GITHUB_ACTIONS" ]; then
    /tmp/test_kimi.sh
else
    echo "测试脚本已创建：/tmp/test_kimi.sh"
    echo "在 GitHub Actions 中运行时会自动测试"
fi

echo ""
echo -e "${GREEN}======================================"
echo "配置完成！"
echo "======================================${NC}"
echo ""
echo "下一步："
echo "1. 在 GitHub 添加 Secrets（见步骤 2）"
echo "2. 运行测试工作流验证"
echo "3. 创建测试 PR 体验 AI 审查"
echo ""
echo "📚 详细文档：.github/KIMI-CONFIG.md"
echo ""
