from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    APP_NAME: str = "FinGuard AI"
    APP_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./finguard.db"

    # Security
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # LLM
    LLM_API_KEY: str = ""
    LLM_API_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_ENABLED: bool = False

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Risk thresholds (prototype values)
    RISK_LOW_MEDIUM: int = 30
    RISK_MEDIUM_HIGH: int = 60
    RISK_HIGH_CRITICAL: int = 80

    # Seed flag
    AUTO_SEED: bool = True
    DEMO_USER_EMAIL: str = "demo@finguard.ai"
    DEMO_USER_PASSWORD: str = "demo123"

    @model_validator(mode="after")
    def validate_security_settings(self):
        if self.ENVIRONMENT == "production" and self.JWT_SECRET_KEY in {
            "",
            "change-me-in-production",
            "please-change-this-secret-key",
        }:
            raise ValueError("JWT_SECRET_KEY must be configured in production")
        return self

    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
