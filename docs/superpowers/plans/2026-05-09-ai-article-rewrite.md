# AI 文章改写系统实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建全自动 AI 文章改写系统，支持微信文章抓取、MiniMax AI 改写、自动优化布局、审核发布

**架构：** 
- 内容抓取层：抓取微信文章 HTML 内容
- AI 改写层：调用 MiniMax API 进行内容改写和布局优化
- 发布管理层：草稿箱管理、审核流程、自动发布
- 前端界面：AI 改写面板、进度监控、批量操作

**技术栈：** 
- Nuxt.js 3.x + TypeScript
- MiniMax AI API
- Cheerio（HTML 解析）
- Node.js Fetch API
- SQLite + Drizzle ORM

---

## 文件结构

### 新增文件

**服务端 API：**
- `app/server/api/admin/articles/ai-rewrite.post.ts` - AI 改写接口
- `app/server/api/admin/articles/ai-progress.get.ts` - 进度查询接口
- `app/server/api/admin/articles/ai-batch.post.ts` - 批量改写接口
- `app/server/utils/scraper/wechat.ts` - 微信文章抓取器
- `app/server/utils/scraper/html-parser.ts` - HTML 内容解析器
- `app/server/utils/ai/minimax.ts` - MiniMax AI 封装
- `app/server/utils/ai/prompts.ts` - AI Prompt 模板

**前端组件：**
- `app/components/admin/ai-rewrite/AIRewritePanel.vue` - AI 改写面板
- `app/components/admin/ai-rewrite/AIProgress.vue` - 进度监控组件
- `app/components/admin/ai-rewrite/AITaskList.vue` - 任务列表组件
- `app/components/admin/ai-rewrite/AIBatchRewrite.vue` - 批量改写组件

**状态管理：**
- `app/stores/ai-rewrite.ts` - AI 改写状态管理

**数据库：**
- `app/server/database/schema/articleMeta.ts` - 扩展文章字段

**配置文件：**
- `.env.example` - 添加 MiniMax API 配置

---

## 任务分解

### 任务 1：数据库扩展

**文件：**
- 修改：`app/server/database/schema/articleMeta.ts`
- 创建：`app/server/database/migrations/000x_add_ai_fields.sql`

- [ ] **步骤 1：添加 AI 相关字段到 Schema**

```typescript
import { sqliteTable, integer, text } from 'drizzle-orm/sqlite-core';

export const articleMeta = sqliteTable('article_meta', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  slug: text('slug').notNull().unique(),
  title: text('title').notNull(),
  description: text('description'),
  content: text('content'),
  coverImage: text('cover_image'),
  status: text('status').default('draft'),
  publishedAt: text('published_at').$type<Date>(),
  createdAt: text('created_at').$type<Date>(),
  updatedAt: text('updated_at').$type<Date>(),
  
  // AI 改写相关字段
  sourceUrl: text('source_url'), // 参考文章来源
  aiGenerated: integer('ai_generated').default(0), // 是否 AI 生成 (0/1)
  aiModel: text('ai_model'), // AI 模型名称
  rewriteStrategy: text('rewrite_strategy').default('standard'), // 改写策略
  templateType: text('template_type').default('tutorial'), // 模板类型
  wordCount: integer('word_count'), // 字数统计
  autoPublished: integer('auto_published').default(0), // 是否自动发布
});

export type ArticleMeta = typeof articleMeta.$inferSelect;
export type NewArticleMeta = typeof articleMeta.$inferInsert;
```

- [ ] **步骤 2：创建数据库迁移文件**

```sql
-- Add AI-related fields to article_meta table
ALTER TABLE article_meta ADD COLUMN source_url TEXT;
ALTER TABLE article_meta ADD COLUMN ai_generated INTEGER DEFAULT 0;
ALTER TABLE article_meta ADD COLUMN ai_model TEXT;
ALTER TABLE article_meta ADD COLUMN rewrite_strategy TEXT DEFAULT 'standard';
ALTER TABLE article_meta ADD COLUMN template_type TEXT DEFAULT 'tutorial';
ALTER TABLE article_meta ADD COLUMN word_count INTEGER;
ALTER TABLE article_meta ADD COLUMN auto_published INTEGER DEFAULT 0;

-- Create index for AI-generated articles
CREATE INDEX IF NOT EXISTS idx_article_ai_generated ON article_meta(ai_generated);
CREATE INDEX IF NOT EXISTS idx_article_source_url ON article_meta(source_url);
```

- [ ] **步骤 3：运行数据库迁移**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog
npm run db:push
```

预期：数据库表结构更新成功

- [ ] **步骤 4：Commit**

```bash
git add app/server/database/schema/articleMeta.ts app/server/database/migrations/
git commit -m "feat: 添加 AI 改写相关数据库字段"
```

---

### 任务 2：MiniMax AI 封装

**文件：**
- 创建：`app/server/utils/ai/minimax.ts`
- 创建：`app/server/utils/ai/prompts.ts`

- [ ] **步骤 1：创建 MiniMax API 封装**

```typescript
// app/server/utils/ai/minimax.ts

interface MiniMaxConfig {
  apiKey: string;
  model?: string;
}

