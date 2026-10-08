import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api.incidents import router as incidents_router
from app.api.investigations import (
    router as investigations_router,
)
from app.api.telemetry import router as telemetry_router

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import engine

from app.core.exception_handlers import (
    database_exception_handler,
)



app = FastAPI(
    title="TraceRoot API",
    description="Agentic AI Incident Investigation Platform",
    version="0.1.0",
)

app.add_exception_handler(
    SQLAlchemyError,
    database_exception_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

app.include_router(incidents_router)
app.include_router(investigations_router)
app.include_router(telemetry_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "traceroot-api",
    }


logger = logging.getLogger(__name__)


@app.get("/ready")
def readiness_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "service": "traceroot-api",
            "database": "connected",
        }

    except SQLAlchemyError:
        logger.exception(
            "PostgreSQL readiness check failed."
        )

        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "traceroot-api",
                "database": "unavailable",
            },
        )