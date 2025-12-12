from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pydantic import BaseModel


class Message(BaseModel):
    role: str  # 'system', 'user', 'assistant'
    content: str


class LLMRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    model: Optional[str] = None


class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Send a chat request to the LLM"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the provider"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration"""
        pass


# Alias for compatibility
BaseLLM = LLMProvider
