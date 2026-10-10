from typing import Any

from fastapi import APIRouter, HTTPException

from app.tools.exceptions import (
    TelemetryNotFoundError,
    TelemetryParseError,
)
from app.tools.telemetry_catalog import (
    get_telemetry_catalog,
)
from app.tools.telemetry_loader import (
    load_telemetry,
)

from fastapi import Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.telemetry_auth import require_telemetry_api_key
from app.repositories.telemetry_repository import TelemetryRepository
from app.schemas.telemetry_ingest import (
    TelemetryIngestRequest,
    TelemetryIngestResponse,
)


router = APIRouter(
    prefix="/api/telemetry",
    tags=["Telemetry"],
)


def _load_source(
    source: str,
    incident_id: str,
) -> list[dict[str, Any]]:
    """
    Load a telemetry source for the API.

    Missing telemetry is represented as an empty list so
    one unavailable source does not prevent the remaining
    telemetry from being inspected.
    """
    try:
        return load_telemetry(
            source=source,
            incident_id=incident_id,
        )
    except TelemetryNotFoundError:
        return []
    except TelemetryParseError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get("/{incident_id}")
def get_incident_telemetry(
    incident_id: str,
) -> dict[str, Any]:
    """
    Return all telemetry available for an incident.
    """

    logs = _load_source(
        source="logs",
        incident_id=incident_id,
    )

    metrics = _load_source(
        source="metrics",
        incident_id=incident_id,
    )

    deployments = _load_source(
        source="deployments",
        incident_id=incident_id,
    )

    if (
        not logs
        and not metrics
        and not deployments
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                "No telemetry found for incident "
                f"{incident_id}"
            ),
        )

    catalog = get_telemetry_catalog(
        incident_id,
    )

    return {
        "incident_id": incident_id,
        "catalog": catalog,
        "counts": {
            "logs": len(logs),
            "metrics": len(metrics),
            "deployments": len(
                deployments,
            ),
        },
        "logs": logs,
        "metrics": metrics,
        "deployments": deployments,
    }


@router.post(
    "/ingest",
    response_model=TelemetryIngestResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_telemetry_api_key)],
)
def ingest_telemetry(
    event: TelemetryIngestRequest,
    db: Session = Depends(get_db),
) -> TelemetryIngestResponse:
    """
    Accept authenticated telemetry events and persist them
    to PostgreSQL.
    """
    try:
        repository = TelemetryRepository(db)
        saved_event = repository.create(event)

        event_id = saved_event.id

        db.commit()

        return TelemetryIngestResponse(
            event_id=event_id,
            status="accepted",
        )

    except Exception:
        db.rollback()
        raise