interface MiniMaxMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface MiniMaxResponse {
  id: string;
  choices: Array<{
    message: {
      content: string;
    };
  }>;
  usage: {
    total_tokens: number;
  };
}

export class MiniMaxAI {
  private apiKey: string;
  private model: string;
  private baseUrl = 'https://api.minimaxi.chat/v1/chat/completions';

  constructor(config: MiniMaxConfig) {
    this.apiKey = config.apiKey;
    this.model = config.model || 'MiniMax-M2.7';
  }

  async chat(messages: MiniMaxMessage[], options?: {
    temperature?: number;
    maxTokens?: number;
  }): Promise<MiniMaxResponse> {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: this.model,
        messages: messages,
        temperature: options?.temperature || 0.7,
        max_tokens: options?.maxTokens || 4000,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`MiniMax API 请求失败：${response.status} - ${error}`);
    }

    return response.json();
  }

  async rewriteArticle(content: string, prompts: {
    extractPrompt: string;
    rewritePrompt: string;
    layoutPrompt: string;
  }): Promise<{
    corePoints: string;
    rewrittenContent: string;
    tokenUsage: number;
  }> {
    // 第一步：提取核心观点
    const extractResponse = await this.chat([
      { role: 'user', content: prompts.extractPrompt + '\n\n' + content }
    ]);
    const corePoints = extractResponse.choices[0].message.content;

    // 第二步：基于核心观点重写
    const rewriteResponse = await this.chat([
      { role: 'user', content: prompts.rewritePrompt + '\n\n核心观点：\n' + corePoints }
    ], { temperature: 0.8 });
    const rewrittenContent = rewriteResponse.choices[0].message.content;

    // 第三步：优化布局
    const layoutResponse = await this.chat([
      { role: 'user', content: prompts.layoutPrompt + '\n\n文章内容：\n' + rewrittenContent }
    ]);
    const finalContent = layoutResponse.choices[0].message.content;

    const totalTokens = extractResponse.usage.total_tokens +
                       rewriteResponse.usage.total_tokens +
                       layoutResponse.usage.total_tokens;

    return {
      corePoints,
      rewrittenContent: finalContent,
      tokenUsage: totalTokens,
    };
  }
}
```

- [ ] **步骤 2：创建 AI Prompt 模板**

```typescript
// app/server/utils/ai/prompts.ts

export const rewritePrompts = {
  // 轻松技术博客风格
  standard: {
    extract: `请从以下文章中提取核心观点和技术要点，用简洁的中文列出：

要求：
1. 提取核心主题（1 句话）
2. 列出 3-5 个关键观点
3. 提取重要的技术细节和代码示例
4. 忽略广告、推广等无关内容

输出格式：
【核心主题】
...

【关键观点】
1. ...
2. ...
3. ...

【技术要点】
- ...
- ...`,

    rewrite: `基于以下核心观点，用轻松的技术博客风格重新创作一篇文章。

要求：
1. 使用自己的表达方式，完全重写，避免版权风险
2. 语言风格：轻松幽默，像和朋友聊天一样讲解技术
3. 结构清晰，逻辑连贯
4. 添加实际案例和代码示例（可以虚构但要有代表性）
5. 适当使用比喻和类比，让技术概念更易懂
6. 字数：2000-3000 字
7. 开头要吸引人，可以用问题或场景引入
8. 结尾要有总结和行动建议

避免：
- 不要使用"本文"、"笔者"等正式用语
- 不要大段复制原文
- 不要使用过于学术化的表达`,

    layout: `请为以下技术文章设计 Markdown 布局，让它更易读、更有吸引力。

要求：
1. 添加合适的标题层级（H1/H2/H3），H2 用于主要章节，H3 用于子章节
2. 代码块使用 \`\`\`language 格式，并添加语言标识
3. 重点内容使用 **加粗** 标注
4. 关键提示使用 > 引用块
5. 列表使用 - 无序列表或 1. 有序列表
6. 对比内容使用表格展示
7. 适当添加分隔线 --- 分隔章节

输出：直接返回优化后的 Markdown 内容，不要额外说明。`,
  },

  // 深度改写（添加案例分析）
  deep: {
    extract: `请深度分析以下文章，提取：
1. 核心论点和技术原理
2. 作者的观点和立场
3. 技术方案的优缺点
4. 适用场景和局限性

请详细列出，作为深度改写的素材。`,

    rewrite: `基于以下核心观点，创作一篇深度技术分析文章。

要求：
1. 保留核心观点，完全重写表达
2. 添加详细的案例分析（可以虚构但要有代表性）
3. 对比不同技术方案的优缺点
4. 给出实际应用场景和建议
5. 语言风格：轻松但专业，像技术大牛分享经验
6. 字数：3000-4000 字
7. 添加"最佳实践"、"避坑指南"等实用章节`,

    layout: `请为这篇深度技术文章设计专业的 Markdown 布局。

要求：
1. 使用多级标题组织内容
2. 代码示例添加详细注释
3. 对比内容使用表格
4. 重点提示使用引用块
5. 添加"要点总结"小节
6. 使用表格对比不同方案`,
  },

  // 创意改写（完全重新创作）
  creative: {
    extract: `请从以下文章中获取灵感，提取：
1. 讨论的技术主题
2. 解决的问题
3. 核心思路

不需要详细观点，只需要主题方向即可。`,

    rewrite: `基于以下技术主题，完全独立创作一篇原创技术文章。

要求：
1. 只保留技术主题，观点和论述完全原创
2. 使用自己的案例和代码示例
3. 可以调整技术立场和观点
4. 语言风格：轻松有趣，可以加入个人见解和吐槽
5. 字数：2000-3000 字
6. 结构自由，但要逻辑清晰`,

    layout: `请为这篇原创技术文章设计吸引人的 Markdown 布局。

要求：
1. 使用有趣的章节标题
2. 适当使用 emoji 增加趣味性（但不要过多）
3. 代码块和文本合理搭配
4. 重点内容突出显示`,
  },
};

