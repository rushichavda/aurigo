import dotenv from 'dotenv';
import path from 'path';

// Load environment variables from .env file
dotenv.config({ path: path.resolve(process.cwd(), '.env') });

export const config = {
  llm: {
    provider: (process.env.LLM_PROVIDER || 'openrouter') as 'openrouter' | 'openai' | 'anthropic',
    apiKey: process.env.OPENROUTER_API_KEY || '',
    model: process.env.LLM_MODEL || 'meta-llama/llama-3.1-8b-instruct:free',
  },
  app: {
    env: process.env.NODE_ENV || 'development',
    port: parseInt(process.env.PORT || '3000', 10),
  },
} as const;

/**
 * Validate required environment variables
 */
export function validateEnv(): void {
  const errors: string[] = [];

  if (!config.llm.apiKey && config.llm.provider === 'openrouter') {
    errors.push('OPENROUTER_API_KEY is required when using OpenRouter provider');
  }

  if (errors.length > 0) {
    throw new Error(
      'Environment validation failed:\n' + errors.map(e => `  - ${e}`).join('\n')
    );
  }
}
