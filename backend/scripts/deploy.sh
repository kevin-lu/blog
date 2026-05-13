#!/bin/bash
# ========================================
# 博客系统云部署一键脚本
# ========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境变量
check_env() {
    print_info "检查环境变量..."
    
    if [ -z "$DB_HOST" ]; then
        print_warning "DB_HOST 未设置，使用默认值：localhost"
        export DB_HOST="localhost"
    fi
    
    if [ -z "$DB_PORT" ]; then
        export DB_PORT="3306"
    fi
    
    if [ -z "$DB_USER" ]; then
        print_warning "DB_USER 未设置，使用默认值：root"
        export DB_USER="root"
    fi
    
    if [ -z "$DB_NAME" ]; then
        print_warning "DB_NAME 未设置，使用默认值：blog_db"
        export DB_NAME="blog_db"
    fi
    
    print_success "环境变量检查完成"
}

# 执行 DDL
run_ddl() {
    print_info "执行 DDL（数据库表结构）..."
    
    # 检查 DDL 文件是否存在
    if [ ! -f "database/ddl/000_init_database.sql" ]; then
        print_error "找不到 DDL 文件：database/ddl/000_init_database.sql"
        exit 1
    fi
    
    # 执行 DDL
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < database/ddl/000_init_database.sql
    print_success "主表结构初始化完成"
    
    if [ -f "database/ddl/001_add_comments_and_view_count.sql" ]; then
        mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < database/ddl/001_add_comments_and_view_count.sql
        print_success "评论和浏览数字段添加完成"
    fi
}

# 执行 DML
run_dml() {
    print_info "执行 DML（初始化数据）..."
    
    # 检查 DML 文件是否存在
    if [ ! -f "database/dml/002_site_settings.sql" ]; then
        print_error "找不到 DML 文件：database/dml/002_site_settings.sql"
        exit 1
    fi
    
    # 执行 Python 初始化脚本
    if [ -f "scripts/init_site_settings.py" ]; then
        python scripts/init_site_settings.py --init
        print_success "站点设置初始化完成"
    else
        print_error "找不到初始化脚本：scripts/init_site_settings.py"
        exit 1
    fi
}

# 验证部署
verify() {
    print_info "验证部署..."
    
    # 查询站点设置
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
        SELECT key_name, 
               CASE 
                   WHEN LENGTH(key_value) > 50 THEN CONCAT(LEFT(key_value, 50), '...')
                   ELSE key_value
               END as key_value
        FROM site_settings 
        ORDER BY key_name;
    "
    
    # 统计设置数量
    COUNT=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -N -e "
        SELECT COUNT(*) FROM site_settings;
    ")
    
    print_success "部署验证完成，共 $COUNT 条设置"
}

# 主函数
main() {
    echo "========================================"
    echo "  博客系统云部署脚本"
    echo "========================================"
    echo ""
    
    # 切换到脚本所在目录
    cd "$(dirname "$0")/.."
    
    check_env
    run_ddl
    run_dml
    verify
    
    echo ""
    echo "========================================"
    print_success "部署完成！"
    echo "========================================"
    echo ""
    echo "下一步操作："
    echo "1. 访问后台管理页面：http://your-domain.com/admin"
    echo "2. 在'站点设置'中配置站点头像和其他信息"
    echo "3. 开始发布文章！"
    echo ""
}

# 执行主函数
main
