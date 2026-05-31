"""
性能压测脚本 - 基于 Locust
模拟真实用户行为，对核心接口进行阶梯式压测
"""
import random
from locust import HttpUser, task, between, events
from datetime import datetime


class BlogUser(HttpUser):
    """模拟博客访客行为"""
    
    # 任务间等待时间 (秒)
    wait_time = between(1, 3)
    
    # 用户 token (压测前通过登录获取)
    token = None
    user_id = None
    
    @task(3)
    def view_articles(self):
        """浏览文章列表 - 高频操作"""
        page = random.randint(1, 5)
        limit = random.choice([10, 20, 30])
        
        with self.client.get(
            f"/api/v1/articles?page={page}&limit={limit}",
            name="/api/v1/articles [GET]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get articles: {response.status_code}")
    
    @task(2)
    def view_article_detail(self):
        """查看文章详情 - 高频操作"""
        article_id = random.randint(1, 100)
        
        with self.client.get(
            f"/api/v1/articles/{article_id}",
            name="/api/v1/articles/{id} [GET]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()  # 404 也是正常响应
            else:
                response.failure(f"Failed to get article: {response.status_code}")
    
    @task(1)
    def view_categories(self):
        """查看分类列表"""
        self.client.get(
            "/api/v1/categories",
            name="/api/v1/categories [GET]"
        )
    
    @task(1)
    def view_tags(self):
        """查看标签列表"""
        self.client.get(
            "/api/v1/tags",
            name="/api/v1/tags [GET]"
        )


class AuthenticatedUser(HttpUser):
    """模拟已登录用户行为（评论、点赞等）"""
    
    wait_time = between(2, 5)
    
    # 登录凭据 - 压测前配置
    username = "admin"
    password = "admin123"
    
    access_token = None
    
    def on_start(self):
        """用户开始时的登录操作"""
        self.login()
    
    def login(self):
        """执行登录获取 token"""
        with self.client.post(
            "/api/v1/auth/login",
            json={
                "username": self.username,
                "password": self.password
            },
            name="/api/v1/auth/login [POST]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.user_id = data.get('user', {}).get('id')
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")
    
    @task(3)
    def create_comment(self):
        """发表评论 - 写操作"""
        article_id = random.randint(1, 50)
        
        comment_content = random.choice([
            "写得很好，学习了！",
            "感谢分享，受益匪浅",
            "博主厉害，继续支持",
            "这个技术点讲得很清楚",
            "已收藏，慢慢看"
        ])
        
        with self.client.post(
            f"/api/v1/articles/{article_id}/comments",
            json={
                "content": comment_content,
                "parent_id": None
            },
            headers={"Authorization": f"Bearer {self.access_token}"},
            name="/api/v1/articles/{id}/comments [POST]",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            elif response.status_code == 400:
                response.success()  # 验证失败也是正常响应
            else:
                response.failure(f"Comment failed: {response.status_code}")
    
    @task(2)
    def like_article(self):
        """点赞文章"""
        article_id = random.randint(1, 50)
        
        with self.client.post(
            f"/api/v1/articles/{article_id}/like",
            headers={"Authorization": f"Bearer {self.access_token}"},
            name="/api/v1/articles/{id}/like [POST]",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Like failed: {response.status_code}")
    
    @task(1)
    def view_dashboard(self):
        """查看管理后台仪表盘"""
        self.client.get(
            "/api/v1/articles?page=1&limit=10",
            headers={"Authorization": f"Bearer {self.access_token}"},
            name="/api/v1/articles [GET] (auth)"
        )


class AdminUser(HttpUser):
    """模拟管理员操作（发布文章、审核评论等）"""
    
    wait_time = between(5, 10)
    
    username = "admin"
    password = "admin123"
    access_token = None
    
    def on_start(self):
        self.login()
    
    def login(self):
        with self.client.post(
            "/api/v1/auth/login",
            json={
                "username": self.username,
                "password": self.password
            },
            name="/api/v1/auth/login [POST] (admin)"
        ) as response:
            if response.status_code == 200:
                self.access_token = response.json().get('access_token')
    
    @task(2)
    def create_article(self):
        """创建文章 - 重操作"""
        article_data = {
            "title": f"性能测试文章 {datetime.now().timestamp()}",
            "content": "<p>这是测试内容</p>" * 50,
            "summary": "这是一篇用于性能测试的文章摘要",
            "category_id": random.randint(1, 5),
            "tags": [1, 2, 3],
            "cover_image": None,
            "published": True
        }
        
        with self.client.post(
            "/api/v1/articles",
            json=article_data,
            headers={"Authorization": f"Bearer {self.access_token}"},
            name="/api/v1/articles [POST] (admin)",
            catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Create article failed: {response.status_code}")
    
    @task(1)
    def ai_rewrite_article(self):
        """AI 改写文章 - 慢操作"""
        article_id = random.randint(1, 10)
        
        with self.client.post(
            f"/api/v1/articles/{article_id}/ai-rewrite",
            headers={"Authorization": f"Bearer {self.access_token}"},
            name="/api/v1/articles/{id}/ai-rewrite [POST] (admin)",
            catch_response=True
        ) as response:
            # AI 接口通常较慢，放宽超时判断
            if response.status_code in [200, 202]:
                response.success()
            elif response.status_code == 429:
                response.success()  # 限流也是正常响应
            else:
                response.failure(f"AI rewrite failed: {response.status_code}")


# ============= 事件监听器 =============

@events.test_start.add_listener
def on_test_start(environment):
    """压测开始时执行"""
    print("=" * 60)
    print("🚀 性能压测开始")
    print(f"📊 目标主机：{environment.host}")
    print(f"⏰ 开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment):
    """压测结束时执行"""
    print("\n" + "=" * 60)
    print("✅ 性能压测结束")
    print(f"⏰ 结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 输出统计摘要
    stats = environment.stats
    print(f"\n📈 总体统计:")
    print(f"  总请求数：{stats.total.num_requests}")
    print(f"  失败请求数：{stats.total.num_failures}")
    print(f"  失败率：{stats.total.fail_ratio * 100:.2f}%")
    print(f"  平均响应时间：{stats.total.avg_response_time:.2f}ms")
    print(f"  P95 响应时间：{stats.total.get_response_time_percentile(0.95):.2f}ms")
    print(f"  P99 响应时间：{stats.total.get_response_time_percentile(0.99):.2f}ms")


@events.request.add_listener
def on_request(name, exception, **kwargs):
    """每个请求完成时执行 - 可用于自定义监控"""
    # 在这里可以添加自定义的指标采集逻辑
    if exception:
        print(f"❌ 请求失败：{name} - {exception}")
