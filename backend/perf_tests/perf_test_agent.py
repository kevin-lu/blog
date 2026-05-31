#!/usr/bin/env python3
"""
性能测试 Agent - 自动化压测 + 监控采集 + 瓶颈分析

功能：
1. 自动执行阶梯式压测
2. 采集多维度监控数据（应用、数据库、中间件）
3. 智能分析性能瓶颈
4. 生成优化建议报告

使用方法：
    python perf_test_agent.py --target http://localhost:5000 --duration 300
"""
import os
import sys
import json
import time
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.article import Article
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceTestAgent:
    """性能测试 Agent"""
    
    def __init__(
        self,
        target_host: str,
        duration: int = 300,
        users_per_stage: int = 10,
        stages: int = 5,
        sla_p99: int = 500,
        sla_error_rate: float = 1.0
    ):
        """
        初始化性能测试 Agent
        
        Args:
            target_host: 目标主机地址
            duration: 每阶梯持续时间（秒）
            users_per_stage: 每阶梯增加的用户数
            stages: 阶梯数量
            sla_p99: P99 延迟 SLA（毫秒）
            sla_error_rate: 错误率 SLA（百分比）
        """
        self.target_host = target_host
        self.duration = duration
        self.users_per_stage = users_per_stage
        self.stages = stages
        self.sla_p99 = sla_p99
        self.sla_error_rate = sla_error_rate
        
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        self.current_stage = 0
        self.test_running = False
        self.monitor_data = {
            'application': [],
            'database': [],
            'system': []
        }
        self.bottlenecks = []
        self.recommendations = []
    
    def generate_staircase_config(self) -> List[Dict]:
        """生成阶梯式压测配置"""
        configs = []
        for i in range(self.stages):
            users = (i + 1) * self.users_per_stage
            spawn_rate = users  # 每秒增加的用户数
            configs.append({
                'stage': i + 1,
                'users': users,
                'spawn_rate': spawn_rate,
                'duration': self.duration,
                'target_tps': users * 10  # 预估 TPS
            })
        return configs
    
    def run_locust_test(self, stage_config: Dict) -> Dict:
        """执行单个阶梯的 Locust 压测"""
        logger.info(f"🚀 开始阶梯 {stage_config['stage']}: {stage_config['users']} 用户")
        
        output_file = self.results_dir / f"stage_{stage_config['stage']}_report.json"
        
        # Locust 命令行参数
        cmd = [
            'locust',
            '-f', str(Path(__file__).parent / 'locustfile.py'),
            '--host', self.target_host,
            '--headless',
            '--users', str(stage_config['users']),
            '--spawn-rate', str(stage_config['spawn_rate']),
            '--run-time', f"{stage_config['duration']}s",
            '--json',
            '--csv', str(self.results_dir / f"stage_{stage_config['stage']}"),
        ]
        
        logger.info(f"执行命令：{' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=stage_config['duration'] + 60
            )
            
            # 解析输出
            if result.returncode == 0:
                logger.info(f"✅ 阶梯 {stage_config['stage']} 完成")
                return {
                    'success': True,
                    'stage': stage_config['stage'],
                    'output': result.stdout
                }
            else:
                logger.error(f"❌ 阶梯 {stage_config['stage']} 失败：{result.stderr}")
                return {
                    'success': False,
                    'stage': stage_config['stage'],
                    'error': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.warning(f"⏰ 阶梯 {stage_config['stage']} 超时")
            return {
                'success': False,
                'stage': stage_config['stage'],
                'error': 'Timeout'
            }
    
    def collect_application_metrics(self) -> Dict:
        """采集应用层指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'active_connections': 0,
            'cache_hit_rate': 0,
            'queue_depth': 0
        }
        
        try:
            app = create_app()
            with app.app_context():
                # 查询数据库连接数
                result = db.session.execute(text("SELECT COUNT(*) FROM information_schema.processlist WHERE db = DATABASE()"))
                # 注意：上面这个 SQL 只适用于 MySQL，SQLite 需要不同的查询
                # 对于 SQLite:
                try:
                    result = db.session.execute(text("SELECT COUNT(*) FROM sqlite_master WHERE type='table'"))
                    metrics['active_connections'] = 1  # SQLite 是单连接
                except:
                    pass
                
                # 查询队列深度
                from app.models.crawler import CrawlerQueue
                try:
                    metrics['queue_depth'] = CrawlerQueue.query.filter(
                        CrawlerQueue.status == 'pending'
                    ).count()
                except:
                    pass
                
                # 查询缓存命中率（如果有 Redis）
                try:
                    from app.extensions import cache
                    if cache.cache_type == 'redis':
                        # 这里可以查询 Redis 的 stats
                        metrics['cache_hit_rate'] = 0  # 需要实现 Redis 统计查询
                except:
                    pass
        except Exception as e:
            logger.error(f"采集应用指标失败：{e}")
        
        self.monitor_data['application'].append(metrics)
        return metrics
    
    def collect_database_metrics(self) -> Dict:
        """采集数据库指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'slow_queries': [],
            'connection_pool_usage': 0,
            'lock_waits': 0
        }
        
        try:
            app = create_app()
            with app.app_context():
                # 查询慢查询（需要数据库支持）
                try:
                    # MySQL 慢查询表
                    result = db.session.execute(text("""
                        SELECT query, avg_timer_wait 
                        FROM performance_schema.events_statements_summary_by_digest 
                        ORDER BY avg_timer_wait DESC 
                        LIMIT 10
                    """))
                    metrics['slow_queries'] = [
                        {'query': row[0], 'avg_time_ms': row[1] / 1000000}
                        for row in result.fetchall()
                    ][:5]
                except:
                    # SQLite 不支持慢查询日志
                    pass
                
                # 查询连接池使用情况
                engine = db.engine
                if hasattr(engine.pool, 'checkedout'):
                    metrics['connection_pool_usage'] = engine.pool.checkedout() / engine.pool.size()
                
        except Exception as e:
            logger.error(f"采集数据库指标失败：{e}")
        
        self.monitor_data['database'].append(metrics)
        return metrics
    
    def collect_system_metrics(self) -> Dict:
        """采集系统层指标"""
        import psutil
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
            'net_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
        }
        
        self.monitor_data['system'].append(metrics)
        return metrics
    
    def analyze_bottlenecks(self, test_results: List[Dict]) -> List[Dict]:
        """分析性能瓶颈"""
        logger.info("🔍 开始分析性能瓶颈...")
        
        bottlenecks = []
        
        # 分析应用指标
        app_metrics = self.monitor_data['application']
        if app_metrics:
            avg_queue_depth = sum(m.get('queue_depth', 0) for m in app_metrics) / len(app_metrics)
            if avg_queue_depth > 10:
                bottlenecks.append({
                    'type': 'application',
                    'severity': 'high',
                    'description': f'队列积压严重，平均深度：{avg_queue_depth:.1f}',
                    'evidence': app_metrics[-5:],  # 最近 5 个样本
                    'recommendation': '增加 AI 并发处理数或优化处理逻辑'
                })
        
        # 分析数据库指标
        db_metrics = self.monitor_data['database']
        if db_metrics:
            # 检查慢查询
            all_slow_queries = []
            for m in db_metrics:
                all_slow_queries.extend(m.get('slow_queries', []))
            
            if all_slow_queries:
                # 统计最慢的查询
                query_times = {}
                for q in all_slow_queries:
                    query_text = q.get('query', '')[:100]
                    query_times[query_text] = query_times.get(query_text, 0) + q.get('avg_time_ms', 0)
                
                top_slow = sorted(query_times.items(), key=lambda x: x[1], reverse=True)[:3]
                if top_slow:
                    bottlenecks.append({
                        'type': 'database',
                        'severity': 'critical',
                        'description': f'检测到慢查询，最慢：{top_slow[0][1]:.2f}ms',
                        'evidence': [{'query': q, 'time': t} for q, t in top_slow],
                        'recommendation': '为相关字段添加索引或优化 SQL'
                    })
            
            # 检查连接池
            avg_pool_usage = sum(m.get('connection_pool_usage', 0) for m in db_metrics) / len(db_metrics)
            if avg_pool_usage > 0.8:
                bottlenecks.append({
                    'type': 'database',
                    'severity': 'high',
                    'description': f'数据库连接池使用率过高：{avg_pool_usage*100:.1f}%',
                    'evidence': db_metrics[-5:],
                    'recommendation': '增加连接池大小或优化查询效率'
                })
        
        # 分析系统指标
        sys_metrics = self.monitor_data['system']
        if sys_metrics:
            avg_cpu = sum(m.get('cpu_percent', 0) for m in sys_metrics) / len(sys_metrics)
            avg_memory = sum(m.get('memory_percent', 0) for m in sys_metrics) / len(sys_metrics)
            
            if avg_cpu > 80:
                bottlenecks.append({
                    'type': 'system',
                    'severity': 'high',
                    'description': f'CPU 使用率过高：{avg_cpu:.1f}%',
                    'evidence': sys_metrics[-5:],
                    'recommendation': '优化 CPU 密集型操作或增加 CPU 资源'
                })
            
            if avg_memory > 85:
                bottlenecks.append({
                    'type': 'system',
                    'severity': 'critical',
                    'description': f'内存使用率过高：{avg_memory:.1f}%',
                    'evidence': sys_metrics[-5:],
                    'recommendation': '检查内存泄漏或增加内存资源'
                })
        
        self.bottlenecks = bottlenecks
        return bottlenecks
    
    def generate_recommendations(self) -> List[Dict]:
        """生成优化建议"""
        recommendations = []
        
        for bottleneck in self.bottlenecks:
            if bottleneck['severity'] == 'critical':
                priority = 'P0 - 必须修复'
            elif bottleneck['severity'] == 'high':
                priority = 'P1 - 强烈建议'
            else:
                priority = 'P2 - 可以优化'
            
            recommendations.append({
                'priority': priority,
                'category': bottleneck['type'],
                'issue': bottleneck['description'],
                'solution': bottleneck['recommendation'],
                'expected_impact': '高' if bottleneck['severity'] in ['critical', 'high'] else '中'
            })
        
        # 添加通用建议
        recommendations.append({
            'priority': 'P2 - 可以优化',
            'category': 'general',
            'issue': '建议添加 Redis 缓存层',
            'solution': '对热点数据（如文章列表、分类标签）添加 Redis 缓存',
            'expected_impact': '中'
        })
        
        self.recommendations = recommendations
        return recommendations
    
    def generate_report(self, test_results: List[Dict]) -> Dict:
        """生成性能测试报告"""
        report = {
            'metadata': {
                'target_host': self.target_host,
                'test_date': datetime.now().isoformat(),
                'duration_per_stage': self.duration,
                'total_stages': self.stages,
                'sla_p99_ms': self.sla_p99,
                'sla_error_rate': self.sla_error_rate
            },
            'test_results': test_results,
            'baseline_capacity': {
                'max_tps': 0,  # 需要从 Locust 结果解析
                'max_users': self.stages * self.users_per_stage,
                'bottleneck_stage': self.current_stage
            },
            'bottlenecks': self.bottlenecks,
            'recommendations': self.recommendations,
            'risk_assessment': {
                'current_capacity': '待评估',
                'target_capacity': '待设定',
                'gap': '待计算'
            }
        }
        
        # 保存报告
        report_file = self.results_dir / f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 性能报告已保存：{report_file}")
        
        return report
    
    def run_full_test(self):
        """执行完整的阶梯压测"""
        logger.info("=" * 60)
        logger.info("🚀 性能测试 Agent 启动")
        logger.info(f"🎯 目标主机：{self.target_host}")
        logger.info(f"📊 压测策略：{self.stages} 阶梯，每阶梯{self.duration}秒")
        logger.info("=" * 60)
        
        staircase_config = self.generate_staircase_config()
        test_results = []
        
        self.test_running = True
        
        for stage_cfg in staircase_config:
            if not self.test_running:
                logger.warning("⚠️ 压测已手动停止")
                break
            
            # 执行压测
            result = self.run_locust_test(stage_cfg)
            test_results.append(result)
            
            # 采集监控数据
            self.collect_application_metrics()
            self.collect_database_metrics()
            self.collect_system_metrics()
            
            # 检查是否触发熔断
            if not result['success']:
                logger.warning(f"⚠️ 阶梯 {stage_cfg['stage']} 失败，可能触发 SLA")
                # 这里可以添加更详细的 SLA 检查逻辑
            
            self.current_stage = stage_cfg['stage']
            
            # 阶梯间休息
            if stage_cfg != staircase_config[-1]:
                logger.info(f"⏸️  阶梯间休息 10 秒...")
                time.sleep(10)
        
        self.test_running = False
        
        # 分析瓶颈
        self.analyze_bottlenecks(test_results)
        
        # 生成建议
        self.generate_recommendations()
        
        # 生成报告
        report = self.generate_report(test_results)
        
        # 打印摘要
        self.print_summary(report)
        
        return report
    
    def print_summary(self, report: Dict):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("📊 性能测试报告摘要")
        print("=" * 60)
        
        print(f"\n🎯 基线能力:")
        print(f"  最大并发用户：{report['baseline_capacity']['max_users']}")
        print(f"  瓶颈阶段：阶梯 {report['baseline_capacity']['bottleneck_stage']}")
        
        print(f"\n🔍 瓶颈 Top {len(self.bottlenecks)}:")
        for i, b in enumerate(self.bottlenecks, 1):
            print(f"  {i}. [{b['severity'].upper()}] {b['description']}")
        
        print(f"\n💡 优化建议 Top {len(self.recommendations)}:")
        for i, r in enumerate(self.recommendations, 1):
            print(f"  {i}. [{r['priority']}] {r['issue']}")
            print(f"     方案：{r['solution']}")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='性能测试 Agent')
    parser.add_argument('--target', type=str, default='http://localhost:5000',
                        help='目标主机地址')
    parser.add_argument('--duration', type=int, default=180,
                        help='每阶梯持续时间（秒）')
    parser.add_argument('--users', type=int, default=10,
                        help='每阶梯用户数')
    parser.add_argument('--stages', type=int, default=5,
                        help='阶梯数量')
    parser.add_argument('--sla-p99', type=int, default=500,
                        help='P99 延迟 SLA（毫秒）')
    parser.add_argument('--sla-error', type=float, default=1.0,
                        help='错误率 SLA（百分比）')
    
    args = parser.parse_args()
    
    agent = PerformanceTestAgent(
        target_host=args.target,
        duration=args.duration,
        users_per_stage=args.users,
        stages=args.stages,
        sla_p99=args.sla_p99,
        sla_error_rate=args.sla_error
    )
    
    try:
        report = agent.run_full_test()
        sys.exit(0 if report else 1)
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
        agent.test_running = False
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试失败：{e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
