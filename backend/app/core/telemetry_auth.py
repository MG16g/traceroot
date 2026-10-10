import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings


telemetry_api_key_header = APIKeyHeader(
    name="X-Telemetry-API-Key",
    auto_error=False,
)


def require_telemetry_api_key(
    provided_key: str | None = Security(
        telemetry_api_key_header,
    ),
) -> None:
    configured_key = settings.telemetry_api_key

    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telemetry ingestion is not configured",
        )

    if (
        provided_key is None
        or not secrets.compare_digest(
            provided_key,
            configured_key,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid telemetry API key",
            headers={"WWW-Authenticate": "APIKey"},
        )