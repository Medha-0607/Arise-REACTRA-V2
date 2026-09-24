"""
Health Check Route Handler for REACTRA V2.
Delegates to HealthService; no inline business logic.
"""

from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.services.health import HealthService

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Returns the operational health of the REACTRA V2 API service."""
    return HealthService.get_health_status()
