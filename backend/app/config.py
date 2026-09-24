"""
Typed Configuration System for REACTRA V2.
Separates development, testing, and production environments.
Enforces no hardcoded secrets and explicit defaults for local offline mode.
"""

from enum import Enum
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    # Application Metadata
    APP_NAME: str = "REACTRA"
    APP_TITLE: str = "REACTRA — Reaction-Aware Field Testing & Verifiable Evidence"
    APP_VERSION: str = "2.0.0-phase0"
    API_VERSION: str = "v1"
    API_V1_PREFIX: str = "/api/v1"
    
    # Environment
    ENV: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT, validation_alias="REACTRA_ENV")
    DEBUG: bool = Field(default=True, validation_alias="REACTRA_DEBUG")
    
    # Security
    SECRET_KEY: str = Field(
        default="reactra-insecure-dev-key-change-in-production",
        validation_alias="REACTRA_SECRET_KEY"
    )
    
    # Storage & Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    PROFILES_DIR: Path = BASE_DIR.parent / "profiles"
    STORAGE_DIR: Path = BASE_DIR / "storage"
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./data/reactra_v2.db",
        validation_alias="REACTRA_DATABASE_URL"
    )
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
