from dataclasses import dataclass
from datetime import datetime


@dataclass
class EventRow:
    hostname: str
    source: str
    event_id: int
    level: str
    message: str
    timestamp: datetime
    collected_at: datetime


@dataclass
class MetricRow:
    hostname: str
    cpu_percent: float
    ram_available_mb: float
    disk_free_percent: float
    uptime_hours: float
    reliability_index: float
    bsod_detected: bool
    collected_at: datetime


def _parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_payload(raw: dict) -> tuple[list[EventRow], MetricRow]:
    hostname = raw["hostname"]
    collected_at = _parse_iso_datetime(raw["collected_at"])

    events: list[EventRow] = []
    for item in raw.get("events", []):
        events.append(
            EventRow(
                hostname=hostname,
                source=item["source"],
                event_id=item["event_id"],
                level=item["level"],
                message=item.get("message", ""),
                timestamp=_parse_iso_datetime(item["timestamp"]),
                collected_at=collected_at,
            )
        )

    metrics = raw.get("metrics", {})
    metric = MetricRow(
        hostname=hostname,
        cpu_percent=metrics.get("cpu_percent", 0),
        ram_available_mb=metrics.get("ram_available_mb", 0),
        disk_free_percent=metrics.get("disk_free_percent", 0),
        uptime_hours=metrics.get("uptime_hours", 0),
        reliability_index=metrics.get("reliability_index", -1),
        bsod_detected=raw.get("bsod_detected", False),
        collected_at=collected_at,
    )

    return events, metric


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS machines (
    hostname TEXT PRIMARY KEY,
    first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    hostname TEXT NOT NULL REFERENCES machines(hostname),
    source TEXT NOT NULL,
    event_id INTEGER NOT NULL,
    level TEXT NOT NULL,
    message TEXT,
    event_timestamp TIMESTAMPTZ NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    hostname TEXT NOT NULL REFERENCES machines(hostname),
    cpu_percent REAL,
    ram_available_mb REAL,
    disk_free_percent REAL,
    uptime_hours REAL,
    reliability_index REAL,
    bsod_detected BOOLEAN NOT NULL DEFAULT FALSE,
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_hostname_ts ON events(hostname, event_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_level_ts ON events(level, event_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_hostname_ts ON metrics(hostname, collected_at DESC);
"""
