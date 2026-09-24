"""Core configuration and constants package."""
from app.core.config import settings, EnvironmentType
from app.core.constants import (
    APP_NAME,
    APP_VERSION,
    API_VERSION,
    SERVICE_NAME,
    PRESUMPTIVE_DISCLAIMER,
)

__all__ = [
    "settings",
    "EnvironmentType",
    "APP_NAME",
    "APP_VERSION",
    "API_VERSION",
    "SERVICE_NAME",
    "PRESUMPTIVE_DISCLAIMER",
]
