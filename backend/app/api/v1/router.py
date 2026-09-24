"""
Central API v1 Router for REACTRA V2.
Aggregates versioned routes.
"""

from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.evidence import router as evidence_router

api_v1_router = APIRouter()

# Register core v1 routes
api_v1_router.include_router(health_router)
api_v1_router.include_router(sessions_router)
api_v1_router.include_router(profiles_router)
api_v1_router.include_router(evidence_router)