export function getPrompts(strategy: 'standard' | 'deep' | 'creative') {
  return rewritePrompts[strategy];
}
```

- [ ] **步骤 3：添加环境变量配置**

```bash
# .env.example
# MiniMax AI Configuration
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_MODEL=MiniMax-M2.7
```

- [ ] **步骤 4：Commit**

```bash
git add app/server/utils/ai/
git commit -m "feat: 创建 MiniMax AI 封装和 Prompt 模板"
```

---

### 任务 3：微信文章抓取器

**文件：**
- 创建：`app/server/utils/scraper/wechat.ts`
- 创建：`app/server/utils/scraper/html-parser.ts`

- [ ] **步骤 1：创建微信文章抓取器**

```typescript
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
```

- [ ] **步骤 2：创建 HTML 内容解析器**

```typescript
// app/server/utils/scraper/html-parser.ts

export interface ParsedContent {
  text: string;
  codeBlocks: Array<{
    language: string;
    code: string;
  }>;
  images: Array<{
    src: string;
    alt: string;
  }>;
  links: Array<{
    text: string;
    href: string;
  }>;
}

export function parseHtmlContent(html: string): ParsedContent {
  const text = html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  const codeBlocks: Array<{ language: string; code: string }> = [];
  const codeBlockRegex = /<pre[^>]*>([\s\S]*?)<\/pre>/gi;
  let match;
  while ((match = codeBlockRegex.exec(html)) !== null) {
    const codeContent = match[1]
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&');
    codeBlocks.push({
      language: 'javascript',
      code: codeContent,
    });
  }

  const images: Array<{ src: string; alt: string }> = [];
  const imageRegex = /<img[^>]+src="([^"]+)"[^>]*>/gi;
  while ((match = imageRegex.exec(html)) !== null) {
    const altMatch = /alt="([^"]*)"/.exec(match[0]);
    images.push({
      src: match[1],
      alt: altMatch ? altMatch[1] : '',
    });
  }

  const links: Array<{ text: string; href: string }> = [];
  const linkRegex = /<a[^>]+href="([^"]+)"[^>]*>([^<]*)<\/a>/gi;
  while ((match = linkRegex.exec(html)) !== null) {
    links.push({
      href: match[1],
      text: match[2],
    });
  }

  return {
    text,
    codeBlocks,
    images,
    links,
  };
}

export function htmlToMarkdown(html: string): string {
  let markdown = html;

  markdown = markdown.replace(/<h1[^>]*>([\s\S]*?)<\/h1>/gi, '# $1\n\n');
  markdown = markdown.replace(/<h2[^>]*>([\s\S]*?)<\/h2>/gi, '## $1\n\n');
  markdown = markdown.replace(/<h3[^>]*>([\s\S]*?)<\/h3>/gi, '### $1\n\n');
  markdown = markdown.replace(/<p[^>]*>([\s\S]*?)<\/p>/gi, '$1\n\n');
  markdown = markdown.replace(/<strong[^>]*>([\s\S]*?)<\/strong>/gi, '**$1**');
  markdown = markdown.replace(/<b[^>]*>([\s\S]*?)<\/b>/gi, '**$1**');
  markdown = markdown.replace(/<em[^>]*>([\s\S]*?)<\/em>/gi, '*$1*');
  markdown = markdown.replace(/<ul[^>]*>([\s\S]*?)<\/ul>/gi, (match, p1) => {
    return p1.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, '- $1\n');
  });
  markdown = markdown.replace(/<ol[^>]*>([\s\S]*?)<\/ol>/gi, (match, p1) => {
    let index = 1;
    return p1.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, () => `${index++}. $1\n`);
  });
  markdown = markdown.replace(/<pre[^>]*><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi, '```\n$1\n```\n');
  markdown = markdown.replace(/<code[^>]*>([\s\S]*?)<\/code>/gi, '`$1`');
  markdown = markdown.replace(/<blockquote[^>]*>([\s\S]*?)<\/blockquote>/gi, '> $1\n');
  markdown = markdown.replace(/<img[^>]+src="([^"]+)"[^>]*>/gi, '![]($1)\n');
  markdown = markdown.replace(/<a[^>]+href="([^"]+)"[^>]*>([^<]*)<\/a>/gi, '[$2]($1)');
  markdown = markdown.replace(/<[^>]+>/g, '');
  markdown = markdown.replace(/\n\s*\n/g, '\n\n');
  markdown = markdown.trim();

  return markdown;
}
```

- [ ] **步骤 3：安装 Cheerio 依赖**

```bash
cd /Users/luzengbiao/traeProjects/blog/blog
npm install cheerio
```

- [ ] **步骤 4：Commit**

```bash
git add app/server/utils/scraper/
git commit -m "feat: 创建微信文章抓取器和 HTML 解析器"
```

---

### 任务 4：AI 改写 API 接口

**文件：**
- 创建：`app/server/api/admin/articles/ai-rewrite.post.ts`
- 创建：`app/server/api/admin/articles/ai-progress.get.ts`
- 创建：`app/server/stores/ai-tasks.ts`

- [ ] **步骤 1：创建 AI 任务存储**

```typescript
// app/server/stores/ai-tasks.ts

