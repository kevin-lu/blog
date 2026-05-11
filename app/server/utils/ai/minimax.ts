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
      reasoning_content?: string;
      reasoning_details?: Array<{ text?: string }>;
    };
  }>;
  usage: {
    total_tokens: number;
  };
}

export class MiniMaxAI {
  private apiKey: string;
  private model: string;
  private baseUrl = process.env.MINIMAX_API_HOST || 'https://api.minimax.io/v1/chat/completions';

  constructor(config: MiniMaxConfig) {
    this.apiKey = config.apiKey;
    this.model = this.normalizeModel(config.model || process.env.MINIMAX_MODEL || 'MiniMax-M2.7');
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
        reasoning_split: true,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`MiniMax API 请求失败：${response.status} - ${error}`);
    }

    const result = await response.json();
    
    if (result.choices && result.choices[0]?.message?.content) {
      result.choices[0].message.content = this.cleanAssistantContent(result.choices[0].message.content);
    }
    
    return result;
  }

  async rewriteArticle(content: string, prompts: {
    extractPrompt: string;
    rewritePrompt: string;
    layoutPrompt: string;
    originalTitle?: string;
  }): Promise<{
    corePoints: string;
    title: string;
    rewrittenContent: string;
    tokenUsage: number;
  }> {
    // 第一步：提取核心观点
    const extractResponse = await this.chat([
      { role: 'system', content: '你是一个专业的技术编辑。请严格按照用户要求提取内容，不要添加任何解释。' },
      { role: 'user', content: prompts.extractPrompt + '\n\n' + content }
    ]);
    let corePoints = extractResponse.choices[0].message.content;
    // 二次过滤确保没有思考内容
    corePoints = this.filterThinking(corePoints);

    // 第二步：基于核心观点重写
    const rewriteResponse = await this.chat([
      { role: 'system', content: '你是一个轻松幽默的技术博主。请直接开始写文章，不要复述要求，不要说废话。' },
      { role: 'user', content: prompts.rewritePrompt + '\n\n核心观点：\n' + corePoints }
    ], { temperature: 0.8 });
    let rewrittenContent = rewriteResponse.choices[0].message.content;
    rewrittenContent = this.filterThinking(rewrittenContent);

    // 第三步：优化布局
    const layoutResponse = await this.chat([
      { role: 'system', content: '你是一个微信公众号排版专家。请直接返回排版后的Markdown内容，不要复述规则，不要添加任何解释。' },
      { role: 'user', content: prompts.layoutPrompt + '\n\n文章内容：\n' + rewrittenContent }
    ]);
    let finalContent = layoutResponse.choices[0].message.content;
    finalContent = this.filterThinking(finalContent);

    // 第四步：重新拟定标题，避免沿用原公众号标题
    const titleResponse = await this.chat([
      { role: 'system', content: '你是一个技术博客标题编辑。请只输出一个新的中文标题，不要解释，不要加引号，不要使用 Markdown。' },
      {
        role: 'user',
        content: [
          '请基于下面已经改写完成的文章，重新拟一个适合技术博客的新标题。',
          '要求：',
          '1. 不要照搬原标题，也不要只做同义词替换',
          '2. 标题要准确概括文章主题，避免夸张标题党',
          '3. 长度控制在 12-32 个中文字符左右',
          '4. 只输出标题本身',
          '',
          `原标题：${prompts.originalTitle || '无'}`,
          '',
          `文章内容：\n${finalContent.substring(0, 3000)}`,
        ].join('\n'),
      },
    ], { temperature: 0.8, maxTokens: 120 });
    const generatedTitle = this.cleanTitle(titleResponse.choices[0].message.content);
    const title = generatedTitle || this.extractTitleFromMarkdown(finalContent) || prompts.originalTitle || '未命名文章';
    finalContent = this.replaceMarkdownTitle(finalContent, title);

    const totalTokens = extractResponse.usage.total_tokens +
                       rewriteResponse.usage.total_tokens +
                       layoutResponse.usage.total_tokens +
                       titleResponse.usage.total_tokens;

    return {
      corePoints,
      title,
      rewrittenContent: finalContent,
      tokenUsage: totalTokens,
    };
  }

  private filterThinking(content: string): string {
    return this.cleanAssistantContent(content);
  }

  private cleanAssistantContent(content: string): string {
    return content
      .replace(/<think\b[^>]*>[\s\S]*?<\/think>/gi, '')
      .replace(/<thinking\b[^>]*>[\s\S]*?<\/thinking>/gi, '')
      .replace(/<reasoning\b[^>]*>[\s\S]*?<\/reasoning>/gi, '')
      .replace(/^\s*```(?:markdown|md)?\s*\n([\s\S]*?)\n```\s*$/i, '$1')
      .trim();
  }

  private normalizeModel(model: string): string {
    const trimmed = model.trim();
    if (/^m2(\.|$)/i.test(trimmed)) {
      return `MiniMax-${trimmed.replace(/^m/i, 'M')}`;
    }
    return trimmed;
  }

  private cleanTitle(title: string): string {
    return this.cleanAssistantContent(title)
      .split('\n')[0]
      .replace(/^#+\s*/, '')
      .replace(/^(?:标题|新标题|文章标题)[:：]\s*/i, '')
      .replace(/^["'“‘《【\s]+|["'”’》】\s]+$/g, '')
      .trim()
      .substring(0, 80);
  }

  private extractTitleFromMarkdown(content: string): string {
    const match = content.match(/^\s*#\s+(.+)$/m);
    return match ? this.cleanTitle(match[1]) : '';
  }

  private replaceMarkdownTitle(content: string, title: string): string {
    if (!title) return content;
    if (/^\s*#\s+.+$/m.test(content)) {
      return content.replace(/^\s*#\s+.+$/m, `# ${title}`);
    }
    return content;
  }
}
