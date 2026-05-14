"""
Alert Service
异常情况告警服务 - 支持钉钉、企业微信 Webhook 通知
"""
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertService:
    """告警服务"""
    
    def __init__(self, dingtalk_webhook: Optional[str] = None, wechat_webhook: Optional[str] = None):
        """
        初始化告警服务
        
        Args:
            dingtalk_webhook: 钉钉机器人 Webhook URL
            wechat_webhook: 企业微信机器人 Webhook URL
        """
        self.dingtalk_webhook = dingtalk_webhook
        self.wechat_webhook = wechat_webhook
    
    def send_alert(self, title: str, content: str, alert_type: str = 'error', mention_all: bool = False):
        """
        发送告警通知
        
        Args:
            title: 告警标题
            content: 告警内容
            alert_type: 告警类型 (error, warning, info)
            mention_all: 是否@所有人
        """
        # 根据告警类型选择图标
        icons = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
        }
        icon = icons.get(alert_type, '📢')
        
        # 发送钉钉通知
        if self.dingtalk_webhook:
            self._send_dingtalk(title, content, icon, mention_all)
        
        # 发送企业微信通知
        if self.wechat_webhook:
            self._send_wechat(title, content, icon, mention_all)
    
    def _send_dingtalk(self, title: str, content: str, icon: str, mention_all: bool = False):
        """发送钉钉消息"""
        try:
            headers = {'Content-Type': 'application/json'}
            
            data = {
                'msgtype': 'markdown',
                'markdown': {
                    'title': title,
                    'text': f'### {icon} {title}\n\n{content}\n\n> 时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                },
                'at': {
                    'isAtAll': mention_all,
                }
            }
            
            response = requests.post(self.dingtalk_webhook, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    logger.info(f"钉钉告警发送成功：{title}")
                else:
                    logger.error(f"钉钉告警发送失败：{result.get('errmsg')}")
            else:
                logger.error(f"钉钉告警发送失败，状态码：{response.status_code}")
                
        except Exception as e:
            logger.error(f"发送钉钉告警异常：{e}")
    
    def _send_wechat(self, title: str, content: str, icon: str, mention_all: bool = False):
        """发送企业微信消息"""
        try:
            headers = {'Content-Type': 'application/json'}
            
            data = {
                'msgtype': 'markdown',
                'markdown': {
                    'content': f'### {icon} {title}\n\n{content}\n\n> 时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                }
            }
            
            if mention_all:
                data['mentioned_list'] = ['@all']
            
            response = requests.post(self.wechat_webhook, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    logger.info(f"企业微信告警发送成功：{title}")
                else:
                    logger.error(f"企业微信告警发送失败：{result.get('errmsg')}")
            else:
                logger.error(f"企业微信告警发送失败，状态码：{response.status_code}")
                
        except Exception as e:
            logger.error(f"发送企业微信告警异常：{e}")
    
    def send_crawler_error_alert(self, source_name: str, error_msg: str):
        """发送抓取错误告警"""
        title = "RSS 抓取失败告警"
        content = f"""
**源名称**: {source_name}
**错误信息**: {error_msg}
**影响**: 该源文章无法自动抓取

请检查：
1. 网络连接是否正常
2. RSS 地址是否有效
3. 是否需要代理访问
"""
        self.send_alert(title, content, 'error', mention_all=False)
    
    def send_ai_rewrite_error_alert(self, queue_id: int, error_msg: str, retry_count: int):
        """发送 AI 改写失败告警"""
        title = "AI 改写失败告警"
        content = f"""
**队列 ID**: {queue_id}
**错误信息**: {error_msg}
**重试次数**: {retry_count}
**影响**: 文章无法自动改写发布

请检查：
1. MiniMax API Key 是否配置
2. API 服务是否正常
3. 文章内容格式是否正确
"""
        self.send_alert(title, content, 'error', mention_all=False)
    
    def send_queue_accumulation_alert(self, pending_count: int, estimated_time: float):
        """发送队列积压告警"""
        title = "AI 队列积压告警"
        content = f"""
**待处理数量**: {pending_count}
**预计处理时间**: {estimated_time:.1f} 分钟
**影响**: 文章改写延迟

建议操作：
1. 手动触发队列处理
2. 检查 AI 服务性能
3. 考虑增加处理频率
"""
        self.send_alert(title, content, 'warning', mention_all=False)
    
    def send_daily_report(self, stats: Dict):
        """发送每日执行报告"""
        title = "📊 每日执行报告"
        content = f"""
**日期**: {stats.get('date', '今日')}

**抓取统计**:
- 抓取源数：{stats.get('sources_crawled', 0)}
- 发现文章：{stats.get('articles_found', 0)}
- 新增文章：{stats.get('articles_new', 0)}
- 重复文章：{stats.get('articles_duplicates', 0)}

**AI 改写统计**:
- 处理队列：{stats.get('queue_processed', 0)}
- 改写成功：{stats.get('ai_success', 0)}
- 改写失败：{stats.get('ai_failed', 0)}
- Token 消耗：{stats.get('token_usage', 0)}

**系统状态**:
- 队列待处理：{stats.get('queue_pending', 0)}
- 定时任务：{'正常' if stats.get('scheduler_running', True) else '异常'}
"""
        self.send_alert(title, content, 'info', mention_all=False)


# 全局告警服务实例
_alert_service: Optional[AlertService] = None


def init_alert_service(dingtalk_webhook: Optional[str] = None, wechat_webhook: Optional[str] = None):
    """初始化告警服务"""
    global _alert_service
    _alert_service = AlertService(dingtalk_webhook, wechat_webhook)
    logger.info(f"告警服务已初始化 - 钉钉：{'✓' if dingtalk_webhook else '✗'}, 企业微信：{'✓' if wechat_webhook else '✗'}")


def get_alert_service() -> Optional[AlertService]:
    """获取告警服务实例"""
    return _alert_service


def send_crawler_error(source_name: str, error_msg: str):
    """快捷发送抓取错误告警"""
    if _alert_service:
        _alert_service.send_crawler_error_alert(source_name, error_msg)


def send_ai_rewrite_error(queue_id: int, error_msg: str, retry_count: int):
    """快捷发送 AI 改写失败告警"""
    if _alert_service:
        _alert_service.send_ai_rewrite_error_alert(queue_id, error_msg, retry_count)


def send_queue_accumulation(pending_count: int, estimated_time: float):
    """快捷发送队列积压告警"""
    if pending_count > 10:  # 超过 10 篇才告警
        if _alert_service:
            _alert_service.send_queue_accumulation_alert(pending_count, estimated_time)


def send_daily_report(stats: Dict):
    """快捷发送每日报告"""
    if _alert_service:
        _alert_service.send_daily_report(stats)
