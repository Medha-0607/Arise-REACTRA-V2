"""
Unit test for /api/v1/health endpoint.
Verifies response status, version metadata, and JSON structure.
"""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    """Verifies that GET /api/v1/health returns 200 OK and expected contract keys."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "reactra-api"
    assert data["api_version"] == "v1"
    assert "app_version" in data
