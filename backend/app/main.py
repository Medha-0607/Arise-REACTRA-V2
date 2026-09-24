"""
Main FastAPI Application Entrypoint for REACTRA V2.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_v1_router
from app.db.session import check_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events management for startup and shutdown."""
    # Ensure data directory exists
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    settings.DEMO_DIR.mkdir(parents=True, exist_ok=True)
    
    # Verify local DB connectivity
    db_ok = check_database_connection()
    if not db_ok:
        print("[WARNING] Database connection check failed at startup.")
    yield


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="Offline-first field evidence companion for presumptive colorimetric drug testing.",
    lifespan=lifespan
)

# Configure CORS for local frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router under /api/v1
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root redirect / information endpoint."""
    return {
        "product": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "api_docs": "/docs",
        "api_v1": settings.API_V1_PREFIX
    }
