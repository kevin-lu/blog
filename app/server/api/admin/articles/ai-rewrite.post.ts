// app/server/api/admin/articles/ai-rewrite.post.ts

import { defineEventHandler, readBody } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { MiniMaxAI } from '~/server/utils/ai/minimax';
import { getPrompts } from '~/server/utils/ai/prompts';
import { scrapeWechatArticle } from '~/server/utils/scraper/wechat';
import { htmlToMarkdown } from '~/server/utils/scraper/html-parser';
import { createAITask, updateAITask } from '~/server/stores/ai-tasks';
import { slugify } from '~/server/utils/slugify';

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event);
    const {
      sourceUrl,
      rewriteStrategy = 'standard',
      templateType = 'tutorial',
      autoPublish = false,
    } = body;

    if (!sourceUrl) {
      return {
        success: false,
        message: '请提供文章链接',
      };
    }

    // 创建任务记录
    const task = createAITask({
      status: 'processing',
      sourceUrl,
      rewriteStrategy,
      templateType,
      autoPublish,
    });

    // 异步执行 AI 改写
    processAIRewrite(task.id, sourceUrl, rewriteStrategy, templateType, autoPublish)
      .catch((error) => {
        console.error('AI 改写失败:', error);
        updateAITask(task.id, {
          status: 'failed',
          error: error.message,
          completedAt: new Date(),
        });
      });

    return {
      success: true,
      data: {
        taskId: task.id,
        status: 'processing',
        estimatedTime: '2-3 分钟',
      },
    };
  } catch (error: any) {
    console.error('AI 改写请求失败:', error);
    return {
      success: false,
      message: error.message || 'AI 改写失败',
    };
  }
});

async function processAIRewrite(
  taskId: string,
  sourceUrl: string,
  rewriteStrategy: string,
  templateType: string,
  autoPublish: boolean
) {
  try {
    // 步骤 1: 抓取文章
    updateAITask(taskId, { 
      status: 'processing',
      progress: 10,
      message: '正在抓取文章内容...',
    });
    const scraped = await scrapeWechatArticle(sourceUrl);
    
    updateAITask(taskId, { 
      progress: 30,
      message: '文章内容抓取成功，正在转换格式...',
    });

    // 步骤 2: 转换为 Markdown
    const markdownContent = htmlToMarkdown(scraped.content);
    
    updateAITask(taskId, { 
      progress: 50,
      message: '正在调用 AI 改写...',
    });

    // 步骤 3: 调用 AI 改写
    const apiKey = process.env.MINIMAX_API_KEY;
    if (!apiKey) {
      throw new Error('未配置 MINIMAX_API_KEY 环境变量');
    }

    const ai = new MiniMaxAI({ apiKey });
    const promptsData = getPrompts(rewriteStrategy as any);
    const prompts = {
      extractPrompt: promptsData.extract,
      rewritePrompt: promptsData.rewrite,
      layoutPrompt: promptsData.layout,
    };
    
    updateAITask(taskId, { 
      progress: 60,
      message: 'AI 正在分析文章结构...',
    });
    
    const result = await ai.rewriteArticle(markdownContent, prompts);
    
    updateAITask(taskId, { 
      progress: 80,
      message: '正在保存文章...',
    });

    // 步骤 4: 保存文章
    const slug = slugify(scraped.title) + '-' + Date.now();
    const article = await db.insert(articleMeta).values({
      slug,
      title: scraped.title,
      description: scraped.description?.substring(0, 200) || '',
      content: result.rewrittenContent,
      status: autoPublish ? 'published' : 'draft',
      sourceUrl,
      aiGenerated: 1,
      aiModel: 'MiniMax-M2.7',
      rewriteStrategy,
      templateType,
      wordCount: result.rewrittenContent.length,
      autoPublished: autoPublish ? 1 : 0,
      publishedAt: autoPublish ? new Date() : null,
      createdAt: new Date(),
      updatedAt: new Date(),
    }).returning();

    // 更新任务状态
    updateAITask(taskId, {
      status: 'completed',
      progress: 100,
      message: '任务完成',
      articleId: article[0].id,
      articleSlug: slug,
      tokenUsage: result.tokenUsage,
      cost: result.tokenUsage * 0.0000012, // MiniMax 输出价格
      completedAt: new Date(),
    });

  } catch (error: any) {
    console.error('AI 改写失败:', error);
    updateAITask(taskId, {
      status: 'failed',
      progress: 0,
      error: error.message || '未知错误',
      message: `执行失败：${error.message}`,
      completedAt: new Date(),
    });
    throw error;
  }
}
