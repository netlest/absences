"""
FastAPI Configuration
Best practice: Use pydantic-settings for configuration management
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    Best practice: Centralize all configuration in a single settings class.
    """
    # Database settings
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_NAME: str = os.getenv("DB_NAME", "absences")
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Absences API"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # API Key/Bearer tokens (for simplicity, using a static list - in production use DB)
    # Best practice: In production, store API keys in database with hashing
    API_KEYS: List[str] = [
        "demo-api-key-12345",  # Example API key
        "test-bearer-token-67890"  # Another example
    ]
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


# Create global settings instance
# Best practice: Single source of truth for configuration
settings = Settings()
