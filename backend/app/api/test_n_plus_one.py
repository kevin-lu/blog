# 测试文件：故意制造 N+1 查询问题
# AI 审查应该能发现这个问题

from flask import Blueprint, jsonify
from app.models import Article, User

bp = Blueprint('test_n_plus_one', __name__)

@bp.route('/test/n-plus-one-bad')
def get_articles_bad():
    """
    坏例子：N+1 查询问题
    
    问题：每次循环都会查询数据库
    如果有 100 篇文章，就会执行 101 次查询
    """
    articles = Article.query.all()  # 1 次查询
    
    result = []
    for article in articles:
        # 坏：每次循环都查询数据库（N 次查询）
        author = User.query.filter_by(id=article.author_id).first()
        result.append({
            'id': article.id,
            'title': article.title,
            'author_name': author.name if author else 'Unknown',
            'created_at': article.created_at
        })
    
    return jsonify({'articles': result, 'query_count': len(articles) + 1})


@bp.route('/test/n-plus-one-good')
def get_articles_good():
    """
    好例子：使用 JOIN 优化查询
    
    只执行 1 次查询获取所有数据
    """
    # 好：使用 JOIN 一次性获取所有数据
    articles = Article.query.join(User).all()
    
    result = []
    for article in articles:
        result.append({
            'id': article.id,
            'title': article.title,
            'author_name': article.author.name if article.author else 'Unknown',
            'created_at': article.created_at
        })
    
    return jsonify({'articles': result, 'query_count': 1})


@bp.route('/test/n-plus-one-better')
def get_articles_better():
    """
    更好的例子：使用 joinedload
    
    SQLAlchemy 的懒加载优化
    """
    from sqlalchemy.orm import joinedload
    
    # 更好：使用 joinedload 预加载关联数据
    articles = Article.query.options(joinedload(Article.author)).all()
    
    result = []
    for article in articles:
        result.append({
            'id': article.id,
            'title': article.title,
            'author_name': article.author.name if article.author else 'Unknown',
            'created_at': article.created_at
        })
    
    return jsonify({'articles': result, 'query_count': 1})
