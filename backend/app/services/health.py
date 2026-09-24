"""
Health Service Application Logic for REACTRA V2.
"""

from app.core.config import settings
from app.schemas.health import HealthResponse


class HealthService:
    """Provides application health status."""

    @staticmethod
    def get_health_status() -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=settings.SERVICE_NAME,
            api_version=settings.API_VERSION,
            app_version=settings.APP_VERSION,
        )
