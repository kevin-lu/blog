# 微信文章批量抓取 + AI 改写实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 实现微信公众号文章合集批量抓取功能，支持自动抓取合集所有文章并加入 AI 改写队列，并发控制为 2 个任务，改写后保存到草稿箱

**架构：** 
- 新增 `WechatAlbumScraper` 类负责抓取微信文章合集列表
- 扩展现有 AI 改写 API 支持批量任务提交
- 增强 `AIQueueService` 并发控制为 2 个并发
- 前端新增批量抓取和任务管理界面

**技术栈：** 
- Python 3.7+
- Flask API
- BeautifulSoup4 (HTML 解析)
- Requests (HTTP 请求)
- Vue.js 3.x (前端)

**配置参数：**
```python
AI_CONCURRENT_LIMIT = 2      # 最大并发数
AI_REQUEST_DELAY = 2         # 请求间隔 (秒)
AI_MAX_RETRIES = 2           # 最大重试次数
AI_TIMEOUT = 300             # 超时时间 (秒)
```

---

## 文件结构

### 新增文件
- `backend/app/services/wechat_album_scraper.py` - 微信合集抓取器
- `backend/scripts/fetch_wechat_articles.py` - 独立脚本 (已创建，需优化)

### 修改文件
- `backend/app/api/v1/articles.py` - 新增批量改写接口
- `backend/app/services/ai_queue.py` - 增强并发控制
- `backend/app/services/ai_rewrite.py` - 优化抓取逻辑
- `backend/app/config.py` - 新增配置项
- `frontend/src/views/admin/ai-generator/AIBatchRewrite.vue` - 批量改写组件 (需创建)

---

## 任务分解

### 任务 1：配置项和常量定义

**文件：**
- 修改：`backend/app/config.py`
- 修改：`backend/app/services/ai_queue.py`

- [ ] **步骤 1：添加 AI 并发控制配置**

```python
# backend/app/config.py

# AI Rewrite Configuration
class Config:
    # ... 其他配置 ...
    
    # MiniMax AI Configuration
    MINIMAX_API_KEY = os.getenv('MINIMAX_API_KEY', '')
    MINIMAX_MODEL = os.getenv('MINIMAX_MODEL', 'MiniMax-M2.7')
    MINIMAX_API_HOST = os.getenv('MINIMAX_API_HOST', 'https://api.minimaxi.com/v1')
    MINIMAX_REQUEST_TIMEOUT = int(os.getenv('MINIMAX_REQUEST_TIMEOUT', '300'))
    MINIMAX_MAX_RETRIES = int(os.getenv('MINIMAX_MAX_RETRIES', '2'))
    
    # AI Queue Configuration
    AI_CONCURRENT_LIMIT = int(os.getenv('AI_CONCURRENT_LIMIT', '2'))  # 最大并发数
    AI_REQUEST_DELAY = int(os.getenv('AI_REQUEST_DELAY', '2'))        # 请求间隔 (秒)
    AI_MAX_RETRIES = int(os.getenv('AI_MAX_RETRIES', '2'))            # 最大重试次数
    AI_TIMEOUT = int(os.getenv('AI_TIMEOUT', '300'))                  # 超时时间 (秒)
```

- [ ] **步骤 2：更新 `.env.example`**

```bash
# .env.example

# MiniMax AI Configuration
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_MODEL=MiniMax-M2.7
MINIMAX_API_HOST=https://api.minimaxi.com/v1
MINIMAX_REQUEST_TIMEOUT=300
MINIMAX_MAX_RETRIES=2

# AI Queue Configuration
AI_CONCURRENT_LIMIT=2
AI_REQUEST_DELAY=2
AI_MAX_RETRIES=2
AI_TIMEOUT=300
```

- [ ] **步骤 3：Commit**

```bash
git add backend/app/config.py .env.example
git commit -m "feat: add AI queue configuration for concurrent control"
```

---

### 任务 2：微信合集抓取器实现

**文件：**
- 创建：`backend/app/services/wechat_album_scraper.py`
- 测试：`backend/tests/services/test_wechat_album_scraper.py`

