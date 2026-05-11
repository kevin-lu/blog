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
  }): Promise<{
    corePoints: string;
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

    const totalTokens = extractResponse.usage.total_tokens +
                       rewriteResponse.usage.total_tokens +
                       layoutResponse.usage.total_tokens;

    return {
      corePoints,
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
}
