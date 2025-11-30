"""Application settings using pydantic BaseSettings."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = ConfigDict(env_prefix="AIPS_")

    # Database
    database_url: str = f"sqlite:///./data/ai_productivity.db"

    # Redis (short-term session store)
    redis_url: str = "redis://localhost:6379/0"
    session_ttl: int = 3600

    # Chroma / embeddings
    chroma_persist_directory: str = str(Path("data") / "chroma")
    embedding_model: str = "all-MiniLM-L6-v2"

    # LLM / Google
    gemini_api_key: str = ""
    model_name: str = "gemini"  # placeholder


settings = Settings()