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