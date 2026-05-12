/**
 * AI Chat API Client
 */
import { apiClient } from '@/utils/api'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  message: string
  conversation_history?: ChatMessage[]
}

export interface ChatResponse {
  reply: string
  model: string
  usage: {
    total_tokens: number
  }
}

export const aiChatApi = {
  /**
   * Send a message to AI chat
   */
  async chat(message: string, conversation_history?: ChatMessage[]): Promise<ChatResponse> {
    const request: ChatRequest = {
      message,
      conversation_history
    }
    
    const response = await apiClient.post<ChatResponse>('ai/chat', request)
    return response
  },
}
