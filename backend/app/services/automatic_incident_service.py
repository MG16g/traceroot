from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import IncidentModel
from app.schemas.telemetry_ingest import TelemetryIngestRequest
from app.services.incident_detector import detect_incident


def process_telemetry_incident(
    db: Session,
    event: TelemetryIngestRequest,
) -> IncidentModel | None:
    """
    Detect an incident from telemetry and create it if needed.

    The caller owns the transaction and must commit or roll back.
    """

    detection = detect_incident(event)

    if detection is None:
        return None

    # Serialize creation attempts for the same fingerprint.
    # PostgreSQL releases this transaction-scoped lock at commit/rollback.
    db.execute(
        select(
            __import__("sqlalchemy").func.pg_advisory_xact_lock(
                __import__("sqlalchemy").func.hashtextextended(
                    detection.fingerprint,
                    0,
                )
            )
        )
    )

    existing = db.scalar(
        select(IncidentModel)
        .where(
            IncidentModel.fingerprint == detection.fingerprint,
            IncidentModel.status.in_(["open", "investigating"]),
        )
        .limit(1)
    )

    if existing is not None:
        return existing

    # Generate a numeric ID that matches the existing schema.
    # The UUID-derived number makes collisions extremely unlikely.
    incident_id = f"INC-{uuid4().int}"

    incident = IncidentModel(
        id=incident_id,
        title=detection.title,
        description=detection.description,
        service=detection.service,
        severity=detection.severity,
        status="open",
        fingerprint=detection.fingerprint,
        created_at=datetime.now(timezone.utc),
    )

    db.add(incident)
    db.flush()

    return incident