- [ ] **步骤 1：创建 WechatAlbumScraper 类**

```python
"""
Wechat Album Scraper
抓取微信公众号文章合集列表
"""
import re
from typing import Dict, List, Optional
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup


class WechatAlbumScraper:
    """微信公众号合集抓取器"""
    
    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48'
        ),
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://mp.weixin.qq.com/',
    }
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def fetch_album_info(self, album_url: str) -> Optional[Dict]:
        """
        抓取合集基本信息
        
        Args:
            album_url: 合集链接
            
        Returns:
            合集信息：{name, total_count, description, cover_image}
        """
        try:
            response = self.session.get(album_url, timeout=self.timeout)
            response.raise_for_status()
            
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取合集名称
            name_elem = soup.find('div', {'id': 'js_tag_name'})
            name = name_elem.get_text(strip=True) if name_elem else '未知合集'
            
            # 提取文章总数
            count_text = soup.find('span', string=re.compile(r'\d+\s*篇'))
            total_count = 0
            if count_text:
                match = re.search(r'(\d+)', count_text.get_text())
                if match:
                    total_count = int(match.group(1))
            
            # 提取描述
            desc_elem = soup.find('meta', {'name': 'description'})
            description = desc_elem.get('content', '') if desc_elem else ''
            
            # 提取封面图
            cover_elem = soup.find('img', {'id': 'js_header_image'})
            cover_image = cover_elem.get('src', '') if cover_elem else ''
            
            return {
                'name': name,
                'total_count': total_count,
                'description': description,
                'cover_image': cover_image,
            }
            
        except Exception as e:
            print(f"抓取合集信息失败：{e}")
            return None
    
    def fetch_article_list(self, album_url: str) -> List[Dict]:
        """
        抓取合集文章列表
        
        Args:
            album_url: 合集链接
            
        Returns:
            文章列表：[{title, url, digest, cover_image}]
        """
        try:
            response = self.session.get(album_url, timeout=self.timeout)
            response.raise_for_status()
            
            html = response.text
            
            # 使用正则提取文章列表
            pattern = r'<li[^>]*class="[^"]*album__list-item[^"]*"[^>]*' \
                     r'data-msgid="(\d+)"[^>]*data-itemidx="(\d+)"[^>]*' \
                     r'data-link="([^"]*)"[^>]*data-title="([^"]*)"'
            
            matches = re.findall(pattern, html, re.DOTALL)
            
            articles = []
            for msgid, itemidx, url, title in matches:
                articles.append({
                    'index': int(itemidx),
                    'title': self._decode_html_entities(title),
                    'url': self._clean_url(url),
                    'msgid': msgid,
                })
            
            # 按索引排序
            articles.sort(key=lambda x: x['index'])
            
            return articles
            
        except Exception as e:
            print(f"抓取文章列表失败：{e}")
            return []
    
    def _decode_html_entities(self, text: str) -> str:
        """解码 HTML 实体"""
        return unquote(text.replace('&amp;', '&')
                           .replace('&lt;', '<')
                           .replace('&gt;', '>')
                           .replace('&quot;', '"')
                           .replace('&#39;', "'"))
    
    def _clean_url(self, url: str) -> str:
        """清理 URL"""
        return url.replace('&amp;', '&')
```

- [ ] **步骤 2：编写测试**

```python
"""Tests for WechatAlbumScraper"""
import pytest
from app.services.wechat_album_scraper import WechatAlbumScraper


class TestWechatAlbumScraper:
    
    def test_fetch_album_info(self):
        """测试抓取合集信息"""
        scraper = WechatAlbumScraper()
        album_url = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkzMDI1NjcyOQ==&action=getalbum&album_id=3022691668057276419"
        
        info = scraper.fetch_album_info(album_url)
        
        assert info is not None
        assert 'name' in info
        assert 'total_count' in info
        assert info['name'] == 'AI'
        assert info['total_count'] > 0
    
    def test_fetch_article_list(self):
        """测试抓取文章列表"""
        scraper = WechatAlbumScraper()
        album_url = "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkzMDI1NjcyOQ==&action=getalbum&album_id=3022691668057276419"
        
        articles = scraper.fetch_article_list(album_url)
        
        assert len(articles) > 0
        assert all('title' in a and 'url' in a for a in articles)
    
    def test_decode_html_entities(self):
        """测试 HTML 实体解码"""
        scraper = WechatAlbumScraper()
        
        text = "测试 &amp; &lt; &gt; &quot; &#39;"
        decoded = scraper._decode_html_entities(text)
        
        assert decoded == "测试 & < > \" '"
```