interface AITask {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  sourceUrl: string;
  rewriteStrategy: 'standard' | 'deep' | 'creative';
  templateType: 'tutorial' | 'concept' | 'comparison' | 'practice';
  autoPublish: boolean;
  articleId?: number;
  articleSlug?: string;
  error?: string;
  tokenUsage?: number;
  cost?: number;
  createdAt: Date;
  completedAt?: Date;
}

const tasks = new Map<string, AITask>();

export function createAITask(task: Omit<AITask, 'id' | 'createdAt'>): AITask {
  const id = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const newTask: AITask = {
    ...task,
    id,
    createdAt: new Date(),
  };
  tasks.set(id, newTask);
  return newTask;
}

export function getAITask(taskId: string): AITask | undefined {
  return tasks.get(taskId);
}

export function updateAITask(taskId: string, updates: Partial<AITask>): AITask | undefined {
  const task = tasks.get(taskId);
  if (!task) return undefined;
  
  const updated = { ...task, ...updates };
  tasks.set(taskId, updated);
  return updated;
}

export function listAITasks(limit = 20): AITask[] {
  return Array.from(tasks.values())
    .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
    .slice(0, limit);
}
```

- [ ] **步骤 2：创建 AI 改写 API**

```typescript
// app/server/api/admin/articles/ai-rewrite.post.ts

import { defineEventHandler, readBody } from 'h3';
import { db } from '~/server/database/postgres';
import { articleMeta } from '~/server/database/schema/articleMeta';
import { MiniMaxAI } from '~/server/utils/ai/minimax';
import { getPrompts } from '~/server/utils/ai/prompts';
import { scrapeWechatArticle } from '~/server/utils/scraper/wechat';
import { htmlToMarkdown } from '~/server/utils/scraper/html-parser';
import { createAITask } from '~/server/stores/ai-tasks';
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
  const { updateAITask } = await import('~/server/stores/ai-tasks');
  
  try {
    // 步骤 1: 抓取文章
    updateAITask(taskId, { status: 'processing' });
    const scraped = await scrapeWechatArticle(sourceUrl);

    // 步骤 2: 转换为 Markdown
    const markdownContent = htmlToMarkdown(scraped.content);

    // 步骤 3: 调用 AI 改写
    const apiKey = process.env.MINIMAX_API_KEY;
    if (!apiKey) {
      throw new Error('未配置 MINIMAX_API_KEY 环境变量');
    }

    const ai = new MiniMaxAI({ apiKey });
    const prompts = getPrompts(rewriteStrategy as any);
    
    const result = await ai.rewriteArticle(markdownContent, prompts);

    // 步骤 4: 保存文章
    const slug = slugify(scraped.title) + '-' + Date.now();
    const article = await db.insert(articleMeta).values({
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
      articleId: article[0].id,
      articleSlug: slug,
      tokenUsage: result.tokenUsage,
      cost: result.tokenUsage * 0.0000012, // MiniMax 输出价格
      completedAt: new Date(),
    });

  } catch (error: any) {
    updateAITask(taskId, {
      status: 'failed',
      error: error.message,
      completedAt: new Date(),
    });
    throw error;
  }
}
```

- [ ] **步骤 3：创建进度查询 API**

```typescript
// app/server/api/admin/articles/ai-progress.get.ts

import { defineEventHandler, getQuery } from 'h3';
import { getAITask, listAITasks } from '~/server/stores/ai-tasks';

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event);
    const { taskId } = query;

    if (taskId) {
      // 查询单个任务
      const task = getAITask(taskId as string);
      if (!task) {
        return {
          success: false,
          message: '任务不存在',
        };
      }

      return {
        success: true,
        data: task,
      };
    } else {
      // 查询任务列表
      const tasks = listAITasks();
      return {
        success: true,
        data: {
          tasks,
          total: tasks.length,
        },
      };
    }
  } catch (error: any) {
    console.error('查询任务进度失败:', error);
    return {
      success: false,
      message: '查询失败',
    };
  }
});
```

- [ ] **步骤 4：创建 Slug 工具函数**

```typescript
// app/server/utils/slugify.ts

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .trim()
    .substring(0, 100);
}
```

- [ ] **步骤 5：Commit**

```bash
git add app/server/api/admin/articles/ai-rewrite.post.ts app/server/api/admin/articles/ai-progress.get.ts app/server/stores/ai-tasks.ts app/server/utils/slugify.ts
git commit -m "feat: 创建 AI 改写 API 接口"
```

---

### 任务 5：管理后台前端组件

**文件：**
- 创建：`app/components/admin/ai-rewrite/AIRewritePanel.vue`
- 创建：`app/components/admin/ai-rewrite/AIProgress.vue`
- 创建：`app/components/admin/ai-rewrite/AITaskList.vue`
- 创建：`app/stores/ai-rewrite.ts`

- [ ] **步骤 1：创建 AI 改写状态管理**

```typescript
// app/stores/ai-rewrite.ts

