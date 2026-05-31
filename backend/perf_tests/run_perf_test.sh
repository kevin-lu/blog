#!/bin/bash
# 性能测试快速启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认配置
TARGET_HOST="${TARGET_HOST:-http://localhost:5000}"
DURATION="${DURATION:-180}"
USERS="${USERS:-10}"
STAGES="${STAGES:-5}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   性能测试 Agent - 快速启动${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查依赖
echo -e "${YELLOW}检查依赖...${NC}"
if ! command -v locust &> /dev/null; then
    echo -e "${RED}❌ Locust 未安装，正在安装...${NC}"
    pip install -q locust
fi

if ! python -c "import psutil" &> /dev/null; then
    echo -e "${RED}❌ psutil 未安装，正在安装...${NC}"
    pip install -q psutil
fi

if ! python -c "import markdown" &> /dev/null; then
    echo -e "${RED}❌ markdown 未安装，正在安装...${NC}"
    pip install -q markdown
fi

echo -e "${GREEN}✅ 依赖检查完成${NC}"
echo ""

# 检查目标主机
echo -e "${YELLOW}检查目标主机：${TARGET_HOST}${NC}"
if ! curl -s --max-time 5 "$TARGET_HOST" > /dev/null; then
    echo -e "${RED}⚠️  目标主机无法访问，请确认服务已启动${NC}"
    echo -e "${YELLOW}提示：启动后端服务 cd .. && python run.py${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 目标主机可访问${NC}"
echo ""

# 创建结果目录
mkdir -p results

# 运行压测
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   开始性能压测${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "📊 目标主机：${TARGET_HOST}"
echo -e "⏱️  每阶梯时长：${DURATION}秒"
echo -e "👥 每阶梯用户数：${USERS}"
echo -e "📈 阶梯数量：${STAGES}"
echo ""

# 运行 Agent
python perf_test_agent.py \
    --target "$TARGET_HOST" \
    --duration "$DURATION" \
    --users "$USERS" \
    --stages "$STAGES"

EXIT_CODE=$?

# 生成报告
if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   生成测试报告${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    python report_generator.py \
        --results-dir ./results
    
    echo ""
    echo -e "${GREEN}✅ 性能测试完成！${NC}"
    echo ""
    echo -e "${YELLOW}查看报告:${NC}"
    echo "  Markdown: ls -lt results/reports/*.md | head -1"
    echo "  HTML:     ls -lt results/reports/*.html | head -1"
else
    echo ""
    echo -e "${RED}❌ 性能测试失败，请检查日志${NC}"
fi

exit $EXIT_CODE
