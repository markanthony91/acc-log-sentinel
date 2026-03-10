from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.api import app


@pytest.fixture
def sample_payload():
    return {
        "hostname": "LOJA-042",
        "collected_at": "2026-03-10T14:00:00Z",
        "events": [
            {
                "source": "System",
                "event_id": 7034,
                "level": "Error",
                "message": "Service terminated",
                "timestamp": "2026-03-10T13:42:11Z",
            }
        ],
        "metrics": {
            "cpu_percent": 45.2,
            "ram_available_mb": 1024,
            "disk_free_percent": 12.5,
            "uptime_hours": 168.3,
            "reliability_index": 7.2,
        },
        "bsod_detected": False,
    }


@pytest.mark.asyncio
async def test_ingest_endpoint_success(sample_payload):
    with patch("src.api.store_payload", new_callable=AsyncMock) as mock_store:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/events", json=sample_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["hostname"] == "LOJA-042"
    mock_store.assert_awaited_once()


@pytest.mark.asyncio
async def test_ingest_endpoint_missing_hostname():
    payload = {"events": [], "metrics": {}}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/events", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "hostname" in body
