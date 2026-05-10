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
  private baseUrl = process.env.MINIMAX_API_HOST || 'https://api.minimax.chat/v1/chat/completions';

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

    const result = await response.json();
    
    // 过滤掉模型的思考标签
    if (result.choices && result.choices[0]?.message?.content) {
      let content = result.choices[0].message.content;
      // 移除 <think> 和 </think> 标签及其内容
      content = content.replace(new RegExp('<think>[\\s\\S]*?</</think>>', 'g'), '').trim();
      result.choices[0].message.content = content;
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
