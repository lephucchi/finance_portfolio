"""
Application settings and configuration.
Handles environment variables and application-wide settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Follows 12-factor app methodology.
    """

    # ========================
    # APP CONFIGURATION
    # ========================
    APP_NAME: str = "Finance Portfolio Dashboard API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # ========================
    # API CONFIGURATION
    # ========================
    API_V1_STR: str = "/api/v1"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8000"
    
    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse ALLOWED_ORIGINS string into list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # ========================
    # AWS CONFIGURATION
    # ========================
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str = "ap-southeast-1"
    AWS_REGION: str = "ap-southeast-1"
    S3_BUCKET: str = "bankanalystportfolio"

    # ========================
    # ATHENA CONFIGURATION
    # ========================
    ATHENA_DATABASE: str = "finance_portfolio"
    ATHENA_RESULTS_LOCATION: str = "s3://bankanalystportfolio/athena_results/"
    ATHENA_WORKGROUP: str = "primary"
    ATHENA_OUTPUT_PATH: str = "s3://bankanalystportfolio/athena_results/"

    # ========================
    # SUPABASE CONFIGURATION
    # ========================
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # ========================
    # DATABASE CONFIGURATION
    # ========================
    # Connection pooling
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # Athena specific
    ATHENA_POLLING_INTERVAL: int = 1  # seconds
    ATHENA_MAX_WAIT_TIME: int = 300  # 5 minutes

    # ========================
    # CACHE CONFIGURATION
    # ========================
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    CACHE_TYPE: str = "redis"  # redis, memory
    REDIS_URL: Optional[str] = None

    # ========================
    # LOGGING CONFIGURATION
    # ========================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json, plain

    # ========================
    # REQUEST CONFIGURATION
    # ========================
    REQUEST_TIMEOUT: int = 30
    MAX_REQUEST_SIZE: int = 1024 * 1024 * 10  # 10 MB

    # ========================
    # PAGINATION CONFIGURATION
    # ========================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ========================
    # RAG CONFIGURATION
    # ========================
    RAG_ENABLED: bool = True
    RAG_MODEL_NAME: str = "intfloat/multilingual-e5-large"  # 1024-dim, matches FAISS index
    RAG_FAISS_INDEX_PATH: str = "data/rag/vector_index.faiss"  # Fixed: was faiss_index.bin
    RAG_METADATA_PATH: str = "data/rag/metadata.json"
    RAG_EMBEDDINGS_PATH: str = "data/rag/embeddings.npy"
    RAG_TOP_K: int = 5
    RAG_TEMPERATURE: float = 0.7
    RAG_MAX_TOKENS: int = 2048
    
    # MCP Configuration
    MCP_ENABLED: bool = True
    MCP_SERVER_PORT: int = 8001
    
    # User API Key Management
    ALLOW_USER_API_KEYS: bool = True  # Allow users to provide their own Gemini API keys
    DEFAULT_GEMINI_API_KEY: Optional[str] = None  # Optional default key for demo

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env that aren't in the model


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache to ensure single instance throughout app lifecycle.

    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Expose settings for easier imports
settings = get_settings()
