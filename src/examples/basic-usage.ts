/**
 * Basic usage examples for the LLM module
 */

import { LLMFactory, LLMProvider } from '../llm';

/**
 * Example 1: Create provider from environment
 */
export async function exampleFromEnv() {
  const llm = LLMFactory.createFromEnv();

  const response = await llm.chat({
    messages: [
      { role: 'user', content: 'Hello! How can you help with EB-1A applications?' },
    ],
  });

  console.log(response.content);
}

/**
 * Example 2: Create provider manually
 */
export async function exampleManualConfig() {
  const llm = LLMFactory.createProvider({
    provider: 'openrouter',
    apiKey: 'your-api-key-here',
    model: 'meta-llama/llama-3.1-8b-instruct:free',
  });

  const response = await llm.chat({
    messages: [
      { role: 'user', content: 'Explain EB-1A in simple terms.' },
    ],
    temperature: 0.5,
    maxTokens: 200,
  });

  console.log(response.content);
}

/**
 * Example 3: Multi-turn conversation
 */
export async function exampleConversation() {
  const llm = LLMFactory.createFromEnv();

  const messages = [
    { role: 'system' as const, content: 'You are an immigration expert.' },
    { role: 'user' as const, content: 'What documents are needed for EB-1A?' },
  ];

  // First turn
  const response1 = await llm.chat({ messages });
  console.log('Assistant:', response1.content);

  // Add response to conversation
  messages.push({ role: 'assistant', content: response1.content });
  messages.push({ role: 'user', content: 'Can you elaborate on recommendation letters?' });

  // Second turn
  const response2 = await llm.chat({ messages });
  console.log('Assistant:', response2.content);
}

/**
 * Example 4: Switching providers (future)
 */
export async function exampleSwitchProvider() {
  // Easy to switch between providers by changing config
  const providers = [
    { provider: 'openrouter' as const, apiKey: process.env.OPENROUTER_API_KEY! },
    // { provider: 'openai' as const, apiKey: process.env.OPENAI_API_KEY! },
    // { provider: 'anthropic' as const, apiKey: process.env.ANTHROPIC_API_KEY! },
  ];

  for (const config of providers) {
    try {
      const llm = LLMFactory.createProvider(config);
      const response = await llm.chat({
        messages: [{ role: 'user', content: 'Test message' }],
      });
      console.log(`${config.provider}:`, response.content.slice(0, 100));
    } catch (error) {
      console.log(`${config.provider}: Not configured or not supported yet`);
    }
  }
}
