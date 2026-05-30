#!/bin/bash
# 测试 Git Hook + Codex CLI 集成

echo "======================================"
echo "🧪 测试 Git Hook + Codex CLI 集成"
echo "======================================"
echo ""

# 1. 检查 Codex CLI 是否安装
echo "1️⃣ 检查 Codex CLI 安装..."
if command -v codex &> /dev/null; then
    echo "✅ Codex CLI 已安装：$(codex --version)"
else
    echo "❌ Codex CLI 未安装"
    echo "   安装命令：npm install -g @openai/codex"
    exit 1
fi
echo ""

# 2. 检查 Git Hook 是否存在
echo "2️⃣ 检查 Git Hook 配置..."
if [ -f ".git/hooks/pre-commit" ]; then
    echo "✅ Pre-commit hook 存在"
else
    echo "❌ Pre-commit hook 不存在"
    exit 1
fi
echo ""

# 3. 检查 Git Hook 权限
echo "3️⃣ 检查 Git Hook 权限..."
if [ -x ".git/hooks/pre-commit" ]; then
    echo "✅ Pre-commit hook 可执行"
else
    echo "⚠️  Pre-commit hook 不可执行，正在修复..."
    chmod +x .git/hooks/pre-commit
    echo "✅ 已赋予执行权限"
fi
echo ""

# 4. 检查 AGENTS.md 是否存在
echo "4️⃣ 检查 AGENTS.md 配置..."
if [ -f "AGENTS.md" ]; then
    echo "✅ AGENTS.md 存在"
else
    echo "⚠️  AGENTS.md 不存在（可选）"
fi
echo ""

# 5. 测试 Codex CLI 基本功能
echo "5️⃣ 测试 Codex CLI 基本功能..."
codex --full-auto exec "Hello, this is a test. Please respond with 'OK'." --output .git/codex-review/test-result.json --timeout 30

if [ $? -eq 0 ]; then
    echo "✅ Codex CLI 基本功能正常"
    echo "   测试结果：$(cat .git/codex-review/test-result.json | head -5)"
else
    echo "❌ Codex CLI 执行失败"
    echo "   可能是认证问题或未配置 API Key"
    echo ""
    echo "   解决方法："
    echo "   1. 运行 codex auth login 进行认证"
    echo "   2. 或设置 OPENAI_API_KEY 环境变量"
    exit 1
fi
echo ""

# 6. 创建测试提交
echo "6️⃣ 创建测试提交..."
echo "# Test for Git Hook" > test-git-hook.txt
git add test-git-hook.txt

# 7. 执行提交（触发 Git Hook）
echo "7️⃣ 执行提交（触发 Git Hook）..."
git commit -m "test: 测试 Git Hook + Codex CLI 集成"

if [ $? -eq 0 ]; then
    echo "✅ 提交成功"
else
    echo "⚠️  提交失败（可能是审查未通过）"
fi
echo ""

# 8. 查看审查报告
echo "8️⃣ 查看审查报告..."
if [ -f ".git/codex-review/review-result.json" ]; then
    echo "审查报告摘要："
    cat .git/codex-review/review-result.json | grep -E "(summary|verdict)" | head -5
else
    echo "⚠️  未找到审查报告"
fi
echo ""

# 9. 清理测试文件
echo "9️⃣ 清理测试文件..."
git reset --hard HEAD~1 2>/dev/null || true
rm -f test-git-hook.txt
rm -rf .git/codex-review/
echo "✅ 清理完成"
echo ""

echo "======================================"
echo "🎉 测试完成！"
echo "======================================"
echo ""
echo "下一步："
echo "1. 检查审查报告质量"
echo "2. 根据需要调整 AGENTS.md 配置"
echo "3. 开始正常使用（每次提交前自动审查）"
echo ""
