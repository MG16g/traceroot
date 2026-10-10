import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from telemetry_config import (
    TELEMETRY_ENABLED,
    TRACEROOT_INGEST_URL,
    TRACEROOT_TELEMETRY_API_KEY,
)


logger = logging.getLogger("monitored-app.telemetry")


async def send_telemetry(
    event_type: str,
    payload: dict[str, Any],
    service: str = "monitored-app",
    timestamp: datetime | None = None,
) -> bool:
    """
    Send one telemetry event to TraceRoot.

    Returns True on successful ingestion.
    Returns False if telemetry is disabled or delivery fails.
    """

    if not TELEMETRY_ENABLED:
        return False

    if not TRACEROOT_TELEMETRY_API_KEY:
        logger.warning(
            "Telemetry delivery skipped: API key is not configured"
        )
        return False

    event_timestamp = timestamp or datetime.now(timezone.utc)

    event = {
        "service": service,
        "event_type": event_type,
        "timestamp": event_timestamp.isoformat(),
        "payload": payload,
    }

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(3.0),
        ) as client:
            response = await client.post(
                TRACEROOT_INGEST_URL,
                json=event,
                headers={
                    "X-Telemetry-API-Key": (
                        TRACEROOT_TELEMETRY_API_KEY
                    ),
                },
            )

            response.raise_for_status()

            if response.status_code != 201:
                logger.warning(
                    "Unexpected telemetry response status: %s",
                    response.status_code,
                )
                return False

            return True

    except httpx.HTTPError as exc:
        logger.warning(
            "Telemetry delivery failed: %s",
            type(exc).__name__,
        )
        return False