/**
 * Example usage of the LLM module
 */

import { LLMFactory } from './llm';
import { config, validateEnv } from './config/env';

async function main() {
  try {
    // Validate environment configuration
    validateEnv();

    // Create LLM provider from environment variables
    const llm = LLMFactory.createFromEnv();

    console.log(`Using provider: ${llm.getProviderName()}`);
    console.log(`Model: ${config.llm.model}\n`);

    // Example 1: Simple question
    const response1 = await llm.chat({
      messages: [
        {
          role: 'user',
          content: 'What are the key criteria for EB-1A visa eligibility?',
        },
      ],
      temperature: 0.7,
      maxTokens: 500,
    });

    console.log('Example 1: EB-1A Eligibility Criteria');
    console.log('=====================================');
    console.log(response1.content);
    console.log('\nUsage:', response1.usage);
    console.log('\n---\n');

    // Example 2: System prompt with context
    const response2 = await llm.chat({
      messages: [
        {
          role: 'system',
          content: 'You are an expert immigration attorney assistant specializing in EB-1A visas.',
        },
        {
          role: 'user',
          content: 'Draft a brief introduction paragraph for a letter of support.',
        },
      ],
      temperature: 0.8,
      maxTokens: 300,
    });

    console.log('Example 2: Draft Introduction');
    console.log('=============================');
    console.log(response2.content);
    console.log('\nUsage:', response2.usage);

  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : error);
    process.exit(1);
  }
}

// Run if this is the main module
if (require.main === module) {
  main();
}

export { main };
