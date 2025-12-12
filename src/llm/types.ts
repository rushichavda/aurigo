/**
 * Common types for LLM interactions
 */

export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface LLMRequest {
  messages: Message[];
  temperature?: number;
  maxTokens?: number;
  model?: string;
  stream?: boolean;
}

export interface LLMResponse {
  content: string;
  model: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  finishReason?: string;
}

export interface LLMProvider {
  /**
   * Send a request to the LLM provider
   */
  chat(request: LLMRequest): Promise<LLMResponse>;

  /**
   * Get the name of the provider
   */
  getProviderName(): string;

  /**
   * Validate configuration
   */
  validateConfig(): boolean;
}
