from datetime import timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import IncidentModel
from app.models.telemetry_event import TelemetryEventModel


SOURCE_EVENT_TYPES = {
    "logs": "log",
    "metrics": "metric",
    "deployments": "deployment",
}


def load_live_telemetry(
    db: Session,
    source: str,
    incident_id: str,
) -> list[dict[str, Any]] | None:
    """
    Return live PostgreSQL telemetry for an automatic incident.

    None means the incident is not live-backed, so the caller
    can use the existing JSON telemetry loader.
    """

    event_type = SOURCE_EVENT_TYPES.get(source)

    if event_type is None:
        raise ValueError(f"Unsupported telemetry source: {source}")

    incident = db.get(IncidentModel, incident_id)

    if incident is None or incident.fingerprint is None:
        return None

    start_time = incident.created_at - timedelta(minutes=15)
    end_time = incident.created_at + timedelta(minutes=15)

    events = db.scalars(
        select(TelemetryEventModel)
        .where(
            TelemetryEventModel.service == incident.service,
            TelemetryEventModel.event_type == event_type,
            TelemetryEventModel.timestamp >= start_time,
            TelemetryEventModel.timestamp <= end_time,
        )
        .order_by(TelemetryEventModel.timestamp.asc())
        .limit(1000)
    ).all()

    results = []

    for event in events:
        results.append(
            {
                **event.payload,
                "service": event.service,
                "timestamp": event.timestamp.isoformat(),
            }
        )

    return results