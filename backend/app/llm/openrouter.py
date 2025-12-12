import httpx
from typing import Optional
from .base import LLMProvider, LLMRequest, LLMResponse


class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str, default_model: str = "meta-llama/llama-3.1-8b-instruct:free"):
        self.api_key = api_key
        self.default_model = default_model
        self.base_url = "https://openrouter.ai/api/v1"

    async def chat(self, request: LLMRequest) -> LLMResponse:
        """Send a chat request to OpenRouter"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/aurigo",
            "X-Title": "Aurigo EB-1A Assistant",
        }

        payload = {
            "model": request.model or self.default_model,
            "messages": [msg.model_dump() for msg in request.messages],
            "temperature": request.temperature,
        }

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice["message"]["content"],
            model=data["model"],
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            } if usage else None,
            finish_reason=choice.get("finish_reason"),
        )

    def get_provider_name(self) -> str:
        return "openrouter"

    def validate_config(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 0)
