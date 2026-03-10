import logging

import asyncpg

from src.config import DATABASE_URL
from src.db import SCHEMA_SQL, parse_payload

logger = logging.getLogger(__name__)

pool: asyncpg.Pool | None = None


async def init_db() -> None:
    global pool
    if pool is not None:
        return

    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=4)
    async with pool.acquire() as conn:
        await conn.execute(SCHEMA_SQL)
    logger.info("Database initialized")


async def close_db() -> None:
    global pool
    if pool is not None:
        await pool.close()
        pool = None


async def upsert_machine(conn: asyncpg.Connection, hostname: str) -> None:
    await conn.execute(
        """
        INSERT INTO machines (hostname, first_seen, last_seen)
        VALUES ($1, NOW(), NOW())
        ON CONFLICT (hostname) DO UPDATE SET last_seen = NOW()
        """,
        hostname,
    )


async def store_payload_db(payload_dict: dict) -> None:
    if pool is None:
        raise RuntimeError("database pool is not initialized")

    events, metric = parse_payload(payload_dict)

    async with pool.acquire() as conn:
        async with conn.transaction():
            await upsert_machine(conn, payload_dict["hostname"])

            for event in events:
                await conn.execute(
                    """
                    INSERT INTO events (hostname, source, event_id, level, message, event_timestamp, collected_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                    event.hostname,
                    event.source,
                    event.event_id,
                    event.level,
                    event.message,
                    event.timestamp,
                    event.collected_at,
                )

            await conn.execute(
                """
                INSERT INTO metrics (
                    hostname,
                    cpu_percent,
                    ram_available_mb,
                    disk_free_percent,
                    uptime_hours,
                    reliability_index,
                    bsod_detected,
                    collected_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                metric.hostname,
                metric.cpu_percent,
                metric.ram_available_mb,
                metric.disk_free_percent,
                metric.uptime_hours,
                metric.reliability_index,
                metric.bsod_detected,
                metric.collected_at,
            )

    logger.info("Stored %d events and metrics for %s", len(events), payload_dict["hostname"])
