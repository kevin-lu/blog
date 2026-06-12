#!/usr/bin/env python3
"""
监控数据采集器 - 实时采集应用、数据库、系统指标

功能：
1. 应用层指标：TPS、RT、错误率、线程池、缓存命中率
2. 数据库指标：慢查询、连接池、锁等待
3. 系统指标：CPU、内存、磁盘 IO、网络 IO
4. 中间件指标：Redis 命中率、MQ 堆积
"""
import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import threading

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """监控指标采集器"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化采集器
        
        Args:
            output_dir: 输出目录，默认保存到 perf_tests/results/
        """
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "results" / "metrics"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.collection_interval = 5  # 采集间隔（秒）
        self.is_running = False
        self.collection_thread = None
        
        self.metrics_buffer = {
            'application': [],
            'database': [],
            'system': [],
            'middleware': []
        }
    
    def start_collection(self, interval: int = 5):
        """开始采集"""
        self.collection_interval = interval
        self.is_running = True
        self.collection_thread = threading.Thread(target=self._collection_loop)
        self.collection_thread.daemon = True
        self.collection_thread.start()
        logger.info(f"📊 开始采集监控数据，间隔：{interval}秒")
    
    def stop_collection(self):
        """停止采集"""
        self.is_running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=10)
        logger.info("⏹️  停止采集监控数据")
    
    def _collection_loop(self):
        """采集循环"""
        while self.is_running:
            try:
                self.collect_all_metrics()
            except Exception as e:
                logger.error(f"采集指标失败：{e}", exc_info=True)
            
            time.sleep(self.collection_interval)
    
    def collect_all_metrics(self) -> Dict:
        """采集所有指标"""
        timestamp = datetime.now().isoformat()
        
        metrics = {
            'timestamp': timestamp,
            'application': self.collect_application_metrics(),
            'database': self.collect_database_metrics(),
            'system': self.collect_system_metrics(),
            'middleware': self.collect_middleware_metrics()
        }
        
        # 保存到 buffer
        for key in ['application', 'database', 'system', 'middleware']:
            if metrics[key]:
                self.metrics_buffer[key].append(metrics[key])
        
        return metrics
    
    def collect_application_metrics(self) -> Dict:
        """采集应用层指标"""
        try:
            app = create_app()
            with app.app_context():
                # 模拟应用指标（实际应该从 APM 系统获取）
                metrics = {
                    'tps': 0,  # 需要从请求日志计算
                    'rt_p50': 0,
                    'rt_p90': 0,
                    'rt_p99': 0,
                    'error_rate': 0,
                    'active_threads': threading.active_count(),
                    'queue_depth': 0
                }
                
                # 查询 AI 队列深度
                try:
                    from app.models.crawler import CrawlerQueue
                    metrics['queue_depth'] = CrawlerQueue.query.filter(
                        CrawlerQueue.status == 'pending'
                    ).count()
                except:
                    pass
                
                return metrics
        except Exception as e:
            logger.error(f"采集应用指标失败：{e}")
            return {}
    
    def collect_database_metrics(self) -> Dict:
        """采集数据库指标"""
        try:
            app = create_app()
            with app.app_context():
                engine = db.engine
                
                metrics = {
                    'connection_pool_size': 0,
                    'connection_pool_used': 0,
                    'connection_pool_usage': 0,
                    'slow_queries': []
                }
                
                # 连接池信息
                if hasattr(engine.pool, 'size'):
                    metrics['connection_pool_size'] = engine.pool.size()
                if hasattr(engine.pool, 'checkedout'):
                    metrics['connection_pool_used'] = engine.pool.checkedout()
                    if metrics['connection_pool_size'] > 0:
                        metrics['connection_pool_usage'] = (
                            metrics['connection_pool_used'] / metrics['connection_pool_size']
                        )
                
                # 慢查询（需要数据库支持）
                try:
                    from sqlalchemy import text
                    
                    # MySQL 慢查询
                    if 'mysql' in str(engine.url):
                        result = db.session.execute(text("""
                            SELECT query, avg_timer_wait, exec_count
                            FROM performance_schema.events_statements_summary_by_digest
                            WHERE avg_timer_wait > 1000000000000  -- 1 秒
                            ORDER BY avg_timer_wait DESC
                            LIMIT 10
                        """))
                        metrics['slow_queries'] = [
                            {
                                'query': row[0][:200],
                                'avg_time_ms': row[1] / 1000000,
                                'exec_count': row[2]
                            }
                            for row in result.fetchall()
                        ]
                    
                    # SQLite 不支持慢查询日志
                except Exception as e:
                    logger.debug(f"查询慢查询失败：{e}")
                
                return metrics
        except Exception as e:
            logger.error(f"采集数据库指标失败：{e}")
            return {}
    
    def collect_system_metrics(self) -> Dict:
        """采集系统层指标"""
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # 内存
            memory = psutil.virtual_memory()
            
            # 磁盘
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # 网络
            net_io = psutil.net_io_counters()
            
            metrics = {
                'cpu_percent': cpu_percent,
                'cpu_per_core': cpu_per_core,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024 ** 3),
                'memory_total_gb': memory.total / (1024 ** 3),
                'disk_percent': disk.percent,
                'disk_read_mb': (disk_io.read_bytes / (1024 ** 2)) if disk_io else 0,
                'disk_write_mb': (disk_io.write_bytes / (1024 ** 2)) if disk_io else 0,
                'net_bytes_sent_mb': (net_io.bytes_sent / (1024 ** 2)) if net_io else 0,
                'net_bytes_recv_mb': (net_io.bytes_recv / (1024 ** 2)) if net_io else 0
            }
            
            return metrics
        except ImportError:
            logger.warning("psutil 未安装，跳过系统指标采集")
            return {}
        except Exception as e:
            logger.error(f"采集系统指标失败：{e}")
            return {}
    
    def collect_middleware_metrics(self) -> Dict:
        """采集中间件指标（Redis、MQ 等）"""
        try:
            metrics = {
                'redis_connected': False,
                'redis_memory_used': 0,
                'redis_hit_rate': 0,
                'mq_queue_depth': 0
            }
            
            # Redis 指标
            try:
                from app.extensions import cache
                if cache.cache_type == 'redis':
                    redis_client = cache._write_client
                    info = redis_client.info('memory')
                    metrics['redis_connected'] = True
                    metrics['redis_memory_used'] = info.get('used_memory_human', '0')
                    
                    # 缓存命中率（需要 stats）
                    stats = redis_client.info('stats')
                    if stats:
                        keyspace_hits = stats.get('keyspace_hits', 0)
                        keyspace_misses = stats.get('keyspace_misses', 0)
                        total = keyspace_hits + keyspace_misses
                        if total > 0:
                            metrics['redis_hit_rate'] = keyspace_hits / total
            except Exception as e:
                logger.debug(f"查询 Redis 指标失败：{e}")
            
            return metrics
        except Exception as e:
            logger.error(f"采集中间件指标失败：{e}")
            return {}
    
    def save_metrics(self, filename: Optional[str] = None):
        """保存指标到文件"""
        if not filename:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_file = self.output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics_buffer, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 指标已保存：{output_file}")
        return output_file
    
    def export_csv(self):
        """导出为 CSV 格式"""
        import csv
        
        for metric_type in ['application', 'database', 'system', 'middleware']:
            if not self.metrics_buffer[metric_type]:
                continue
            
            filename = f"{metric_type}_metrics.csv"
            output_file = self.output_dir / filename
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if not self.metrics_buffer[metric_type]:
                    continue
                
                writer = csv.DictWriter(f, fieldnames=self.metrics_buffer[metric_type][0].keys())
                writer.writeheader()
                writer.writerows(self.metrics_buffer[metric_type])
            
            logger.info(f"📊 CSV 已导出：{output_file}")


def main():
    """独立运行采集器"""
    import argparse
    
    parser = argparse.ArgumentParser(description='监控指标采集器')
    parser.add_argument('--interval', type=int, default=5,
                        help='采集间隔（秒）')
    parser.add_argument('--duration', type=int, default=300,
                        help='采集持续时间（秒）')
    parser.add_argument('--output', type=str, default=None,
                        help='输出目录')
    
    args = parser.parse_args()
    
    collector = MetricsCollector(output_dir=args.output)
    
    try:
        collector.start_collection(interval=args.interval)
        logger.info(f"采集器运行中... 持续{args.duration}秒")
        time.sleep(args.duration)
    except KeyboardInterrupt:
        logger.info("用户中断采集")
    finally:
        collector.stop_collection()
        collector.save_metrics()
        collector.export_csv()


if __name__ == '__main__':
    main()
