# 测试文件：故意制造并发和资源问题
# AI 审查应该能发现这些问题

import threading
import time
from flask import Blueprint, jsonify
from app.models import Article

bp = Blueprint('test_concurrency', __name__)

# 全局变量（共享状态）
counter = 0
cache = {}


@bp.route('/test/race-condition-bad')
def increment_counter_bad():
    """
    坏例子：竞态条件
    
    问题：多个请求同时修改全局变量
    可能导致计数不准确
    """
    global counter
    
    # 坏：非原子操作
    # 读 - 改 - 写 不是原子的
    temp = counter
    time.sleep(0.001)  # 模拟处理延迟
    counter = temp + 1
    
    return jsonify({'counter': counter})


@bp.route('/test/race-condition-good')
def increment_counter_good():
    """
    好例子：使用锁保护共享资源
    """
    global counter
    
    # 好：使用锁保证原子性
    lock = threading.Lock()
    with lock:
        counter = counter + 1
    
    return jsonify({'counter': counter})


@bp.route('/test/cache-stale-bad')
def get_article_cache_bad(article_id):
    """
    坏例子：陈旧缓存问题
    
    问题：
    1. 缓存永不过期
    2. 数据库更新后缓存未失效
    3. 可能读取到过期数据
    """
    global cache
    
    # 坏：缓存没有过期时间
    if article_id in cache:
        return jsonify(cache[article_id])
    
    # 从数据库读取
    article = Article.query.get(article_id)
    if article:
        data = article.to_dict()
        cache[article_id] = data  # 永久缓存
        return jsonify(data)
    
    return jsonify({'error': 'Not found'}), 404


@bp.route('/test/cache-stale-good')
def get_article_cache_good(article_id):
    """
    好例子：添加缓存过期时间和失效机制
    """
    import time
    
    CACHE_TTL = 300  # 5 分钟过期
    
    # 检查缓存是否过期
    if article_id in cache:
        cached_data = cache[article_id]
        if time.time() - cached_data['cached_at'] < CACHE_TTL:
            return jsonify(cached_data['data'])
        else:
            # 缓存过期，删除
            del cache[article_id]
    
    # 从数据库读取并缓存
    article = Article.query.get(article_id)
    if article:
        data = {
            'cached_at': time.time(),
            'data': article.to_dict()
        }
        cache[article_id] = data
        return jsonify(article.to_dict())
    
    return jsonify({'error': 'Not found'}), 404


@bp.route('/test/memory-leak-bad')
def process_data_bad():
    """
    坏例子：内存泄漏风险
    
    问题：
    1. 无限增长的全局列表
    2. 没有清理机制
    3. 可能耗尽内存
    """
    global cache
    
    # 坏：不断添加数据，永不清理
    for i in range(1000):
        cache[f'temp_{i}'] = {'data': 'x' * 1000}
    
    return jsonify({'cache_size': len(cache)})


@bp.route('/test/memory-leak-good')
def process_data_good():
    """
    好例子：限制缓存大小，使用 LRU 策略
    """
    from collections import OrderedDict
    
    MAX_CACHE_SIZE = 100
    
    # 好：限制缓存大小
    if not hasattr(process_data_good, 'cache'):
        process_data_good.cache = OrderedDict()
    
    cache = process_data_good.cache
    
    # 添加新数据
    for i in range(10):
        key = f'temp_{i}'
        cache[key] = {'data': 'x' * 100}
        cache.move_to_end(key)
    
    # 清理旧数据（LRU）
    while len(cache) > MAX_CACHE_SIZE:
        cache.popitem(last=False)
    
    return jsonify({'cache_size': len(cache), 'max_size': MAX_CACHE_SIZE})