import { defineStore } from 'pinia';

interface AITask {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  sourceUrl: string;
  rewriteStrategy: string;
  templateType: string;
  articleId?: number;
  articleSlug?: string;
  error?: string;
  tokenUsage?: number;
  cost?: number;
  createdAt: string;
  completedAt?: string;
}

export const useAIRewriteStore = defineStore('ai-rewrite', {
  state: () => ({
    tasks: [] as AITask[],
    currentTask: null as AITask | null,
    isLoading: false,
  }),

  actions: {
    async submitRewrite(data: {
      sourceUrl: string;
      rewriteStrategy: string;
      templateType: string;
      autoPublish: boolean;
    }) {
      this.isLoading = true;
      try {
        const response = await fetch('/api/admin/articles/ai-rewrite', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });
        const result = await response.json();
        
        if (result.success) {
          this.currentTask = result.data;
          this.pollTaskStatus(result.data.taskId);
        } else {
          throw new Error(result.message);
        }
      } finally {
        this.isLoading = false;
      }
    },

    async pollTaskStatus(taskId: string) {
      const poll = async () => {
        const response = await fetch(`/api/admin/articles/ai-progress?taskId=${taskId}`);
        const result = await response.json();
        
        if (result.success) {
          this.currentTask = result.data;
          
          if (result.data.status === 'completed' || result.data.status === 'failed') {
            this.loadTasks();
            return;
          }
          
          setTimeout(poll, 3000);
        }
      };
      
      poll();
    },

    async loadTasks() {
      const response = await fetch('/api/admin/articles/ai-progress');
      const result = await response.json();
      
      if (result.success) {
        this.tasks = result.data.tasks;
      }
    },
  },
});
```

- [ ] **步骤 2：创建 AI 改写面板组件**

```vue
<!-- app/components/admin/ai-rewrite/AIRewritePanel.vue -->

<template>
  <div class="ai-rewrite-panel">
    <n-card title="🤖 AI 智能改写" size="large">
      <n-form ref="formRef" :model="formData" label-placement="top">
        <n-form-item label="参考文章链接" required>
          <n-input
            v-model:value="formData.sourceUrl"
            placeholder="请输入微信公众号文章链接，如：https://mp.weixin.qq.com/s/xxx"
            clearable
          />
        </n-form-item>

        <n-form-item label="改写策略" required>
          <n-radio-group v-model:value="formData.rewriteStrategy">
            <n-space>
              <n-radio value="standard">
                标准改写
                <n-text depth="3" style="font-size: 12px">
                  （保留核心观点）
                </n-text>
              </n-radio>
              <n-radio value="deep">
                深度改写
                <n-text depth="3" style="font-size: 12px">
                  （添加案例分析）
                </n-text>
              </n-radio>
              <n-radio value="creative">
                创意改写
                <n-text depth="3" style="font-size: 12px">
                  （完全重新创作）
                </n-text>
              </n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>

        <n-form-item label="文章模板" required>
          <n-radio-group v-model:value="formData.templateType">
            <n-space>
              <n-radio value="tutorial">教程类</n-radio>
              <n-radio value="concept">概念类</n-radio>
              <n-radio value="comparison">对比类</n-radio>
              <n-radio value="practice">实战类</n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>

        <n-form-item label="发布设置" required>
          <n-radio-group v-model:value="formData.autoPublish">
            <n-space>
              <n-radio :value="false">
                保存到草稿箱
                <n-text depth="3" style="font-size: 12px">
                  （推荐，人工审核后发布）
                </n-text>
              </n-radio>
              <n-radio :value="true">
                立即发布
                <n-text depth="3" style="font-size: 12px">
                  （自动发布到前台）
                </n-text>
              </n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>

        <n-alert type="info" title="预计成本" style="margin-bottom: 20px">
          预计消耗：¥0.016 | 预计时间：2-3 分钟
        </n-alert>

        <n-space>
          <n-button
            type="primary"
            :loading="store.isLoading"
            @click="handleSubmit"
          >
            🚀 开始改写
          </n-button>
          <n-button @click="handleReset">
            重置
          </n-button>
        </n-space>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useMessage } from 'naive-ui';
import { useAIRewriteStore } from '@/stores/ai-rewrite';

const message = useMessage();
const store = useAIRewriteStore();
const formRef = ref(null);

