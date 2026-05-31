# 测试文件：故意制造信任边界问题
# AI 审查应该能发现这些安全问题

from flask import Blueprint, request, jsonify
from app.models import Comment, Article
import re

bp = Blueprint('test_trust_boundary', __name__)


@bp.route('/test/trust-boundary-bad', methods=['POST'])
def create_comment_bad():
    """
    坏例子：信任边界问题
    
    问题：
    1. 直接使用用户输入，未验证类型
    2. 未验证范围（user_id 可能是负数）
    3. 未清理输入（XSS 攻击风险）
    4. 未检查文章是否存在
    """
    # 坏：完全信任用户输入
    user_id = request.json.get('user_id')
    article_id = request.json.get('article_id')
    content = request.json.get('content')
    
    # 直接使用，存在安全风险
    comment = Comment(
        user_id=user_id,
        article_id=article_id,
        content=content
    )
    
    return jsonify({
        'status': 'success',
        'comment': {
            'user_id': user_id,
            'article_id': article_id,
            'content': content
        }
    })


@bp.route('/test/trust-boundary-good', methods=['POST'])
def create_comment_good():
    """
    好例子：添加完整的验证和清理
    
    验证：
    1. 类型验证（必须是整数）
    2. 范围验证（必须大于 0）
    3. 长度限制
    4. 清理输入（移除 HTML 标签）
    5. 检查资源是否存在
    """
    # 获取输入
    user_id = request.json.get('user_id')
    article_id = request.json.get('article_id')
    content = request.json.get('content')
    
    # 1. 类型验证
    if not isinstance(user_id, int) or user_id <= 0:
        return jsonify({'error': 'Invalid user_id'}), 400
    
    if not isinstance(article_id, int) or article_id <= 0:
        return jsonify({'error': 'Invalid article_id'}), 400
    
    # 2. 长度验证
    if not content or len(content) > 10000:
        return jsonify({'error': 'Invalid content'}), 400
    
    # 3. 检查资源是否存在
    article = Article.query.get(article_id)
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    # 4. 清理输入（防止 XSS）
    # 移除 HTML 标签
    content = re.sub(r'<[^>]+>', '', content)
    # 移除脚本标签
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    # 转义特殊字符
    content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # 创建评论
    comment = Comment(
        user_id=user_id,
        article_id=article_id,
        content=content
    )
    
    return jsonify({
        'status': 'success',
        'comment': {
            'id': comment.id,
            'user_id': user_id,
            'article_id': article_id,
            'content': content
        }
    }), 201


@bp.route('/test/sql-injection-bad', methods=['GET'])
def search_articles_bad():
    """
    坏例子：SQL 注入风险
    
    问题：使用字符串拼接构建 SQL 查询
    """
    from app import db
    
    keyword = request.args.get('keyword', '')
    
    # 坏：字符串拼接 SQL
    sql = f"SELECT * FROM article WHERE title LIKE '%{keyword}%'"
    articles = db.session.execute(sql).fetchall()
    
    return jsonify({'articles': [a.to_dict() for a in articles]})


@bp.route('/test/sql-injection-good', methods=['GET'])
def search_articles_good():
    """
    好例子：使用参数化查询
    
    使用 SQLAlchemy ORM，自动防止 SQL 注入
    """
    keyword = request.args.get('keyword', '')
    
    # 好：使用 ORM 和参数化查询
    articles = Article.query.filter(
        Article.title.ilike(f'%{keyword}%')
    ).all()
    
    return jsonify({'articles': [a.to_dict() for a in articles]})
