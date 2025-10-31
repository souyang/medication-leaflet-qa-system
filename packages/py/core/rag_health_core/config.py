"""Configuration settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env in project root (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings from environment."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else ".env", extra="ignore"
    )

    # Redis
    redis_url: str | None = None
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_index_name: str = "idx:leaflets"

    # OpenAI
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-large"
    openai_embedding_dim: int = 3072
    openai_chat_model: str = "gpt-4o-mini"

    # W&B
    wandb_project: str = "rag-health-poc"
    wandb_entity: str | None = None
    wandb_api_key: str | None = None

    # W&B Weave (LLM tracing)
    weave_enabled: bool = True
    weave_project: str = "rag-health-weave"

    # RAG
    chunk_size: int = 1536
    chunk_overlap: int = 150
    retrieval_top_k: int = 6
    confidence_threshold: float = 0.7

    # API
    api_title: str = "RAG Health API"
    api_version: str = "0.1.0"