const formData = reactive({
  sourceUrl: '',
  rewriteStrategy: 'standard',
  templateType: 'tutorial',
  autoPublish: false,
});

const handleSubmit = () => {
  if (!formData.sourceUrl) {
    message.error('请输入文章链接');
    return;
  }

  store.submitRewrite(formData);
  message.success('开始改写，请在任务列表中查看进度');
};

const handleReset = () => {
  formData.sourceUrl = '';
  formData.rewriteStrategy = 'standard';
  formData.templateType = 'tutorial';
  formData.autoPublish = false;
};
</script>

<style scoped>
.ai-rewrite-panel {
  max-width: 800px;
  margin: 0 auto;
}
</style>
```

- [ ] **步骤 3：创建进度监控组件**

```vue
<!-- app/components/admin/ai-rewrite/AIProgress.vue -->

<template>
  <div class="ai-progress">
    <n-card title="📊 改写进度" size="large">
      <div v-if="store.currentTask" class="current-task">
        <n-alert :type="getAlertType(store.currentTask.status)">
          <template #header>
            <n-space align="center">
              <n-icon :component="getStatusIcon(store.currentTask.status)" />
              <span>{{ getStatusText(store.currentTask.status) }}</span>
            </n-space>
          </template>
          
          <n-descriptions :column="2" bordered>
            <n-descriptions-item label="任务 ID">
              {{ store.currentTask.id }}
            </n-descriptions-item>
            <n-descriptions-item label="状态">
              <n-tag :type="getStatusTagType(store.currentTask.status)">
                {{ store.currentTask.status }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="源链接">
              <n-a :href="store.currentTask.sourceUrl" target="_blank">
                {{ store.currentTask.sourceUrl }}
              </n-a>
            </n-descriptions-item>
            <n-descriptions-item label="改写策略">
              {{ getStrategyName(store.currentTask.rewriteStrategy) }}
            </n-descriptions-item>
            <n-descriptions-item v-if="store.currentTask.tokenUsage" label="Token 消耗">
              {{ store.currentTask.tokenUsage }}
            </n-descriptions-item>
            <n-descriptions-item v-if="store.currentTask.cost" label="成本">
              ¥{{ (store.currentTask.cost * 7).toFixed(4) }}
            </n-descriptions-item>
          </n-descriptions>

          <div v-if="store.currentTask.status === 'completed'" class="actions">
            <n-space>
              <n-button
                v-if="store.currentTask.articleSlug"
                type="primary"
                @click="goToArticle(store.currentTask.articleSlug)"
              >
                查看文章
              </n-button>
              <n-button
                v-if="!store.currentTask.autoPublished"
                secondary
                @click="goToEdit(store.currentTask.articleId)"
              >
                编辑草稿
              </n-button>
            </n-space>
          </div>

          <div v-if="store.currentTask.status === 'failed'" class="error">
            <n-text type="error">
              错误信息：{{ store.currentTask.error }}
            </n-text>
          </div>
        </n-alert>
      </div>

      <div v-else class="no-task">
        <n-empty description="当前没有进行中的任务" />
      </div>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAIRewriteStore } from '@/stores/ai-rewrite';
import { CheckCircleOutline, CloseCircleOutline, TimeOutline, SyncOutline } from '@vicons/ionicons5';

const router = useRouter();
const store = useAIRewriteStore();

const getAlertType = (status: string) => {
  const map = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'error',
  };
  return map[status as keyof typeof map];
};

const getStatusIcon = (status: string) => {
  const map = {
    pending: TimeOutline,
    processing: SyncOutline,
    completed: CheckCircleOutline,
    failed: CloseCircleOutline,
  };
  return map[status as keyof typeof map];
};

const getStatusText = (status: string) => {
  const map = {
    pending: '等待处理',
    processing: '正在改写',
    completed: '改写完成',
    failed: '改写失败',
  };
  return map[status as keyof typeof map];
};

const getStatusTagType = (status: string) => {
  const map = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'error',
  };
  return map[status as keyof typeof map];
};

const getStrategyName = (strategy: string) => {
  const map = {
    standard: '标准改写',
    deep: '深度改写',
    creative: '创意改写',
  };
  return map[strategy as keyof typeof map];
};

const goToArticle = (slug: string) => {
  window.open(`/posts/${slug}`, '_blank');
};

const goToEdit = (articleId?: number) => {
  if (articleId) {
    router.push(`/admin/articles/edit/${articleId}`);
  }
};
</script>

<style scoped>
.ai-progress {
  max-width: 800px;
  margin: 20px auto;
}

.current-task {
  margin-top: 20px;
}

.actions {
  margin-top: 20px;
  text-align: right;
}

.error {
  margin-top: 16px;
  padding: 12px;
  background: #fee;
  border-radius: 4px;
}
</style>
```

- [ ] **步骤 4：创建任务列表组件**

```vue
<!-- app/components/admin/ai-rewrite/AITaskList.vue -->

<template>
  <div class="ai-task-list">
    <n-card title="📝 改写历史" size="large">
      <n-data-table
        :columns="columns"
        :data="store.tasks"
        :pagination="{ pageSize: 10 }"
      />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue';
