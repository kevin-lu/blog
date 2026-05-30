#!/usr/bin/env python3
"""
性能测试报告生成器

功能：
1. 解析 Locust 结果
2. 整合监控数据
3. 生成可视化报告（Markdown + HTML）
4. 输出优化建议
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ReportGenerator:
    """性能测试报告生成器"""
    
    def __init__(self, results_dir: Optional[str] = None):
        """
        初始化报告生成器
        
        Args:
            results_dir: 结果目录，默认 perf_tests/results/
        """
        self.results_dir = Path(results_dir) if results_dir else Path(__file__).parent / "results"
        self.report_dir = self.results_dir / "reports"
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def load_test_results(self, stage: Optional[int] = None) -> List[Dict]:
        """加载压测结果"""
        results = []
        
        # 查找 CSV 文件
        csv_files = list(self.results_dir.glob("stage_*.csv"))
        
        for csv_file in sorted(csv_files):
            if stage and f"stage_{stage}" not in csv_file.name:
                continue
            
            # 解析 CSV
            try:
                import csv
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        results.append({
                            'method': row.get('Method', ''),
                            'name': row.get('Name', ''),
                            'requests': int(row.get('Request Count', 0)),
                            'failures': int(row.get('Failure Count', 0)),
                            'avg_rt': float(row.get('Average Response Time', 0)),
                            'min_rt': float(row.get('Min Response Time', 0)),
                            'max_rt': float(row.get('Max Response Time', 0)),
                            'p50': float(row.get('50%', 0)),
                            'p95': float(row.get('95%', 0)),
                            'p99': float(row.get('99%', 0)),
                            'tps': float(row.get('Current RPS', 0))
                        })
            except Exception as e:
                print(f"解析 CSV 失败 {csv_file}: {e}")
        
        return results
    
    def load_metrics(self) -> Dict:
        """加载监控指标"""
        metrics_files = list(self.results_dir.glob("metrics_*.json"))
        
        if not metrics_files:
            return {}
        
        latest_file = max(metrics_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_performance(self, test_results: List[Dict], metrics: Dict) -> Dict:
        """分析性能数据"""
        analysis = {
            'summary': {},
            'bottlenecks': [],
            'recommendations': []
        }
        
        # 汇总统计
        total_requests = sum(r.get('requests', 0) for r in test_results)
        total_failures = sum(r.get('failures', 0) for r in test_results)
        avg_tps = sum(r.get('tps', 0) for r in test_results) / len(test_results) if test_results else 0
        
        # 计算 P99 延迟
        p99_values = [r.get('p99', 0) for r in test_results if r.get('p99')]
        overall_p99 = max(p99_values) if p99_values else 0
        
        analysis['summary'] = {
            'total_requests': total_requests,
            'total_failures': total_failures,
            'failure_rate': (total_failures / total_requests * 100) if total_requests > 0 else 0,
            'avg_tps': avg_tps,
            'overall_p99_ms': overall_p99,
            'interfaces_tested': len(set(r.get('name', '') for r in test_results))
        }
        
        # 识别瓶颈
        # 1. 高延迟接口
        for result in test_results:
            if result.get('p99', 0) > 500:  # P99 > 500ms
                analysis['bottlenecks'].append({
                    'type': 'high_latency',
                    'interface': result.get('name', ''),
                    'p99_ms': result.get('p99', 0),
                    'severity': 'critical' if result.get('p99', 0) > 1000 else 'high',
                    'evidence': f"P99: {result.get('p99', 0):.2f}ms, 平均：{result.get('avg_rt', 0):.2f}ms"
                })
        
        # 2. 高错误率接口
        for result in test_results:
            if result.get('requests', 0) > 0:
                error_rate = result.get('failures', 0) / result.get('requests', 1) * 100
                if error_rate > 1:  # 错误率 > 1%
                    analysis['bottlenecks'].append({
                        'type': 'high_error_rate',
                        'interface': result.get('name', ''),
                        'error_rate': error_rate,
                        'severity': 'critical' if error_rate > 5 else 'high',
                        'evidence': f"错误率：{error_rate:.2f}%, 失败数：{result.get('failures', 0)}"
                    })
        
        # 3. 数据库瓶颈（从监控数据分析）
        if metrics and 'database' in metrics:
            db_metrics = metrics['database']
            if db_metrics:
                # 检查连接池使用率
                for m in db_metrics:
                    pool_usage = m.get('connection_pool_usage', 0)
                    if pool_usage > 0.8:
                        analysis['bottlenecks'].append({
                            'type': 'database_connection_pool',
                            'interface': 'Database',
                            'pool_usage': pool_usage * 100,
                            'severity': 'high',
                            'evidence': f"连接池使用率：{pool_usage*100:.1f}%"
                        })
                
                # 检查慢查询
                for m in db_metrics:
                    slow_queries = m.get('slow_queries', [])
                    if slow_queries:
                        analysis['bottlenecks'].append({
                            'type': 'slow_query',
                            'interface': 'Database',
                            'query_count': len(slow_queries),
                            'severity': 'critical',
                            'evidence': f"慢查询数量：{len(slow_queries)}, 最慢：{slow_queries[0].get('avg_time_ms', 0):.2f}ms"
                        })
                        break
        
        # 4. 系统资源瓶颈
        if metrics and 'system' in metrics:
            sys_metrics = metrics['system']
            if sys_metrics:
                avg_cpu = sum(m.get('cpu_percent', 0) for m in sys_metrics) / len(sys_metrics)
                avg_memory = sum(m.get('memory_percent', 0) for m in sys_metrics) / len(sys_metrics)
                
                if avg_cpu > 80:
                    analysis['bottlenecks'].append({
                        'type': 'high_cpu',
                        'interface': 'System',
                        'cpu_percent': avg_cpu,
                        'severity': 'high',
                        'evidence': f"平均 CPU 使用率：{avg_cpu:.1f}%"
                    })
                
                if avg_memory > 85:
                    analysis['bottlenecks'].append({
                        'type': 'high_memory',
                        'interface': 'System',
                        'memory_percent': avg_memory,
                        'severity': 'critical',
                        'evidence': f"平均内存使用率：{avg_memory:.1f}%"
                    })
        
        # 生成建议
        analysis['recommendations'] = self._generate_recommendations(analysis['bottlenecks'])
        
        return analysis
    
    def _generate_recommendations(self, bottlenecks: List[Dict]) -> List[Dict]:
        """基于瓶颈生成优化建议"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'high_latency':
                recommendations.append({
                    'priority': 'P0' if bottleneck['severity'] == 'critical' else 'P1',
                    'category': '性能优化',
                    'issue': f"接口 {bottleneck['interface']} 延迟过高",
                    'solution': '1. 添加缓存层\n2. 优化数据库查询\n3. 异步处理非关键逻辑',
                    'expected_impact': 'P99 延迟降低 50-80%'
                })
            
            elif bottleneck['type'] == 'slow_query':
                recommendations.append({
                    'priority': 'P0',
                    'category': '数据库优化',
                    'issue': '存在慢查询',
                    'solution': '1. 为查询字段添加索引\n2. 优化 SQL 语句\n3. 考虑读写分离',
                    'expected_impact': '查询速度提升 10-100 倍'
                })
            
            elif bottleneck['type'] == 'database_connection_pool':
                recommendations.append({
                    'priority': 'P1',
                    'category': '数据库优化',
                    'issue': '数据库连接池不足',
                    'solution': '1. 增加连接池大小（pool_size）\n2. 优化查询减少连接占用时间\n3. 使用连接池监控',
                    'expected_impact': '减少连接等待，RT 降低 30-50%'
                })
            
            elif bottleneck['type'] == 'high_cpu':
                recommendations.append({
                    'priority': 'P1',
                    'category': '系统优化',
                    'issue': 'CPU 使用率过高',
                    'solution': '1. 优化 CPU 密集型代码\n2. 使用异步/并发处理\n3. 增加 CPU 核心数',
                    'expected_impact': 'CPU 使用率降低 20-40%'
                })
            
            elif bottleneck['type'] == 'high_memory':
                recommendations.append({
                    'priority': 'P0',
                    'category': '系统优化',
                    'issue': '内存使用率过高',
                    'solution': '1. 检查内存泄漏\n2. 优化数据结构\n3. 增加内存或使用分页查询',
                    'expected_impact': '避免 OOM，提升稳定性'
                })
            
            elif bottleneck['type'] == 'high_error_rate':
                recommendations.append({
                    'priority': 'P0',
                    'category': '稳定性',
                    'issue': f"接口 {bottleneck['interface']} 错误率高",
                    'solution': '1. 查看错误日志定位原因\n2. 增加重试机制\n3. 添加熔断降级',
                    'expected_impact': '错误率降低到 1% 以下'
                })
        
        # 通用建议
        if recommendations:
            recommendations.append({
                'priority': 'P2',
                'category': '架构优化',
                'issue': '建议添加 Redis 缓存层',
                'solution': '对热点数据（文章列表、分类标签、配置信息）添加 Redis 缓存，TTL 5-10 分钟',
                'expected_impact': '数据库 QPS 降低 40-60%'
            })
        
        return recommendations
    
    def generate_markdown_report(self, analysis: Dict, output_file: Optional[str] = None) -> str:
        """生成 Markdown 格式报告"""
        if not output_file:
            output_file = self.report_dir / f"perf_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report = f"""# 性能测试报告

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**测试环境**: {os.getenv('TEST_TARGET_HOST', 'localhost:5000')}

