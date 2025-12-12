import { LLMProvider } from './types';
import { OpenRouterProvider } from './providers/openrouter';

export type ProviderType = 'openrouter' | 'openai' | 'anthropic';

export interface LLMConfig {
  provider: ProviderType;
  apiKey: string;
  model?: string;
}

/**
 * Factory class to create LLM providers
 * Makes it easy to swap between different providers
 */
export class LLMFactory {
  static createProvider(config: LLMConfig): LLMProvider {
    switch (config.provider) {
      case 'openrouter':
        return new OpenRouterProvider(config.apiKey, config.model);

      case 'openai':
        // Placeholder for future OpenAI implementation
        throw new Error('OpenAI provider not yet implemented. Coming soon!');

      case 'anthropic':
        // Placeholder for future Anthropic implementation
        throw new Error('Anthropic provider not yet implemented. Coming soon!');

      default:
        throw new Error(`Unknown provider: ${config.provider}`);
    }
  }

  /**
   * Create provider from environment variables
   */
  static createFromEnv(): LLMProvider {
    const provider = (process.env.LLM_PROVIDER || 'openrouter') as ProviderType;
    const apiKey = this.getApiKeyFromEnv(provider);
    const model = process.env.LLM_MODEL;

    if (!apiKey) {
      throw new Error(
        `API key not found for provider: ${provider}. ` +
        `Please set the appropriate environment variable.`
      );
    }

    return this.createProvider({ provider, apiKey, model });
  }

  private static getApiKeyFromEnv(provider: ProviderType): string | undefined {
    switch (provider) {
      case 'openrouter':
        return process.env.OPENROUTER_API_KEY;
      case 'openai':
        return process.env.OPENAI_API_KEY;
      case 'anthropic':
        return process.env.ANTHROPIC_API_KEY;
      default:
        return undefined;
    }
  }
}
