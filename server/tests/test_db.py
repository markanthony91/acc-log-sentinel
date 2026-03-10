from src.db import parse_payload


def test_parse_payload_events():
    raw = {
        "hostname": "LOJA-042",
        "collected_at": "2026-03-10T14:00:00Z",
        "events": [
            {
                "source": "System",
                "event_id": 7034,
                "level": "Error",
                "message": "Service terminated unexpectedly",
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

    events, metric = parse_payload(raw)

    assert len(events) == 1
    assert events[0].hostname == "LOJA-042"
    assert events[0].event_id == 7034
    assert events[0].level == "Error"
    assert events[0].source == "System"
    assert metric.hostname == "LOJA-042"


def test_parse_payload_metrics():
    raw = {
        "hostname": "LOJA-001",
        "collected_at": "2026-03-10T14:00:00Z",
        "events": [],
        "metrics": {
            "cpu_percent": 90.5,
            "ram_available_mb": 256,
            "disk_free_percent": 5.2,
            "uptime_hours": 720.0,
            "reliability_index": 3.1,
        },
        "bsod_detected": True,
    }

    events, metric = parse_payload(raw)

    assert len(events) == 0
    assert metric.hostname == "LOJA-001"
    assert metric.cpu_percent == 90.5
    assert metric.ram_available_mb == 256
    assert metric.disk_free_percent == 5.2
    assert metric.bsod_detected is True
