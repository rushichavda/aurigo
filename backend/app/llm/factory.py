from typing import Literal
from .base import BaseLLM
from .openrouter import OpenRouterProvider
from .gemini import GeminiLLM
from .claude import ClaudeLLM


ProviderType = Literal["openrouter", "gemini", "claude"]


class LLMFactory:
    """Factory for creating LLM providers"""

    @staticmethod
    def create_provider(
        provider: ProviderType
    ) -> BaseLLM:
        """Create an LLM provider instance"""

        if provider == "gemini":
            return GeminiLLM()
        elif provider == "claude":
            return ClaudeLLM()
        elif provider == "openrouter":
            # Legacy support
            from ..config import get_settings
            settings = get_settings()
            return OpenRouterProvider(settings.openrouter_api_key, settings.llm_model)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    @staticmethod
    def create_from_config(config) -> BaseLLM:
        """Create provider from app configuration"""
        return LLMFactory.create_provider(provider=config.llm_provider)

    @staticmethod
    def create_gemini() -> GeminiLLM:
        """Create Gemini provider instance"""
        return GeminiLLM()

    @staticmethod
    def create_claude() -> ClaudeLLM:
        """Create Claude provider instance"""
        return ClaudeLLM()
