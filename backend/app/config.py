from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Server
    app_name: str = "Aurigo EB-1A Assistant"
    port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./aurigo.db"

    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # LLM Configuration
    llm_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"
    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"

    # Feature Flags
    use_claude_polish: bool = False

    # Legacy OpenRouter
    openrouter_api_key: str = ""
    llm_model: str = "meta-llama/llama-3.1-8b-instruct:free"

    # CORS
    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
