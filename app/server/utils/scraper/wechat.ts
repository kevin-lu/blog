// app/server/utils/scraper/wechat.ts

import * as cheerio from 'cheerio';

export interface ScrapedArticle {
  title: string;
  content: string;
  author?: string;
  publishedAt?: string;
  coverImage?: string;
  sourceUrl: string;
  description?: string;
}

export async function scrapeWechatArticle(url: string): Promise<ScrapedArticle> {
  try {
    // 检查 URL 是否有效
    if (!url.includes('mp.weixin.qq.com')) {
      throw new Error('仅支持微信公众号文章链接');
    }

    // 获取文章内容
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      },
    });

    if (!response.ok) {
      throw new Error(`获取文章失败：${response.status}`);
    }

    const html = await response.text();
    const $ = cheerio.load(html);

    // 提取标题
    const title = $('#activity-name').text().trim() || $('title').text().trim();

    // 提取作者
    const author = $('#js_author_name').text().trim() || 
                   $('meta[name="author"]').attr('content') || '';

    // 提取发布时间
    const publishedAt = $('#publish_time').text().trim() || '';

    // 提取封面图
    const coverImage = $('img#js_cover').attr('src') || 
                       $('meta[property="og:image"]').attr('content') || '';

    // 提取正文内容
    const content = $('#js_content').html() || 
                    $('.rich_media_content').html() || '';

    // 提取描述
    const description = $('meta[name="description"]').attr('content') || '';

    if (!content) {
      throw new Error('无法提取文章内容，可能是文章需要权限访问');
    }

    return {
      title,
      content,
      author,
      publishedAt,
      coverImage,
      sourceUrl: url,
      description,
    };
  } catch (error: any) {
    console.error('抓取微信文章失败:', error.message);
    throw new Error(`抓取失败：${error.message}`);
  }
}
