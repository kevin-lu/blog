"""
Tests for Article Like API
"""
import pytest
from app import create_app
from app.extensions import db
from app.models.article import Article
from app.models.like import ArticleLike
from app.models.admin import Admin
from datetime import datetime, timedelta
import json


@pytest.fixture
def app():
    """Create test app"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_article(app):
    """Create sample article"""
    with app.app_context():
        article = Article(
            slug='test-article',
            title='Test Article',
            content='Test content',
            status='published',
            published_at=datetime.utcnow()
        )
        db.session.add(article)
        db.session.commit()
        return article


class TestLikeArticle:
    """Test like article endpoint"""
    
    def test_like_article_success(self, client, sample_article):
        """Test successful like"""
        response = client.post(f'/api/v1/articles/{sample_article.id}/like')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['like_count'] == 1
        assert data['liked'] is True
    
    def test_like_article_not_found(self, client):
        """Test like non-existent article"""
        response = client.post('/api/v1/articles/99999/like')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_like_article_duplicate(self, client, sample_article):
        """Test duplicate like returns 409"""
        # First like
        client.post(f'/api/v1/articles/{sample_article.id}/like')
        
        # Second like (same IP/session)
        response = client.post(f'/api/v1/articles/{sample_article.id}/like')
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_unlike_article_success(self, client, sample_article):
        """Test successful unlike"""
        # First like
        client.post(f'/api/v1/articles/{sample_article.id}/like')
        
        # Then unlike
        response = client.delete(f'/api/v1/articles/{sample_article.id}/unlike')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['like_count'] == 0
        assert data['liked'] is False
    
    def test_unlike_article_not_liked(self, client, sample_article):
        """Test unlike without prior like returns 404"""
        response = client.delete(f'/api/v1/articles/{sample_article.id}/unlike')
        assert response.status_code == 404
