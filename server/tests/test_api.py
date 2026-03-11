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


@pytest.mark.asyncio
async def test_fleet_summary_endpoint():
    fake_summary = {
        "summary": {
            "total_machines": 10,
            "reporting_machines": 9,
            "silent_machines": 1,
            "machines_with_critical": 1,
            "machines_with_error": 3,
            "total_events": 20,
            "critical_count": 1,
            "error_count": 5,
            "warning_count": 14,
            "avg_reliability": 8.1,
        },
        "silent_hosts": ["LOJA-002"],
        "bsod_machines": [],
        "top_error_machines": [],
        "resource_alerts": [],
    }
    with patch("src.api.fetch_fleet_summary", new_callable=AsyncMock) as mock_summary:
        mock_summary.return_value = fake_summary
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/fleet/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["summary"]["total_machines"] == 10
    mock_summary.assert_awaited_once()


@pytest.mark.asyncio
async def test_machine_detail_endpoint():
    fake_machine = {
        "hostname": "LOJA-042",
        "first_seen": "2026-03-10T14:00:00+00:00",
        "last_seen": "2026-03-10T15:00:00+00:00",
        "event_counts_24h": {"critical": 0, "error": 2, "warning": 4},
        "latest_metric": None,
        "recent_events": [],
    }
    with patch("src.api.fetch_machine_detail", new_callable=AsyncMock) as mock_detail:
        mock_detail.return_value = fake_machine
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/machines/LOJA-042")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["hostname"] == "LOJA-042"
    mock_detail.assert_awaited_once()


@pytest.mark.asyncio
async def test_machine_detail_not_found():
    with patch("src.api.fetch_machine_detail", new_callable=AsyncMock) as mock_detail:
        mock_detail.return_value = None
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/machines/LOJA-404")

    assert response.status_code == 404
