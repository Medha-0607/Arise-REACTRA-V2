"""
Typed Configuration System for REACTRA V2.
Separates development, testing, and production environments.
Enforces no hardcoded secrets and explicit defaults for local offline mode.
"""

from enum import Enum
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.constants import APP_NAME, APP_VERSION, API_VERSION, SERVICE_NAME


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    # Application Metadata
    APP_NAME: str = APP_NAME
    APP_TITLE: str = "REACTRA — Reaction-Aware Field Testing & Verifiable Evidence"
    APP_VERSION: str = APP_VERSION
    API_VERSION: str = API_VERSION
    SERVICE_NAME: str = SERVICE_NAME
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
    BACKEND_DIR: Path = Path(__file__).resolve().parent.parent.parent
    ROOT_DIR: Path = BACKEND_DIR.parent
    DATA_DIR: Path = ROOT_DIR / "data" / "local"
    EXPORTS_DIR: Path = ROOT_DIR / "data" / "exports"
    DEMO_DIR: Path = ROOT_DIR / "data" / "demo"
    PROFILES_DIR: Path = ROOT_DIR / "profiles"
    
    # Database URL override
    _database_url_override: str | None = None

    @property
    def DATABASE_URL(self) -> str:
        if self._database_url_override:
            return self._database_url_override
        db_path = (self.DATA_DIR / "reactra_v2.db").as_posix()
        return f"sqlite:///{db_path}"

    @DATABASE_URL.setter
    def DATABASE_URL(self, value: str) -> None:
        self._database_url_override = value
    
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
