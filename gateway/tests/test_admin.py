import pytest
from gateway.core.config import settings


@pytest.mark.asyncio
async def test_admin_without_key_forbidden(async_client):
    response = await async_client.get("/admin/rate-limits")
    assert response.status_code == 403
    data = response.json()
    assert "Forbidden" in data["detail"] or "Invalid" in data["detail"]


@pytest.mark.asyncio
async def test_admin_metrics_with_valid_key(async_client):
    headers = {"X-Admin-Key": settings.ADMIN_KEY}
    response = await async_client.get("/admin/metrics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "endpoints" in data
