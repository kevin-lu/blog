"""
AI rewrite workflow helpers.
"""
import json
import re
import socket
import time
import unicodedata
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.extensions import db
from app.models.article import Article
from app.services.ai_tasks import update_task


WECHAT_REQUEST_HEADERS = (
    {
        'User-Agent': (
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) '
            'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48'
        ),
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://mp.weixin.qq.com/',
    },
    {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        ),
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://mp.weixin.qq.com/',
    },
)


def extract_images_from_html(html: str) -> list:
    """从 HTML 中提取所有图片信息"""
    if not html:
        return []
    
    images = []
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*(?:alt=["\']([^"\']*)["\'])?[^>]*>'
    
    for match in re.finditer(img_pattern, html, re.IGNORECASE):
        src = match.group(1)
        alt = match.group(2) or ''
        
        # 跳过过小的图片（可能是图标、表情等）
        if any(skip in src.lower() for skip in ['emoji', 'icon', 'gif', 'spacer', 'blank']):
            continue
        
        images.append({
            'src': src,
            'alt': alt,
            'type': 'image'
        })
    
    return images


PROMPTS = {
    'standard': {
        'extract': """你是一个专业的技术编辑。请从以下文章中提取核心观点和技术要点。

任务要求：
1. 提取核心主题（1 句话）
2. 详细列出所有关键观点（不要遗漏任何重要观点）
3. 提取所有技术细节、代码示例、配置参数
4. 提取文章中的所有案例、场景、数据
5. 忽略广告、推广等无关内容

重要：必须保留原文的所有技术细节和深度，不要简化！

只输出提取结果，不要复述要求。""",
        'rewrite': """你是一个资深技术博主，擅长深入讲解技术。请基于以下核心观点重新创作一篇文章。

写作要求：
1. 使用自己的表达方式，但必须保留所有技术细节和深度
2. 语言风格自然，像在给朋友讲技术，但内容要详细
3. 结构清晰，逻辑连贯
4. 保留所有代码示例、配置参数、技术术语
5. 添加详细的示例、经验和踩坑提醒
6. 每个观点都要详细展开，不要一笔带过
7. 字数要求：至少 3000-5000 字，确保内容充实
8. 输出 Markdown 内容

禁止：
- 不要过度简化内容
- 不要省略技术细节
- 不要删除代码示例
- 不要合并或压缩段落

直接开始写文章，不要说废话。""",
        'layout': """你是一个技术内容排版编辑。请把下面文章整理成适合博客发布的 Markdown。

规则：
1. 生成一个一级标题
2. 使用二级、三级、四级标题组织结构
3. 关键术语加粗
4. 代码使用 fenced code block，并添加详细注释
5. 重要提示使用引用块（>）突出显示
6. 对比内容使用表格
7. 复杂流程使用 Mermaid 图表表示
8. 直接输出最终 Markdown

注意：保留所有技术细节，不要删除任何内容。
""",
    },
    'deep': {
        'extract': """你是一个资深技术分析师。请详细提炼下面文章的所有技术内容。

任务要求：
1. 提取所有核心技术原理和实现细节
2. 列出所有优缺点分析
3. 提取所有适用场景和局限性
4. 保留所有技术术语、参数、配置
5. 提取文中的案例、数据、对比

重要：必须详细、完整，不要遗漏任何技术细节！

只输出分析结果，不要解释过程。""",
        'rewrite': """你是一个经验丰富的技术专家，擅长深度技术分析。请基于给出的要点，写一篇深入的技术分析文章。

要求：
1. 详细讲解技术原理和实现细节
2. 保留所有优缺点分析和对比
3. 增加详细的案例分析和避坑建议
4. 给出实际应用场景和落地建议
5. 每个技术点都要深入展开，不要浅尝辄止
6. 字数要求：4000-6000 字，确保深度和广度
7. 使用 Markdown
8. 直接开始写正文

禁止：
- 不要简化技术内容
- 不要省略实现细节
- 不要删除对比分析
- 不要合并技术要点
""",
        'layout': """请将内容整理成面向技术博客的 Markdown。

要求：
1. 一级标题 + 多级章节标题（H2/H3/H4）
2. 增加"最佳实践"、"常见问题"、"避坑指南"等实用章节
3. 代码示例添加详细注释
4. 对比内容使用表格展示
5. 复杂流程使用 Mermaid 流程图
6. 重点提示使用引用块突出
7. 直接输出整理后的 Markdown

注意：保持技术深度，不要删除任何细节。
""",
    },
    'creative': {
        'extract': """请详细提取这篇文章的所有技术内容。

任务要求：
1. 提取讨论的技术主题和问题
2. 提取所有核心思路和技术方案
3. 保留所有技术细节、代码、参数
4. 提取文中的案例、场景、数据

详细提取，不要遗漏重要内容。""",
        'rewrite': """你是一个有个人风格的技术博主。请围绕这些主题完全原创一篇新文章。

要求：
1. 保留所有技术主题和核心内容，但表达和结构重新创作
2. 保留所有技术细节、代码示例、配置参数
3. 文风可以轻松，但技术内容必须详细深入
4. 添加个人见解、经验和案例
5. 字数要求：3000-5000 字
6. 使用 Markdown
7. 直接输出文章

禁止：
- 不要简化技术内容
- 不要省略关键细节
- 不要删除代码示例
""",
        'layout': """请把文章整理成适合发布的 Markdown，保证标题、列表、引用和代码块清晰。

要求：
1. 使用多级标题组织内容
2. 代码块添加语言标识和注释
3. 重点内容加粗或使用引用块
4. 复杂流程用 Mermaid 图表表示
5. 直接输出最终 Markdown
""",
    },
}


class MiniMaxClient:
    """Thin client for MiniMax OpenAI-compatible chat completions."""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        request_timeout: int = 300,
        max_retries: int = 2,
    ):
        self.api_key = api_key
        self.model = (model or 'MiniMax-M2.7').strip()
        self.base_url = (base_url or 'https://api.minimaxi.com/v1/chat/completions').strip()
        self.request_timeout = max(int(request_timeout or 300), 30)
        self.max_retries = max(int(max_retries or 0), 0)

    def chat(self, messages, temperature: float = 0.7, max_tokens: int = 4000) -> Dict[str, Any]:
        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        request = Request(
            self.base_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                with urlopen(request, timeout=self.request_timeout) as response:
                    charset = response.headers.get_content_charset() or 'utf-8'
                    body = response.read().decode(charset, errors='ignore')
                break
            except HTTPError as exc:
                body = exc.read().decode('utf-8', errors='ignore')
                raise RuntimeError(f'MiniMax API 请求失败：{exc.code} {body}') from exc
            except (TimeoutError, socket.timeout) as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    raise RuntimeError(
                        f'MiniMax 响应超时，已重试 {self.max_retries} 次，请稍后重试或改用标准改写'
                    ) from exc
                time.sleep(2 * (attempt + 1))
            except URLError as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    raise RuntimeError(f'MiniMax API 请求失败：{exc.reason}') from exc
                time.sleep(2 * (attempt + 1))
        else:
            raise RuntimeError(f'MiniMax API 请求失败：{last_error}')

        result = json.loads(body)
        message = (((result.get('choices') or [{}])[0]).get('message') or {})
        if 'content' not in message:
            raise RuntimeError(f'MiniMax API 返回格式异常：{body[:300]}')
        message['content'] = clean_assistant_content(message.get('content') or '')
        return result

    def rewrite_article(self, content: str, prompts: Dict[str, str], original_title: str = '') -> Dict[str, Any]:
        extract_response = self.chat([
            {'role': 'system', 'content': '你是一个专业的技术编辑，请严格按要求提取信息。'},
            {'role': 'user', 'content': f"{prompts['extract']}\n\n{content}"},
        ])
        core_points = clean_assistant_content(extract_response['choices'][0]['message']['content'])

        rewrite_response = self.chat([
            {'role': 'system', 'content': '你是一个擅长技术写作的中文作者。'},
            {'role': 'user', 'content': f"{prompts['rewrite']}\n\n核心观点：\n{core_points}"},
        ], temperature=0.8)
        rewritten_content = clean_assistant_content(rewrite_response['choices'][0]['message']['content'])

        layout_response = self.chat([
            {'role': 'system', 'content': '你是一个技术博客排版编辑。'},
            {'role': 'user', 'content': f"{prompts['layout']}\n\n文章内容：\n{rewritten_content}"},
        ])
        final_content = clean_assistant_content(layout_response['choices'][0]['message']['content'])
        title = extract_markdown_title(final_content) or original_title or '未命名文章'
        final_content = replace_markdown_title(final_content, title)

        usage = (
            (extract_response.get('usage') or {}).get('total_tokens', 0) +
            (rewrite_response.get('usage') or {}).get('total_tokens', 0) +
            (layout_response.get('usage') or {}).get('total_tokens', 0)
        )
        return {
            'core_points': core_points,
            'title': title,
            'rewritten_content': final_content,
            'token_usage': usage,
        }


def process_rewrite_task(app, task_id: str, source_url: str, rewrite_strategy: str, template_type: str, auto_publish: bool):
    """Background job entrypoint."""
    with app.app_context():
        try:
            prompts = PROMPTS.get(rewrite_strategy) or PROMPTS['standard']
            api_key = app.config.get('MINIMAX_API_KEY')
            if not api_key:
                raise RuntimeError('未配置 MINIMAX_API_KEY')

            update_task(task_id, {
                'status': 'processing',
                'progress': 10,
                'message': '正在抓取微信公众号文章...',
            })
            scraped = scrape_wechat_article(source_url)

            update_task(task_id, {
                'progress': 30,
                'message': '抓取完成，正在整理原文...',
            })
            markdown_content = build_source_markdown(scraped)
            if not markdown_content.strip():
                raise RuntimeError('抓取到的正文为空')
            source_max_chars = int(app.config.get('AI_SOURCE_MAX_CHARS') or 12000)
            if len(markdown_content) > source_max_chars:
                markdown_content = markdown_content[:source_max_chars]

            update_task(task_id, {
                'progress': 55,
                'message': '正在调用 MiniMax 改写文章...',
            })
            client = MiniMaxClient(
                api_key=api_key,
                model=app.config.get('MINIMAX_MODEL'),
                base_url=app.config.get('MINIMAX_API_HOST'),
                request_timeout=app.config.get('MINIMAX_REQUEST_TIMEOUT', 300),
                max_retries=app.config.get('MINIMAX_MAX_RETRIES', 2),
            )
            result = client.rewrite_article(
                markdown_content,
                prompts,
                original_title=scraped.get('title') or '',
            )

            update_task(task_id, {
                'progress': 80,
                'message': 'AI 改写完成，正在保存文章...',
            })

            title = result['title']
            slug = build_unique_slug(title)
            article = Article(
                slug=slug,
                title=title,
                description=(scraped.get('description') or summarize_text(result['rewritten_content'], 180)),
                content=result['rewritten_content'],
                cover_image=scraped.get('cover_image'),
                source_url=source_url,
                ai_generated=1,
                ai_model=app.config.get('MINIMAX_MODEL') or 'MiniMax-M2.7',
                rewrite_strategy=rewrite_strategy,
                template_type=template_type,
                word_count=len(strip_html(result['rewritten_content'])),
                auto_published=1 if auto_publish else 0,
                status='published' if auto_publish else 'draft',
                published_at=datetime.utcnow() if auto_publish else None,
            )
            db.session.add(article)
            db.session.commit()

            update_task(task_id, {
                'status': 'completed',
                'progress': 100,
                'message': '改写完成',
                'article_id': article.id,
                'article_slug': article.slug,
                'token_usage': result['token_usage'],
                'cost': estimate_cost(result['token_usage']),
                'completed_at': datetime.utcnow(),
                'result': {
                    'article': {
                        'id': article.id,
                        'slug': article.slug,
                        'title': article.title,
                        'content': article.content or '',
                    },
                },
            })
        except Exception as exc:
            update_task(task_id, {
                'status': 'failed',
                'progress': get_task_progress(task_id),
                'message': '改写失败',
                'error': str(exc),
                'completed_at': datetime.utcnow(),
            })


def scrape_wechat_article(url: str) -> Dict[str, Any]:
    """Fetch and parse a WeChat public article."""
    if 'mp.weixin.qq.com' not in url:
        raise RuntimeError('仅支持微信公众号文章链接')

    html = fetch_wechat_html(url)
    content_html = extract_wechat_content_html(html)
    content_text = html_fragment_to_text(content_html) if content_html else extract_wechat_content_text(html)
    if not content_text.strip():
        if is_wechat_verification_page(html):
            raise RuntimeError('微信返回了安全验证页，服务端当前无法直接抓取这篇文章，请稍后重试')
        raise RuntimeError('无法提取文章正文，可能需要登录、文章已失效，或当前网络环境被微信限制')

    title = extract_regex_text(html, r'<h1[^>]*id=["\']activity-name["\'][^>]*>([\s\S]*?)</h1>')
    if not title:
        title = extract_regex_text(html, r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']')
    if not title:
        title = extract_regex_text(html, r'<title[^>]*>([\s\S]*?)</title>')

    author = extract_regex_text(html, r'<div[^>]*id=["\']js_author_name["\'][^>]*>([\s\S]*?)</div>')
    if not author:
        author = extract_regex_text(html, r'<meta[^>]+name=["\']author["\'][^>]+content=["\']([^"\']+)["\']')

    published_at = extract_regex_text(html, r'<div[^>]*id=["\']publish_time["\'][^>]*>([\s\S]*?)</div>')
    cover_image = extract_regex_text(html, r'<img[^>]+id=["\']js_cover["\'][^>]+src=["\']([^"\']+)["\']')
    if not cover_image:
        cover_image = extract_regex_text(html, r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']')

    description = extract_regex_text(html, r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']')
    if not description:
        description = summarize_text(content_text, 160)
    
    # 提取所有图片
    images = extract_images_from_html(content_html or html)

    return {
        'title': clean_text(title),
        'author': clean_text(author),
        'published_at': clean_text(published_at),
        'cover_image': cover_image,
        'description': clean_text(description),
        'content': content_html or content_text,
        'content_text': content_text,
        'source_url': url,
        'images': images,  # 添加图片列表
    }


def html_to_markdown(html: str) -> str:
    """Convert basic HTML blocks to Markdown."""
    markdown = html or ''
    
    # 首先提取所有图片并添加说明
    images = extract_images_from_html(html)
    if images:
        # 在文章开头添加图片说明章节
        img_section = "## 文章图片说明\n\n"
        img_section += "> 原文包含以下图片，改写时请保留这些图片或在相应位置使用 Mermaid 图表/文字描述替代\n\n"
        for i, img in enumerate(images, 1):
            img_section += f"![图片{i}: {img['alt'] or '无说明'}]({img['src']})\n"
            img_section += f"> 位置：{img['src'][:80]}...\n\n"
        img_section += "---\n\n"
        markdown = img_section + markdown
    
    replacements = [
        (r'<h1[^>]*>([\s\S]*?)</h1>', r'# \1\n\n'),
        (r'<h2[^>]*>([\s\S]*?)</h2>', r'## \1\n\n'),
        (r'<h3[^>]*>([\s\S]*?)</h3>', r'### \1\n\n'),
        (r'<h4[^>]*>([\s\S]*?)</h4>', r'#### \1\n\n'),
        (r'<p[^>]*>([\s\S]*?)</p>', r'\1\n\n'),
        (r'<strong[^>]*>([\s\S]*?)</strong>', r'**\1**'),
        (r'<b[^>]*>([\s\S]*?)</b>', r'**\1**'),
        (r'<em[^>]*>([\s\S]*?)</em>', r'*\1*'),
        (r'<i[^>]*>([\s\S]*?)</i>', r'*\1*'),
        (r'<code[^>]*>([\s\S]*?)</code>', r'`\1`'),
        (r'<blockquote[^>]*>([\s\S]*?)</blockquote>', r'> \1\n\n'),
        (r'<br\s*/?>', r'\n'),
        # 改进图片处理，保留 alt 文本
        (r'<img[^>]+src="([^"]+)"[^>]*alt="([^"]*)"[^>]*>', r'![\2](\1)\n'),
        (r'<img[^>]+alt="([^"]*)"[^>]+src="([^"]+)"[^>]*>', r'![\1](\2)\n'),
        (r'<img[^>]+src="([^"]+)"[^>]*>', r'![](图片地址：\1)\n'),
        (r'<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>', r'[\2](\1)'),
    ]
    for pattern, replacement in replacements:
        markdown = re.sub(pattern, replacement, markdown, flags=re.IGNORECASE)

    markdown = re.sub(
        r'<pre[^>]*><code[^>]*>([\s\S]*?)</code></pre>',
        lambda match: f"```\n{unescape(strip_html(match.group(1), keep_line_breaks=True)).strip()}\n```\n\n",
        markdown,
        flags=re.IGNORECASE,
    )
    markdown = re.sub(
        r'<ul[^>]*>([\s\S]*?)</ul>',
        lambda match: re.sub(r'<li[^>]*>([\s\S]*?)</li>', r'- \1\n', match.group(1), flags=re.IGNORECASE),
        markdown,
        flags=re.IGNORECASE,
    )
    markdown = re.sub(
        r'<ol[^>]*>([\s\S]*?)</ol>',
        _replace_ordered_list,
        markdown,
        flags=re.IGNORECASE,
    )
    markdown = strip_html(markdown, keep_line_breaks=True)
    markdown = re.sub(r'\n{3,}', '\n\n', unescape(markdown))
    return markdown.strip()


def build_unique_slug(title: str) -> str:
    """Build a unique slug for saved AI articles."""
    base = slugify(title) or 'ai-article'
    slug = f"{base}-{int(time.time())}"
    counter = 1
    while Article.query.filter_by(slug=slug).first():
        counter += 1
        slug = f"{base}-{int(time.time())}-{counter}"
    return slug


def estimate_cost(token_usage: int) -> float:
    """Rough token cost estimate for task display."""
    return round((token_usage or 0) * 0.0000012, 6)


def get_task_progress(task_id: str) -> int:
    from app.services.ai_tasks import get_task

    task = get_task(task_id) or {}
    try:
        return int(task.get('progress') or 0)
    except (TypeError, ValueError):
        return 0


def slugify(value: str) -> str:
    normalized = unicodedata.normalize('NFKD', value or '')
    ascii_value = normalized.encode('ascii', 'ignore').decode('ascii')
    ascii_value = re.sub(r'[^a-zA-Z0-9]+', '-', ascii_value.lower()).strip('-')
    return ascii_value[:80]


def summarize_text(value: str, limit: int = 200) -> str:
    text = clean_text(strip_html(value or ''))
    return text[:limit]


def clean_assistant_content(content: str) -> str:
    return (
        content
        .replace('\r\n', '\n')
        .replace('\r', '\n')
    )


def clean_title(title: str) -> str:
    return (
        clean_assistant_content(title)
        .split('\n')[0]
        .replace('标题：', '')
        .replace('标题:', '')
        .strip(' "#\'“”‘’《》【】')
        .strip()
    )[:80]


def extract_markdown_title(content: str) -> str:
    match = re.search(r'^\s*#\s+(.+)$', content or '', flags=re.MULTILINE)
    return clean_title(match.group(1)) if match else ''


def replace_markdown_title(content: str, title: str) -> str:
    if not title:
        return content
    if re.search(r'^\s*#\s+.+$', content or '', flags=re.MULTILINE):
        return re.sub(r'^\s*#\s+.+$', f'# {title}', content, count=1, flags=re.MULTILINE)
    return f'# {title}\n\n{content}'.strip()


def strip_html(value: str, keep_line_breaks: bool = False) -> str:
    if not value:
        return ''
    text = value
    if keep_line_breaks:
        text = re.sub(r'</(?:p|div|h[1-6]|li|blockquote|pre|ul|ol|table|tr)>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<script[\s\S]*?</script>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<style[\s\S]*?</style>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)
    return unescape(text)


def clean_text(value: str) -> str:
    return re.sub(r'\s+', ' ', (value or '')).strip()


def extract_text(*nodes) -> str:
    for node in nodes:
        if not node:
            continue
        if getattr(node, 'name', None) == 'meta':
            content = node.get('content')
            if content:
                return content
        text = node.get_text(' ', strip=True)
        if text:
            return text
    return ''


def extract_attr(node, attr_name: str) -> str:
    if not node:
        return ''
    value = node.get(attr_name)
    return value.strip() if isinstance(value, str) else ''


def extract_regex_text(html: str, pattern: str) -> str:
    match = re.search(pattern, html or '', flags=re.IGNORECASE)
    if not match:
        return ''
    return clean_text(strip_html(match.group(1)))


def fetch_wechat_html(url: str) -> str:
    last_verification_page = ''
    last_error = None
    for headers in WECHAT_REQUEST_HEADERS:
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=30) as response:
                charset = response.headers.get_content_charset() or 'utf-8'
                html = response.read().decode(charset, errors='ignore')
                final_url = response.geturl()
        except HTTPError as exc:
            raise RuntimeError(f'抓取失败：HTTP {exc.code}') from exc
        except URLError as exc:
            last_error = exc
            continue

        if is_wechat_article_page(html):
            return html
        if is_wechat_verification_page(html, final_url):
            last_verification_page = html
            continue
        if html.strip():
            return html

    if last_verification_page:
        raise RuntimeError('微信返回了安全验证页，服务端当前无法直接抓取这篇文章，请稍后重试')
    if last_error:
        raise RuntimeError(f'抓取失败：{last_error.reason}') from last_error
    raise RuntimeError('抓取失败：未获取到有效页面内容')


def is_wechat_article_page(html: str) -> bool:
    page = html or ''
    return (
        'id="js_content"' in page or
        "id='js_content'" in page or
        'content_noencode:' in page or
        'var msg_title =' in page
    )


def is_wechat_verification_page(html: str, final_url: str = '') -> bool:
    page = html or ''
    if 'wappoc_appmsgcaptcha' in (final_url or ''):
        return True
    if '完成验证后即可继续访问' in page:
        return True
    if '环境异常' in page and '去验证' in page:
        return True
    if 'secitptpage/verify' in page:
        return True
    return False


def extract_wechat_content_html(html: str) -> str:
    js_match = re.search(
        r"content_noencode\s*:\s*JsDecode\('((?:\\.|[^'\\])*)'\)",
        html or '',
        flags=re.IGNORECASE,
    )
    if js_match:
        decoded = clean_wechat_content_html(decode_js_string(js_match.group(1)))
        if looks_like_html(decoded):
            return decoded

    parser = WeChatElementHTMLParser('div', 'js_content')
    parser.feed(html or '')
    parser.close()
    return clean_wechat_content_html(parser.html())


def extract_wechat_content_text(html: str) -> str:
    parser = WeChatContentParser()
    parser.feed(html or '')
    parser.close()
    return parser.text()


def build_source_markdown(scraped: Dict[str, Any]) -> str:
    raw_content = (scraped.get('content') or '').strip()
    if looks_like_html(raw_content):
        body = html_to_markdown(raw_content)
    else:
        body = normalize_source_text(raw_content)

    title = clean_title(scraped.get('title') or '')
    meta_parts = []
    if scraped.get('author'):
        meta_parts.append(f"作者：{scraped['author']}")
    if scraped.get('published_at'):
        meta_parts.append(f"发布时间：{scraped['published_at']}")

    sections = []
    if title:
        sections.append(f"# {title}")
    if meta_parts:
        sections.append(' | '.join(meta_parts))
    
    # 添加图片信息
    images = scraped.get('images', [])
    if images:
        img_section = "\n## 原文图片\n\n"
        for i, img in enumerate(images, 1):
            img_section += f"**图片{i}**: {img['alt'] or '无说明'}\n"
            img_section += f"![{img['alt'] or '图片'}]({img['src']})\n\n"
        sections.append(img_section)
    
    if body:
        sections.append(body)
    return '\n\n'.join(section for section in sections if section).strip()


def clean_wechat_content_html(value: str) -> str:
    content = value or ''
    content = re.sub(r'<!--[\s\S]*?-->', '', content)
    content = re.sub(r'<script[\s\S]*?</script>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<style[\s\S]*?</style>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<(?:mp-style-type|mp-common-profile)[^>]*>[\s\S]*?</(?:mp-style-type|mp-common-profile)>', '', content, flags=re.IGNORECASE)
    content = re.sub(r'<p[^>]*display\s*:\s*none[^>]*>[\s\S]*?</p>', '', content, flags=re.IGNORECASE)
    return content.strip()


def decode_js_string(value: str) -> str:
    result = value or ''
    result = re.sub(r'\\x([0-9a-fA-F]{2})', lambda match: chr(int(match.group(1), 16)), result)
    result = re.sub(r'\\u([0-9a-fA-F]{4})', lambda match: chr(int(match.group(1), 16)), result)
    replacements = {
        r"\/": '/',
        r"\'": "'",
        r'\"': '"',
        r'\n': '\n',
        r'\r': '\r',
        r'\t': '\t',
        r'\b': '\b',
        r'\f': '\f',
        r'\\': '\\',
    }
    for pattern, replacement in replacements.items():
        result = result.replace(pattern, replacement)
    return result


def html_fragment_to_text(value: str) -> str:
    return normalize_source_text(strip_html(value or '', keep_line_breaks=True))


def normalize_source_text(value: str) -> str:
    text = unescape(value or '')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()


def looks_like_html(value: str) -> bool:
    return bool(re.search(r'<[a-zA-Z][^>]*>', value or ''))


class WeChatContentParser(HTMLParser):
    VOID_TAGS = {
        'br', 'hr', 'img', 'input', 'meta', 'link', 'source', 'area', 'base',
        'col', 'embed', 'param', 'track', 'wbr'
    }
    BLOCK_TAGS = {
        'p', 'div', 'section', 'article', 'aside', 'header', 'footer', 'nav',
        'li', 'blockquote', 'pre', 'figure', 'figcaption', 'table', 'tr', 'td',
        'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    }

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self._capture = False
        self._depth = 0
        self._parts = []

    def handle_starttag(self, tag, attrs):
        attr_map = dict(attrs)
        class_name = attr_map.get('class', '')
        if not self._capture and tag == 'div':
            if attr_map.get('id') == 'js_content' or 'rich_media_content' in class_name.split():
                self._capture = True
                self._depth = 1
                return

        if self._capture:
            if tag == 'br' or tag in self.BLOCK_TAGS:
                self._parts.append('\n')
            if tag not in self.VOID_TAGS:
                self._depth += 1

    def handle_endtag(self, tag):
        if not self._capture:
            return

        if tag in self.BLOCK_TAGS:
            self._parts.append('\n')

        if tag not in self.VOID_TAGS:
            self._depth -= 1
            if self._depth <= 0:
                self._capture = False

    def handle_data(self, data):
        if self._capture:
            self._parts.append(data)

    def text(self) -> str:
        text = unescape(''.join(self._parts))
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()


class WeChatElementHTMLParser(HTMLParser):
    VOID_TAGS = WeChatContentParser.VOID_TAGS

    def __init__(self, target_tag: str, target_id: str):
        super().__init__(convert_charrefs=False)
        self.target_tag = target_tag
        self.target_id = target_id
        self._capture = False
        self._depth = 0
        self._parts = []

    def handle_starttag(self, tag, attrs):
        attr_map = dict(attrs)
        if not self._capture and tag == self.target_tag and attr_map.get('id') == self.target_id:
            self._capture = True
            self._depth = 1
            return
        if not self._capture:
            return
        self._parts.append(self.get_starttag_text())
        if tag not in self.VOID_TAGS:
            self._depth += 1

    def handle_startendtag(self, tag, attrs):
        if self._capture:
            self._parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if not self._capture:
            return
        if tag not in self.VOID_TAGS:
            self._depth -= 1
            if self._depth <= 0:
                self._capture = False
                return
        self._parts.append(f'</{tag}>')

    def handle_data(self, data):
        if self._capture:
            self._parts.append(data)

    def handle_entityref(self, name):
        if self._capture:
            self._parts.append(f'&{name};')

    def handle_charref(self, name):
        if self._capture:
            self._parts.append(f'&#{name};')

    def handle_comment(self, data):
        if self._capture:
            self._parts.append(f'<!--{data}-->')

    def html(self) -> str:
        return ''.join(self._parts).strip()


def _replace_ordered_list(match) -> str:
    index = 0

    def repl(item_match):
        nonlocal index
        index += 1
        return f'{index}. {item_match.group(1)}\n'

    return re.sub(r'<li[^>]*>([\s\S]*?)</li>', repl, match.group(1), flags=re.IGNORECASE)
