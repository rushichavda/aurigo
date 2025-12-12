/**
 * LLM Module - Flexible interface for multiple LLM providers
 *
 * This module provides a unified interface to interact with different LLM providers.
 * Currently supports OpenRouter, with easy extensibility for OpenAI, Anthropic, etc.
 */

export { LLMProvider, LLMRequest, LLMResponse, Message } from './types';
export { LLMFactory, LLMConfig, ProviderType } from './factory';
export { OpenRouterProvider } from './providers/openrouter';