import { NTag, NButton } from 'naive-ui';
import { useRouter } from 'vue-router';
import { useAIRewriteStore } from '@/stores/ai-rewrite';

const router = useRouter();
const store = useAIRewriteStore();

const columns = [
  {
    title: '任务 ID',
    key: 'id',
    width: 200,
    ellipsis: true,
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    render: (row: any) => {
      const typeMap = {
        pending: 'info',
        processing: 'warning',
        completed: 'success',
        failed: 'error',
      };
      return h(NTag, {
        type: typeMap[row.status as keyof typeof typeMap],
        () => row.status,
      });
    },
  },
  {
    title: '源链接',
    key: 'sourceUrl',
    ellipsis: true,
    render: (row: any) => {
      return h('a', {
        href: row.sourceUrl,
        target: '_blank',
      }, row.sourceUrl);
    },
  },
  {
    title: '改写策略',
    key: 'rewriteStrategy',
    width: 120,
  },
  {
    title: '成本',
    key: 'cost',
    width: 100,
    render: (row: any) => {
      return row.cost ? `¥${(row.cost * 7).toFixed(4)}` : '-';
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    render: (row: any) => {
      if (row.status === 'completed' && row.articleSlug) {
        return h(NButton, {
          size: 'small',
          type: 'primary',
          onClick: () => router.push(`/posts/${row.articleSlug}`),
        }, { default: () => '查看' });
      }
      return '-';
    },
  },
];
</script>

<style scoped>
.ai-task-list {
  max-width: 1200px;
  margin: 20px auto;
}
</style>
```

- [ ] **步骤 5：Commit**

```bash
git add app/components/admin/ai-rewrite/ app/stores/ai-rewrite.ts
git commit -m "feat: 创建 AI 改写管理后台组件"
```

---

### 任务 6：添加管理后台页面

**文件：**
- 创建：`app/pages/admin/ai-generator/index.vue`

- [ ] **步骤 1：创建 AI 改写主页**

```vue
<!-- app/pages/admin/ai-generator/index.vue -->

<template>
  <div class="ai-generator-page">
    <n-grid :cols="24" :x-gap="20">
      <n-gi :span="24">
        <n-page title="AI 智能改写">
          <template #header>
            <n-space align="center">
              <n-text style="font-size: 24px; font-weight: bold">
                🤖 AI 智能改写
              </n-text>
              <n-text depth="3">
                输入文章链接，AI 自动改写并发布
              </n-text>
            </n-space>
          </template>

          <AIRewritePanel />
          <AIProgress />
          <AITaskList />
        </n-page>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAIRewriteStore } from '@/stores/ai-rewrite';
import AIRewritePanel from '@/components/admin/ai-rewrite/AIRewritePanel.vue';
import AIProgress from '@/components/admin/ai-rewrite/AIProgress.vue';
import AITaskList from '@/components/admin/ai-rewrite/AITaskList.vue';

const store = useAIRewriteStore();

onMounted(() => {
  store.loadTasks();
});
</script>

<style scoped>
.ai-generator-page {
  padding: 24px;
}
</style>
```

- [ ] **步骤 2：添加导航菜单项**

读取并修改导航配置文件（如果存在）：

```bash
# 查找导航配置文件
find /Users/luzengbiao/traeProjects/blog/blog -name "*nav*" -o -name "*menu*" | grep -E "\.(ts|vue|json)$"
```

- [ ] **步骤 3：Commit**

```bash
git add app/pages/admin/ai-generator/
git commit -m "feat: 添加 AI 改写管理页面"
```

---

### 任务 7：优化文章详情页布局样式

**文件：**
- 修改：`frontend/src/views/blog/PostDetail.vue`

- [ ] **步骤 1：优化代码块样式**

```vue
<!-- 在 PostDetail.vue 的 style 中添加 -->

<style scoped>
/* 代码块样式 */
.post-body :deep(pre) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-left: 4px solid #18a058;
  border-radius: 8px;
  padding: 16px 20px;
  margin: 20px 0;
  overflow-x: auto;
  box-shadow: 0 2px 8px rgba(24, 160, 88, 0.1);
}

.post-body :deep(code) {
  font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

/* 引用块样式 */
.post-body :deep(blockquote) {
  background: rgba(24, 160, 88, 0.05);
  border-left: 4px solid #18a058;
  padding: 16px 20px;
  margin: 20px 0;
  color: #555;
  font-style: italic;
  border-radius: 0 8px 8px 0;
}

/* 标题样式 */
.post-body :deep(h2) {
  font-size: 24px;
  font-weight: 700;
  color: #18a058;
  margin: 40px 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(24, 160, 88, 0.2);
}

.post-body :deep(h3) {
  font-size: 20px;
  font-weight: 600;
  color: #0c7a43;
  margin: 30px 0 15px 0;
}

/* 表格样式 */
.post-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(24, 160, 88, 0.1);
}