---

## 📊 测试摘要

| 指标 | 值 |
|------|-----|
| 总请求数 | {analysis['summary'].get('total_requests', 0):,} |
| 总失败数 | {analysis['summary'].get('total_failures', 0):,} |
| 失败率 | {analysis['summary'].get('failure_rate', 0):.2f}% |
| 平均 TPS | {analysis['summary'].get('avg_tps', 0):.1f} |
| 整体 P99 | {analysis['summary'].get('overall_p99_ms', 0):.2f}ms |
| 测试接口数 | {analysis['summary'].get('interfaces_tested', 0)} |

---

## 🔍 瓶颈分析

共发现 **{len(analysis['bottlenecks'])}** 个性能瓶颈

"""
        
        # 瓶颈详情
        for i, bottleneck in enumerate(analysis['bottlenecks'], 1):
            severity_emoji = '🔴' if bottleneck['severity'] == 'critical' else '🟠'
            report += f"""
### {severity_emoji} 瓶颈 #{i}: {bottleneck['type']}

- **接口**: {bottleneck.get('interface', 'N/A')}
- **严重程度**: {bottleneck['severity'].upper()}
- **证据**: {bottleneck.get('evidence', 'N/A')}

"""
        
        # 优化建议
        report += f"""
---

## 💡 优化建议

