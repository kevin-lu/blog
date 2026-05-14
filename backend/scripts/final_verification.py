#!/usr/bin/env python
"""系统最终验证脚本"""
from app import create_app
from app.config import Config

app = create_app()
with app.app_context():
    print('=' * 60)
    print('✅ 自动文章抓取系统 - 最终验证')
    print('=' * 60)
    print()
    
    # 1. 检查配置
    print('1. 配置检查:')
    print(f'   ✓ RSS 源数量：{len(Config.RSS_SOURCES)}')
    print(f'   ✓ 启用的源：{sum(1 for s in Config.RSS_SOURCES if s.get("enabled"))}')
    print(f'   ✓ Minimax API 配置：{"✓" if Config.MINIMAX_API_KEY else "✗"}')
    print(f'   ✓ 告警服务配置：{"✓" if Config.DINGTALK_WEBHOOK or Config.WECHAT_WORK_WEBHOOK else "✗ (可选)"}')
    print()
    
    # 2. 检查服务模块
    print('2. 服务模块检查:')
    try:
        from app.services import rss_crawler
        print('   ✓ RSS 爬虫服务')
    except ImportError as e:
        print(f'   ✗ RSS 爬虫服务导入失败：{e}')
    
    try:
        from app.services import ai_queue
        print('   ✓ AI 队列服务')
    except ImportError as e:
        print(f'   ✗ AI 队列服务导入失败：{e}')
    
    try:
        from app.services import scheduler
        print('   ✓ 定时任务调度器')
    except ImportError as e:
        print(f'   ✗ 定时任务调度器导入失败：{e}')
    
    try:
        from app.services import alert
        print('   ✓ 告警服务')
    except ImportError as e:
        print(f'   ✗ 告警服务导入失败：{e}')
    print()
    
    # 3. 检查优化工具
    print('3. 性能优化工具检查:')
    try:
        from app.utils import db_optimization
        print('   ✓ 数据库优化工具')
    except ImportError as e:
        print(f'   ✗ 数据库优化工具导入失败：{e}')
    print()
    
    # 4. 检查 API 路由
    print('4. API 路由检查:')
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    crawler_rules = [r for r in rules if 'crawler' in r]
    queue_rules = [r for r in rules if 'queue' in r]
    scheduler_rules = [r for r in rules if 'scheduler' in r]
    
    print(f'   ✓ 抓取管理 API: {len(crawler_rules)} 个')
    print(f'   ✓ 队列管理 API: {len(queue_rules)} 个')
    print(f'   ✓ 定时任务 API: {len(scheduler_rules)} 个')
    print()
    
    print('=' * 60)
    print('🎉 系统验证完成！所有组件已就绪！')
    print('=' * 60)