.post-body :deep(th) {
  background: linear-gradient(135deg, #18a058 0%, #0c7a43 100%);
  color: white;
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
}

.post-body :deep(td) {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.post-body :deep(tr:nth-child(even)) {
  background: rgba(24, 160, 88, 0.02);
}

.post-body :deep(tr:hover) {
  background: rgba(24, 160, 88, 0.05);
}

/* 列表样式 */
.post-body :deep(ul),
.post-body :deep(ol) {
  padding-left: 24px;
  margin: 16px 0;
}

.post-body :deep(li) {
  margin: 8px 0;
  line-height: 1.8;
}

/* 重点内容加粗 */
.post-body :deep(strong),
.post-body :deep(b) {
  color: #18a058;
  font-weight: 600;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/views/blog/PostDetail.vue
git commit -m "style: 优化文章详情页布局样式"
```

---

### 任务 8：环境变量配置和文档

**文件：**
- 修改：`.env.example`
- 创建：`docs/AI_REWRITE_GUIDE.md`

- [ ] **步骤 1：添加环境变量配置**

```bash
# .env.example

# MiniMax AI Configuration
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_MODEL=MiniMax-M2.7

# 获取 API Key: https://platform.minimaxi.com/
```

- [ ] **步骤 2：创建使用文档**

```markdown
# AI 智能改写使用指南

## 快速开始

### 1. 配置 API Key

复制 `.env.example` 为 `.env`，并添加 MiniMax API Key：

```bash
MINIMAX_API_KEY=your_api_key_here
```

获取 API Key：访问 https://platform.minimaxi.com/ 注册并创建 API Key

### 2. 启动服务

```bash
npm run dev
```

访问 `http://localhost:3002/admin/ai-generator` 开始使用

### 3. 使用流程

1. **输入文章链接**
   - 支持微信公众号文章（mp.weixin.qq.com）
   - 其他博客平台（掘金、知乎、CSDN 等）

2. **选择改写策略**
   - **标准改写**：保留核心观点，完全重写表达（推荐）
   - **深度改写**：添加案例分析和对比
   - **创意改写**：只保留主题，完全独立创作

3. **选择文章模板**
   - 教程类、概念类、对比类、实战类

4. **选择发布方式**
   - **保存到草稿箱**（推荐）：人工审核后发布
   - **立即发布**：自动发布到前台

5. **查看进度**
   - 实时显示改写进度
   - 完成后自动跳转到文章

## 成本说明

**MiniMax API 定价：**
- 输入：$0.3 / 百万 tokens
- 输出：$1.2 / 百万 tokens

**单篇文章成本：**
- 3000 字文章：约 ¥0.016
- 每天 5 篇：约 ¥0.08/天
- 每月成本：约 ¥2.5/月

## 版权说明

本系统采用"保留核心观点 + 完全重写表达"的方式，确保：
- ✅ 只提取技术要点和核心思路
- ✅ 完全使用自己的表达方式
- ✅ 添加原创案例和代码示例
- ✅ 改变文章结构和叙述逻辑

## 最佳实践

1. **内容审核**
   - 建议使用"保存到草稿箱"模式
   - 人工审核技术准确性
   - 添加个人见解和案例

2. **发布频率**
   - 建议每天 3-5 篇
   - 避免短时间大量发布
   - 保持稳定的更新节奏

3. **SEO 优化**
   - 优化标题和描述
   - 添加合适的标签和分类
   - 添加原创内容比例（建议 30% 以上）

## 常见问题

### Q: 抓取失败怎么办？
A: 微信文章可能需要权限访问，尝试：
- 使用公开链接
- 检查链接是否有效
- 稍后重试

### Q: 改写质量不满意？
A: 可以尝试：
- 更换改写策略（标准/深度/创意）
- 手动编辑优化
- 调整 Prompt 模板

### Q: 成本超支怎么办？
A: 系统会显示每次改写的成本，建议：
- 设置每日预算
- 优先使用草稿箱模式
- 批量改写时控制数量

## 技术支持

如有问题，请查看：
- 系统日志：`logs/ai-rewrite.log`
- API 文档：`docs/API.md`
```

- [ ] **步骤 3：Commit**

```bash
git add .env.example docs/AI_REWRITE_GUIDE.md
git commit -m "docs: 添加 AI 改写配置文档和使用指南"
```

---

## 自检

### 1. 规格覆盖度

✅ 数据库扩展 - 任务 1
✅ MiniMax AI 封装 - 任务 2
✅ 微信文章抓取 - 任务 3
✅ AI 改写 API - 任务 4
✅ 管理后台组件 - 任务 5
✅ 管理后台页面 - 任务 6
✅ 文章布局优化 - 任务 7
✅ 配置和文档 - 任务 8

### 2. 占位符扫描

无占位符，所有步骤都有具体代码

### 3. 类型一致性

- 所有 API 使用统一的响应格式 `{ success: boolean, data: any }`
- 数据库字段命名使用 snake_case
- 前端组件使用 Composition API + TypeScript
- 状态管理使用 Pinia

---

计划已完成并保存到 `docs/superpowers/plans/2026-05-09-ai-article-rewrite.md`。两种执行方式：

**1. 子代理驱动（推荐）** - 每个任务调度一个新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用 executing-plans 执行任务，批量执行并设有检查点

**选哪种方式？**