共 **{len(analysis['recommendations'])}** 条建议

"""
        
        for i, rec in enumerate(analysis['recommendations'], 1):
            priority_color = {
                'P0': '🔴',
                'P1': '🟠',
                'P2': '🟡'
            }.get(rec['priority'], '⚪')
            
            report += f"""
### {priority_color} {rec['priority']} - {rec['category']}

**问题**: {rec['issue']}

**解决方案**:
{rec['solution']}

**预期效果**: {rec.get('expected_impact', 'N/A')}

"""
        
        # 总结
        report += f"""
---

## 📈 总结与下一步

### 当前系统能力评估

基于本次压测结果：

1. **系统最大承载**: 待评估（需要更多阶梯测试）
2. **性能瓶颈**: 主要集中在 {', '.join(set(b['type'] for b in analysis['bottlenecks'][:3])) or '无明显瓶颈'}
3. **风险评估**: {'⚠️ 高风险' if any(b['severity'] == 'critical' for b in analysis['bottlenecks']) else '✅ 风险可控'}

### 下一步行动

1. **优先修复 P0 问题** - 解决影响系统稳定性的关键瓶颈
2. **实施 P1 优化** - 提升系统整体性能
3. **回归验证** - 优化后重新压测验证效果
4. **建立监控** - 持续监控性能指标，设置告警

---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 报告已保存：{output_file}")
        return str(output_file)
    
    def generate_html_report(self, markdown_file: str) -> str:
        """将 Markdown 报告转换为 HTML"""
        try:
            import markdown
            from markdown.extensions.tables import TableExtension
            from markdown.extensions.fenced_code import FencedCodeExtension
            
            with open(markdown_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = markdown.markdown(
                md_content,
                extensions=[TableExtension(), FencedCodeExtension()],
                output_format='html5'
            )
            
            # 添加样式
            html_report = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>性能测试报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
            font-weight: 600;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            margin-top: 30px;
        }}
        code {{
            background-color: #f8f8f8;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        pre {{
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            
            html_file = str(markdown_file).replace('.md', '.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            print(f"📄 HTML 报告已保存：{html_file}")
            return html_file
            
        except ImportError:
            print("⚠️  markdown 库未安装，跳过 HTML 报告生成")
            return markdown_file


def main():
    parser = argparse.ArgumentParser(description='性能测试报告生成器')
    parser.add_argument('--results-dir', type=str, default=None,
                        help='结果目录')
    parser.add_argument('--stage', type=int, default=None,
                        help='只分析指定阶梯')
    parser.add_argument('--output', type=str, default=None,
                        help='输出文件名')
    
    args = parser.parse_args()
    
    generator = ReportGenerator(results_dir=args.results_dir)
    
    # 加载数据
    print("📊 加载压测结果...")
    test_results = generator.load_test_results(stage=args.stage)
    
    print("📊 加载监控指标...")
    metrics = generator.load_metrics()
    
    # 分析
    print("🔍 分析性能数据...")
    analysis = generator.analyze_performance(test_results, metrics)
    
    # 生成报告
    print("📝 生成报告...")
    md_file = generator.generate_markdown_report(analysis, output_file=args.output)
    generator.generate_html_report(md_file)
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("📊 性能测试摘要")
    print("=" * 60)
    print(f"总请求数：{analysis['summary'].get('total_requests', 0):,}")
    print(f"失败率：{analysis['summary'].get('failure_rate', 0):.2f}%")
    print(f"平均 TPS: {analysis['summary'].get('avg_tps', 0):.1f}")
    print(f"P99 延迟：{analysis['summary'].get('overall_p99_ms', 0):.2f}ms")
    print(f"\n发现瓶颈：{len(analysis['bottlenecks'])} 个")
    print(f"优化建议：{len(analysis['recommendations'])} 条")
    print("=" * 60)


if __name__ == '__main__':
    main()
