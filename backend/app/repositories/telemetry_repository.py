from sqlalchemy.orm import Session

from app.models.telemetry_event import TelemetryEventModel
from app.schemas.telemetry_ingest import TelemetryIngestRequest


class TelemetryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        event: TelemetryIngestRequest,
    ) -> TelemetryEventModel:
        telemetry_event = TelemetryEventModel(
            service=event.service,
            event_type=event.event_type,
            timestamp=event.timestamp,
            payload=event.payload,
        )

        self.db.add(telemetry_event)
        self.db.flush()

        return telemetry_event