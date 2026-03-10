import logging
import socket
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

from src.config import API_SHARED_TOKEN
from src.database import close_db, init_db, store_payload_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [LogSentinel-API] %(message)s")
logger = logging.getLogger(__name__)


class EventIn(BaseModel):
    source: str
    event_id: int
    level: str
    message: str = ""
    timestamp: str


class MetricsIn(BaseModel):
    cpu_percent: float = 0
    ram_available_mb: float = 0
    disk_free_percent: float = 0
    uptime_hours: float = 0
    reliability_index: float = -1


class PayloadIn(BaseModel):
    hostname: str
    collected_at: str
    events: list[EventIn] = Field(default_factory=list)
    metrics: MetricsIn = Field(default_factory=MetricsIn)
    bsod_detected: bool = False


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    try:
        yield
    finally:
        await close_db()


app = FastAPI(title="Log Sentinel API", version="1.0.0", lifespan=lifespan)


def verify_token(authorization: Annotated[str | None, Header()] = None) -> None:
    if not API_SHARED_TOKEN:
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = authorization.removeprefix("Bearer ").strip()
    if token != API_SHARED_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )


async def store_payload(payload_dict: dict) -> None:
    await store_payload_db(payload_dict)


@app.post("/api/v1/events", dependencies=[Depends(verify_token)])
async def ingest_events(payload: PayloadIn) -> dict:
    payload_dict = payload.model_dump()

    try:
        await store_payload(payload_dict)
    except Exception as exc:
        logger.error("Store error for %s: %s", payload.hostname, exc)
        raise HTTPException(status_code=500, detail="Storage error") from exc

    logger.info("Ingested %d events from %s", len(payload.events), payload.hostname)
    return {
        "success": True,
        "hostname": payload.hostname,
        "events_count": len(payload.events),
    }


@app.get("/api/v1/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "hostname": socket.gethostname(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
