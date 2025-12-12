import axios, { AxiosInstance } from 'axios';
import { LLMProvider, LLMRequest, LLMResponse, Message } from '../types';

interface OpenRouterMessage {
  role: string;
  content: string;
}

interface OpenRouterRequest {
  model: string;
  messages: OpenRouterMessage[];
  temperature?: number;
  max_tokens?: number;
}

interface OpenRouterResponse {
  id: string;
  model: string;
  choices: Array<{
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export class OpenRouterProvider implements LLMProvider {
  private client: AxiosInstance;
  private apiKey: string;
  private defaultModel: string;

  constructor(apiKey: string, defaultModel: string = 'meta-llama/llama-3.1-8b-instruct:free') {
    this.apiKey = apiKey;
    this.defaultModel = defaultModel;

    this.client = axios.create({
      baseURL: 'https://openrouter.ai/api/v1',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://github.com/aurigo', // Optional: for rankings
        'X-Title': 'Aurigo EB-1A Assistant', // Optional: for rankings
      },
    });
  }

  async chat(request: LLMRequest): Promise<LLMResponse> {
    try {
      const openRouterRequest: OpenRouterRequest = {
        model: request.model || this.defaultModel,
        messages: request.messages.map(msg => ({
          role: msg.role,
          content: msg.content,
        })),
        temperature: request.temperature ?? 0.7,
        max_tokens: request.maxTokens,
      };

      const response = await this.client.post<OpenRouterResponse>(
        '/chat/completions',
        openRouterRequest
      );

      const choice = response.data.choices[0];

      return {
        content: choice.message.content,
        model: response.data.model,
        usage: response.data.usage ? {
          promptTokens: response.data.usage.prompt_tokens,
          completionTokens: response.data.usage.completion_tokens,
          totalTokens: response.data.usage.total_tokens,
        } : undefined,
        finishReason: choice.finish_reason,
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(
          `OpenRouter API error: ${error.response?.data?.error?.message || error.message}`
        );
      }
      throw error;
    }
  }

  getProviderName(): string {
    return 'openrouter';
  }

  validateConfig(): boolean {
    return !!this.apiKey && this.apiKey.length > 0;
  }
}
