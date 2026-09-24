"""
Health Response Pydantic Schema for REACTRA V2.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status indicator")
    service: str = Field(..., description="Service name identifier")
    api_version: str = Field(..., description="API contract version")
    app_version: str = Field(..., description="Application release version")
