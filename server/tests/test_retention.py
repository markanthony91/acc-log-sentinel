from datetime import datetime, timezone

from src.retention import build_retention_plan


def test_build_retention_plan_windows():
    now = datetime(2026, 3, 10, 14, 0, tzinfo=timezone.utc)

    plan = build_retention_plan(now=now, event_days=30, metric_days=90)

    assert plan.events_cutoff == datetime(2026, 2, 8, 14, 0, tzinfo=timezone.utc)
    assert plan.metrics_cutoff == datetime(2025, 12, 10, 14, 0, tzinfo=timezone.utc)
