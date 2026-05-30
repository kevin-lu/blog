#!/bin/bash
# AI 代码审查自动化 - 测试脚本
# 用法：./test-ai-review.sh

set -e

echo "======================================"
echo "AI 代码审查自动化 - 测试脚本"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 GitHub CLI
if ! command -v gh &> /dev/null; then
    echo -e "${RED}错误：需要安装 GitHub CLI (gh)${NC}"
    echo "安装：brew install gh"
    exit 1
fi

# 检查 Python 依赖
echo -e "${YELLOW}检查 Python 依赖...${NC}"
if ! python3 -c "import github" 2>/dev/null; then
    echo -e "${YELLOW}安装 PyGithub...${NC}"
    pip3 install PyGithub requests
fi

# 检查 Secrets 配置
echo -e "${YELLOW}检查 GitHub Secrets 配置...${NC}"
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}警告：GITHUB_TOKEN 未设置${NC}"
    echo "请在 GitHub 仓库设置中添加 Secrets"
    echo ""
    echo "步骤："
    echo "1. 打开 https://github.com/${GITHUB_REPOSITORY:-your-repo}/settings/secrets/actions"
    echo "2. 添加以下 Secrets:"
    echo "   - LLM_API_KEY: 你的 LLM API 密钥"
    echo "   - LLM_API_URL: LLM API 地址（可选）"
    echo ""
fi

# 创建测试分支
echo -e "${YELLOW}创建测试分支...${NC}"
TEST_BRANCH="test/ai-review-$(date +%Y%m%d-%H%M%S)"
git checkout -b $TEST_BRANCH

# 创建测试修改
echo -e "${YELLOW}创建测试代码修改...${NC}"

# 修改 1: 添加一个简单的 N+1 查询示例（用于测试 AI 是否能发现）
cat >> backend/app/api/test_n_plus_one.py << 'EOF'
# 测试文件：故意制造 N+1 查询问题
# AI 审查应该能发现这个问题

from app.models import Article, User

def get_articles_with_authors():
    """获取所有文章及其作者 - N+1 查询示例"""
    articles = Article.query.all()
    
    # 坏例子：循环中查询（N+1 问题）
    result = []
    for article in articles:
        # 每次循环都会查询数据库
        author = User.query.filter_by(id=article.author_id).first()
        result.append({
            'title': article.title,
            'author_name': author.name if author else 'Unknown'
        })
    
    return result

def get_articles_optimized():
    """优化版本 - 使用 join"""
    articles = Article.query.join(User).all()
    
    result = []
    for article in articles:
        result.append({
            'title': article.title,
            'author_name': article.author.name if article.author else 'Unknown'
        })
    
    return result
EOF

# 修改 2: 添加一个信任边界问题示例
cat >> backend/app/api/test_trust_boundary.py << 'EOF'
# 测试文件：故意制造信任边界问题
# AI 审查应该能发现这个问题

from flask import request

def create_comment():
    """创建评论 - 信任边界问题示例"""
    # 坏例子：直接使用用户输入，未验证
    user_id = request.json.get('user_id')  # 未验证
    article_id = request.json.get('article_id')  # 未验证
    content = request.json.get('content')  # 未验证
    
    # 直接使用，存在安全风险
    # 应该验证类型、范围、SQL 注入等
    
    return {
        'user_id': user_id,
        'article_id': article_id,
        'content': content
    }

def create_comment_safe():
    """安全版本 - 添加验证"""
    import re
    
    user_id = request.json.get('user_id')
    article_id = request.json.get('article_id')
    content = request.json.get('content')
    
    # 验证
    if not user_id or not isinstance(user_id, int) or user_id <= 0:
        raise ValueError('Invalid user_id')
    
    if not article_id or not isinstance(article_id, int) or article_id <= 0:
        raise ValueError('Invalid article_id')
    
    if not content or len(content) > 10000:
        raise ValueError('Invalid content')
    
    # 清理输入
    content = re.sub(r'<[^>]+>', '', content)  # 移除 HTML 标签
    
    return {
        'user_id': user_id,
        'article_id': article_id,
        'content': content
    }
EOF

# 提交修改
git add backend/app/api/test_*.py
git commit -m "Test: 添加 AI 审查测试代码

- 添加 N+1 查询示例
- 添加信任边界问题示例

用于测试 AI 代码审查自动化系统"

# 推送到 GitHub
echo -e "${YELLOW}推送到 GitHub...${NC}"
git push origin $TEST_BRANCH

# 创建 PR
echo -e "${YELLOW}创建测试 PR...${NC}"
PR_URL=$(gh pr create \
    --title "🧪 测试 AI 代码审查" \
    --body "这是一个测试 PR，用于验证 AI 代码审查自动化系统。

## 测试内容

- N+1 查询示例
- 信任边界问题示例

## 预期行为

1. AI 审查应该发现 N+1 查询问题
2. AI 审查应该发现信任边界问题
3. 发布综合审查报告
4. 创建行内评论
5. (可选) 自动修复 Critical 问题

---

*测试 PR | 自动创建*" \
    --base main \
    --head $TEST_BRANCH)

echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}测试 PR 已创建！${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "PR 地址：$PR_URL"
echo ""
echo "下一步："
echo "1. 打开 PR 地址查看"
echo "2. 查看 Actions 中的 'AI Code Review' 工作流"
echo "3. 等待 AI 审查完成（约 1-2 分钟）"
echo "4. 查看 AI 发布的评论"
echo ""
echo -e "${YELLOW}监控工作流：${NC}"
echo "gh run watch --repo $GITHUB_REPOSITORY"
echo ""
echo -e "${YELLOW}查看日志：${NC}"
echo "gh run view --log --repo $GITHUB_REPOSITORY"
echo ""
