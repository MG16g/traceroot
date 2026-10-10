import asyncio
import json
import logging
import time

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request

from starlette.background import BackgroundTask
from telemetry_sender import send_telemetry

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger("monitored-app")

app = FastAPI(
    title="TraceRoot Monitored Application",
    description="Sample service monitored by TraceRoot",
    version="0.1.0",
)


@app.middleware("http")
async def transmit_telemetry(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    status_code = response.status_code

    payload = {
        "level": "ERROR" if status_code >= 500 else "INFO",
        "message": (
            f"{request.method} {request.url.path} "
            f"returned HTTP {status_code}"
        ),
        "method": request.method,
        "path": request.url.path,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }

    existing_background = response.background

    async def deliver_after_response():
        if existing_background is not None:
            await existing_background()

        await send_telemetry(
            event_type="log",
            payload=payload,
        )

    response.background = BackgroundTask(
        deliver_after_response
    )

    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response

    finally:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        log_record = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "service": "monitored-app",
            "level": (
                "ERROR"
                if status_code >= 500
                else "INFO"
            ),
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "duration_ms": duration_ms,
        }

        
        logger.log(
            logging.ERROR if status_code >= 500 else logging.INFO,
            json.dumps(log_record),
        )




@app.get("/")
def root():
    return {
        "service": "monitored-app",
        "message": "TraceRoot monitored application is running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "monitored-app",
    }


@app.get("/simulate/error")
def simulate_error():
    """
    Simulate an internal server error for TraceRoot testing.
    """
    raise HTTPException(
        status_code=500,
        detail="Simulated internal server failure",
    )



@app.get("/simulate/latency")
async def simulate_latency():
    """
    Simulate a slow API response.
    """
    await asyncio.sleep(3)

    return {
        "service": "monitored-app",
        "status": "slow",
        "message": "Simulated API latency",
        "simulated_delay_seconds": 3,
    }


@app.get("/simulate/database-error")
def simulate_database_error():
    """
    Simulate a database connection failure.

    No actual database connection is attempted.
    """
    raise HTTPException(
        status_code=503,
        detail="Simulated database connection unavailable",
    )