- [ ] **步骤 3：运行测试**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog/backend
pytest tests/services/test_wechat_album_scraper.py -v
```

预期：3 个测试全部通过

- [ ] **步骤 4：Commit**

```bash
git add backend/app/services/wechat_album_scraper.py backend/tests/services/test_wechat_album_scraper.py
git commit -m "feat: implement WechatAlbumScraper for fetching article lists"
```

---

### 任务 3：批量改写 API 接口

**文件：**
- 修改：`backend/app/api/v1/articles.py`

- [ ] **步骤 1：导入新依赖**

```python
# backend/app/api/v1/articles.py

# 在文件开头添加导入
from app.services.wechat_album_scraper import WechatAlbumScraper
from app.services.ai_queue import enqueue_article
```

- [ ] **步骤 2：添加批量改写接口**

```python
@bp.route('/ai-batch', methods=['POST'])
@jwt_required()
@limiter.limit(lambda: current_app.config.get('AI_BATCH_RATE_LIMIT', '5 per hour'))
def ai_batch_rewrite():
    """批量提交 AI 改写任务（支持微信合集）"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Request body is required'}), 400

    source_urls = data.get('sourceUrls', [])
    album_url = data.get('albumUrl')
    rewrite_strategy = data.get('rewriteStrategy', 'standard')
    template_type = data.get('templateType', 'tutorial')
    auto_publish = bool(data.get('autoPublish', False))

    # 验证参数
    if not source_urls and not album_url:
        return jsonify({'error': '请提供文章链接列表或合集链接'}), 400

    if rewrite_strategy not in ('standard', 'deep', 'creative'):
        return jsonify({'error': '不支持的改写策略'}), 400
    
    if template_type not in ('tutorial', 'concept', 'comparison', 'practice'):
        return jsonify({'error': '不支持的文章模板'}), 400

    if not current_app.config.get('MINIMAX_API_KEY'):
        return jsonify({'error': '后端未配置 MINIMAX_API_KEY'}), 400

    # 如果是合集链接，先抓取文章列表
    if album_url:
        try:
            scraper = WechatAlbumScraper()
            articles = scraper.fetch_article_list(album_url)
            
            if not articles:
                return jsonify({'error': '合集中没有找到文章'}), 404
            
            source_urls = [article['url'] for article in articles]
            
        except Exception as e:
            return jsonify({'error': f'抓取合集失败：{str(e)}'}), 500

    # 批量创建改写任务
    tasks = []
    for url in source_urls:
        if not url.strip():
            continue
            
        try:
            # 先抓取文章获取标题
            scraper = WechatAlbumScraper()
            article_info = scraper.fetch_single_article_info(url)
            title = article_info.get('title', '未知标题')
            content = article_info.get('content', '')
            
            # 加入 AI 改写队列
            queue_item = enqueue_article(
                title=title,
                original_content=content,
                source_url=url,
                author='码哥跳动',
                rewrite_strategy=rewrite_strategy,
                template_type=template_type,
                auto_publish=auto_publish,
                priority=0,
            )
            
            tasks.append({
                'queueId': queue_item.queue_id,
                'title': title,
                'url': url,
                'status': 'pending',
            })
            
        except Exception as e:
            tasks.append({
                'url': url,
                'status': 'failed',
                'error': str(e),
            })

    return jsonify({
        'success': True,
        'data': {
            'total': len(tasks),
            'tasks': tasks,
            'concurrentLimit': current_app.config.get('AI_CONCURRENT_LIMIT', 2),
        },
    }), 202
```

- [ ] **步骤 3：添加单篇文章信息抓取方法**

```python
# 在 WechatAlbumScraper 类中添加方法

def fetch_single_article_info(self, url: str) -> Dict:
    """
    抓取单篇文章信息
    
    Args:
        url: 文章链接
        
    Returns:
        {title, content, description, cover_image}
    """
    try:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title_elem = soup.find('h1', {'id': 'activity-name'})
        title = title_elem.get_text(strip=True) if title_elem else ''
        
        # 提取描述
        desc_elem = soup.find('meta', {'name': 'description'})
        description = desc_elem.get('content', '') if desc_elem else ''
        
        # 提取封面图
        cover_elem = soup.find('meta', {'property': 'og:image'})
        cover_image = cover_elem.get('content', '') if cover_elem else ''
        
        # 提取正文
        content_elem = soup.find('div', {'id': 'js_content'})
        if not content_elem:
            content_elem = soup.find('div', class_='rich_media_content')
        
        content = content_elem.prettify() if content_elem else ''
        
        return {
            'title': title,
            'content': content,
            'description': description,
            'cover_image': cover_image,
        }
        
    except Exception as e:
        print(f"抓取单篇文章失败：{e}")
        return {'title': '', 'content': '', 'description': '', 'cover_image': ''}
```

- [ ] **步骤 4：Commit**

```bash
git add backend/app/api/v1/articles.py
git commit -m "feat: add batch AI rewrite API endpoint"
```

---

### 任务 4：增强 AI 队列并发控制

**文件：**
- 修改：`backend/app/services/ai_queue.py`

- [ ] **步骤 1：添加并发控制逻辑**

```python
# backend/app/services/ai_queue.py

# 在文件开头添加
from threading import Lock
from datetime import timedelta

_queue_lock = Lock()


def get_processing_count() -> int:
    """获取正在处理的任务数"""
    return AIQueue.query.filter_by(status='processing').count()


def can_process_next() -> bool:
    """检查是否可以处理下一个任务"""
    concurrent_limit = Config.AI_CONCURRENT_LIMIT
    processing_count = get_processing_count()
    return processing_count < concurrent_limit


def process_queue():
    """
    队列处理器 - 由定时任务调用
    并发控制：最多 2 个任务同时处理
    """
    with _queue_lock:
        if not can_process_next():
            return
        
        # 获取下一个待处理任务
        task = get_next_queue_task()
        if not task:
            return
        
        # 处理任务
        process_ai_task(task)
```

- [ ] **步骤 2：优化 `process_ai_task` 方法**

```python
def process_ai_task(queue_item: AIQueue) -> bool:
    """
    处理单个 AI 改写任务（带并发控制和延迟）
    
    Args:
        queue_item: 队列项
        
    Returns:
        True 表示成功，False 表示失败
    """
    try:
        # 更新状态
        queue_item.status = 'processing'
        queue_item.started_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"开始处理 AI 任务：{queue_item.queue_id}")
        
        # 调用 MiniMax AI 改写（带延迟，避免 API 限流）
        delay_seconds = Config.AI_REQUEST_DELAY
        rewritten_content = call_minimax_ai_with_delay(
            title=queue_item.title,
            content=queue_item.original_content,
            strategy=queue_item.rewrite_strategy or 'standard',
            delay_seconds=delay_seconds,
        )
        
        if not rewritten_content:
            raise Exception("AI 改写返回空内容")
        
        # 创建文章并保存为草稿（不直接发布）
        article = create_and_save_draft(
            title=queue_item.title,
            content=rewritten_content,
            source_url=queue_item.source_url,
            author=queue_item.author,
            published_at=queue_item.published_at,
            ai_model='minimax-abab6.5',
            rewrite_strategy=queue_item.rewrite_strategy or 'standard',
        )
        
        # 更新队列状态
        queue_item.status = 'completed'
        queue_item.article_id = article.id
        queue_item.rewritten_content = rewritten_content
        queue_item.ai_model = 'minimax-abab6.5'
        queue_item.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"AI 任务完成：{queue_item.queue_id}, 文章 ID: {article.id}, 状态：草稿")
        
        return True
        
    except Exception as e:
        logger.error(f"AI 任务失败：{queue_item.queue_id}, 错误：{e}")
        
        # 失败重试逻辑
        queue_item.retry_count += 1
        if queue_item.retry_count >= queue_item.max_retries:
            queue_item.status = 'failed'
            queue_item.error_message = str(e)
            logger.error(f"AI 任务达到最大重试次数，标记为失败：{queue_item.queue_id}")
            
            # 发送告警
            from app.services.alert import send_ai_rewrite_error
            send_ai_rewrite_error(queue_item.queue_id, str(e), queue_item.retry_count)
        else:
            queue_item.status = 'pending'  # 重新加入队列
            logger.info(f"AI 任务失败，将重新加入队列（重试 {queue_item.retry_count}/{queue_item.max_retries}）: {queue_item.queue_id}")
        
        db.session.commit()
        return False
```

- [ ] **步骤 3：添加队列状态查询接口**

```python
# backend/app/api/v1/articles.py

@bp.route('/ai-queue/status', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def ai_queue_status():
    """获取 AI 队列状态"""
    pending_count = AIQueue.query.filter_by(status='pending').count()
    processing_count = AIQueue.query.filter_by(status='processing').count()
    completed_count = AIQueue.query.filter_by(status='completed').count()
    failed_count = AIQueue.query.filter_by(status='failed').count()
    
    concurrent_limit = current_app.config.get('AI_CONCURRENT_LIMIT', 2)
    
    return jsonify({
        'queue': {
            'pending': pending_count,
            'processing': processing_count,
            'completed': completed_count,
            'failed': failed_count,
            'concurrent_limit': concurrent_limit,
            'can_process': processing_count < concurrent_limit,
        },
    }), 200
```

- [ ] **步骤 4：Commit**

```bash
git add backend/app/services/ai_queue.py backend/app/api/v1/articles.py
git commit -m "feat: add concurrent control to AI queue (limit: 2)"
```

---

### 任务 5：前端批量改写组件

**文件：**
- 创建：`frontend/src/views/admin/ai-generator/AIBatchRewrite.vue`
- 创建：`frontend/src/stores/ai-batch.ts`

- [ ] **步骤 1：创建批量改写组件**

```vue
<template>
  <div class="ai-batch-rewrite">
    <a-card title="批量 AI 改写">
      <a-form layout="vertical">
        <!-- 合集链接输入 -->
        <a-form-item label="微信合集链接">
          <a-input
            v-model:value="albumUrl"
            placeholder="https://mp.weixin.qq.com/mp/appmsgalbum?..."
            size="large"
          >
            <template #prefix>
              <LinkOutlined />
            </template>
          </a-input>
          <a-button 
            type="primary" 
            @click="fetchAlbumArticles"
            :loading="fetching"
            :disabled="!albumUrl"
          >
            抓取文章列表
          </a-button>
        </a-form-item>

        <!-- 文章列表展示 -->
        <div v-if="articles.length > 0" class="article-list">
          <div class="article-list-header">
            <h3>找到 {{ articles.length }} 篇文章</h3>
            <a-checkbox v-model:checked="selectAll" @change="toggleSelectAll">
              全选
            </a-checkbox>
          </div>
          
          <a-list
            :data-source="articles"
            :loading="fetching"
            size="small"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-checkbox
                  v-model:checked="item.selected"
                  @change="updateSelectedCount"
                >
                  {{ item.title }}
                </a-checkbox>
                <a-tag color="blue">{{ item.index }}</a-tag>
              </a-list-item>
            </template>
          </a-list>

          <!-- 批量操作按钮 -->
          <div class="batch-actions">
            <a-alert
              message="已选择 {{ selectedCount }} 篇文章"
              type="info"
              show-icon
            />
            <a-button
              type="primary"
              size="large"
              @click="submitBatchRewrite"
              :loading="submitting"
              :disabled="selectedCount === 0"
            >
              开始批量改写 (并发 2 个)
            </a-button>
          </div>
        </div>
      </a-form>
    </a-card>

    <!-- 任务进度 -->
    <AIQueueProgress v-if="showProgress" :tasks="tasks" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import { LinkOutlined } from '@ant-design/icons-vue'
import AIQueueProgress from './AIQueueProgress.vue'
import { useAIBatchStore } from '@/stores/ai-batch'

const albumUrl = ref('')
const fetching = ref(false)
const submitting = ref(false)
const articles = ref<any[]>([])
const selectAll = ref(false)
const selectedCount = ref(0)
const showProgress = ref(false)
const tasks = ref<any[]>([])

const batchStore = useAIBatchStore()

// 抓取合集文章
async function fetchAlbumArticles() {
  if (!albumUrl.value) {
    message.warning('请输入合集链接')
    return
  }

  fetching.value = true
  try {
    const response = await fetch(`/api/v1/articles/album/articles?url=${encodeURIComponent(albumUrl.value)}`)
    const data = await response.json()
    
    if (data.success) {
      articles.value = data.data.articles.map((article: any) => ({
        ...article,
        selected: false,
      }))
      selectAll.value = false
      selectedCount.value = 0
      message.success(`找到 ${articles.value.length} 篇文章`)
    } else {
      message.error(data.error || '抓取失败')
    }
  } catch (error) {
    message.error('抓取失败：' + error)
  } finally {
    fetching.value = false
  }
}

// 全选/取消全选
function toggleSelectAll() {
  articles.value.forEach(article => {
    article.selected = selectAll.value
  })
  updateSelectedCount()
}

// 更新选中数量
function updateSelectedCount() {
  selectedCount.value = articles.value.filter(a => a.selected).length
}

// 提交批量改写
async function submitBatchRewrite() {
  const selectedArticles = articles.value.filter(a => a.selected)
  
  if (selectedArticles.length === 0) {
    message.warning('请至少选择一篇文章')
    return
  }

  submitting.value = true
  try {
    const response = await fetch('/api/v1/articles/ai-batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sourceUrls: selectedArticles.map(a => a.url),
        rewriteStrategy: 'standard',
        templateType: 'tutorial',
        autoPublish: false, // 保存到草稿箱
      }),
    })
    
    const data = await response.json()
    
    if (data.success) {
      tasks.value = data.data.tasks
      showProgress.value = true
      message.success(`已提交 ${data.data.total} 个改写任务`)
    } else {
      message.error(data.error || '提交失败')
    }
  } catch (error) {
    message.error('提交失败：' + error)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.ai-batch-rewrite {
  margin-top: 24px;
}

.article-list {
  margin-top: 24px;
  max-height: 400px;
  overflow-y: auto;
}

.article-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.batch-actions {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
```

- [ ] **步骤 2：创建状态管理**

```typescript
// frontend/src/stores/ai-batch.ts
import { defineStore } from 'pinia'

export interface BatchTask {
  queueId: string
  title: string
  url: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  error?: string
}

export const useAIBatchStore = defineStore('ai-batch', {
  state: () => ({
    tasks: [] as BatchTask[],
    isProcessing: false,
  }),

  getters: {
    pendingTasks: (state) => state.tasks.filter(t => t.status === 'pending'),
    processingTasks: (state) => state.tasks.filter(t => t.status === 'processing'),
    completedTasks: (state) => state.tasks.filter(t => t.status === 'completed'),
    failedTasks: (state) => state.tasks.filter(t => t.status === 'failed'),
    progress: (state) => {
      if (state.tasks.length === 0) return 0
      const completed = state.tasks.filter(t => t.status === 'completed').length
      return Math.round((completed / state.tasks.length) * 100)
    },
  },

  actions: {
    addTasks(tasks: BatchTask[]) {
      this.tasks.push(...tasks)
    },
    updateTask(queueId: string, updates: Partial<BatchTask>) {
      const task = this.tasks.find(t => t.queueId === queueId)
      if (task) {
        Object.assign(task, updates)
      }
    },
    clearCompleted() {
      this.tasks = this.tasks.filter(t => t.status !== 'completed')
    },
  },
})
```

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/views/admin/ai-generator/AIBatchRewrite.vue frontend/src/stores/ai-batch.ts
git commit -m "feat: add batch rewrite UI component"
```

---

### 任务 6：测试和文档

**文件：**
- 创建：`docs/AI_BATCH_REWRITE_GUIDE.md`

- [ ] **步骤 1：编写使用文档**

```markdown
# AI 批量改写使用指南

## 功能概述

支持微信公众号文章合集批量抓取和 AI 改写，自动并发控制（2 个任务同时处理），改写后保存到草稿箱。

## 使用流程

### 1. 输入合集链接

访问 `http://localhost:3002/admin/ai-generator`，选择"批量改写"标签页。

输入微信文章合集链接，例如：
```
https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkzMDI1NjcyOQ==&action=getalbum&album_id=3022691668057276419
```

### 2. 抓取文章列表

点击"抓取文章列表"按钮，系统会自动：
- 抓取合集中的所有文章
- 显示文章列表（标题、序号）
- 支持全选/单选

### 3. 提交批量改写

选择需要改写的文章，点击"开始批量改写"。

系统会：
- 自动抓取每篇文章内容
- 加入 AI 改写队列（最多 2 个并发）
- 保存到草稿箱（不直接发布）

### 4. 查看进度

在"任务进度"面板可以实时查看：
- 待处理任务数
- 正在处理任务数
- 已完成任务数
- 失败任务数

## 并发控制

**配置参数：**
- `AI_CONCURRENT_LIMIT = 2` - 最大并发数
- `AI_REQUEST_DELAY = 2` - 请求间隔（秒）
- `AI_MAX_RETRIES = 2` - 最大重试次数

**优势：**
- ✅ 避免触发 MiniMax API 限流
- ✅ 稳定的改写质量
- ✅ 失败自动重试

## 成本估算

**MiniMax API 定价：**
- 输入：$0.3 / 百万 tokens
- 输出：$1.2 / 百万 tokens

**单篇成本：**
- 3000 字文章：约 ¥0.016

**批量成本（10 篇）：**
- 约 ¥0.16

## 最佳实践

1. **分批处理**
   - 建议每批 10-20 篇
   - 避免大量任务积压

2. **人工审核**
   - 所有改写保存到草稿箱
   - 人工审核技术准确性
   - 添加个人见解

3. **定时处理**
   - 系统会自动处理队列
   - 无需手动干预

## 常见问题

### Q: 抓取失败怎么办？
A: 检查链接是否有效，或稍后重试。微信文章可能需要权限访问。

### Q: 任务卡住不动？
A: 查看后端日志，可能是 API 调用超时。系统会自动重试。

### Q: 如何调整并发数？
A: 修改 `.env` 文件中的 `AI_CONCURRENT_LIMIT`，重启服务。
```

- [ ] **步骤 2：Commit**

```bash
git add docs/AI_BATCH_REWRITE_GUIDE.md
git commit -m "docs: add AI batch rewrite guide"
```

---

## 自检

- [ ] **规格覆盖度检查：**
  - ✅ 微信合集抓取功能
  - ✅ 批量改写 API
  - ✅ 并发控制（2 个）
  - ✅ 保存到草稿箱
  - ✅ 前端界面

- [ ] **配置一致性检查：**
  - ✅ `AI_CONCURRENT_LIMIT = 2` 在所有文件中一致
  - ✅ `AI_REQUEST_DELAY = 2` 在所有文件中一致

- [ ] **错误处理检查：**
  - ✅ 抓取失败处理
  - ✅ API 调用失败重试
  - ✅ 队列任务失败标记

---

## 执行交接

计划已完成并保存到 `/Users/luzengbiao/traeProjects/blog/blog/backend/scripts/IMPLEMENTATION_PLAN.md`。

**两种执行方式：**

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

**选哪种方式？**
