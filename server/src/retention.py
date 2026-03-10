import logging
import socket
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from src.database import get_pool

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetentionPlan:
    events_cutoff: datetime
    metrics_cutoff: datetime


def build_retention_plan(
    now: datetime | None = None,
    event_days: int = 30,
    metric_days: int = 90,
) -> RetentionPlan:
    reference = now or datetime.now(timezone.utc)
    return RetentionPlan(
        events_cutoff=reference - timedelta(days=event_days),
        metrics_cutoff=reference - timedelta(days=metric_days),
    )


async def run_retention(
    now: datetime | None = None,
    event_days: int = 30,
    metric_days: int = 90,
) -> dict[str, object]:
    plan = build_retention_plan(now=now, event_days=event_days, metric_days=metric_days)
    pool = get_pool()

    async with pool.acquire() as conn:
        deleted_events = await conn.fetchval(
            "DELETE FROM events WHERE event_timestamp < $1 RETURNING 1",
            plan.events_cutoff,
        )
        deleted_metrics = await conn.fetchval(
            "DELETE FROM metrics WHERE collected_at < $1 RETURNING 1",
            plan.metrics_cutoff,
        )

    result = {
        "hostname": socket.gethostname(),
        "events_cutoff": plan.events_cutoff.isoformat(),
        "metrics_cutoff": plan.metrics_cutoff.isoformat(),
        "deleted_events": int(deleted_events or 0),
        "deleted_metrics": int(deleted_metrics or 0),
    }
    logger.info(
        "[LogSentinel-Retention] %s deleted_events=%d deleted_metrics=%d",
        result["hostname"],
        result["deleted_events"],
        result["deleted_metrics"],
    )
    return result


async def _main() -> int:
    from src.database import close_db, init_db

    await init_db()
    try:
        result = await run_retention()
        print(result)
        return 0
    finally:
        await close_db()


if __name__ == "__main__":
    import asyncio

    sys.exit(asyncio.run(_main()))
