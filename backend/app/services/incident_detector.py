from dataclasses import dataclass

from app.schemas.telemetry_ingest import TelemetryIngestRequest


@dataclass(frozen=True)
class IncidentDetection:
    title: str
    description: str
    service: str
    severity: str
    fingerprint: str


def detect_incident(
    event: TelemetryIngestRequest,
) -> IncidentDetection | None:
    """
    Identify incident-worthy HTTP errors.

    This function evaluates telemetry only.
    It does not access or modify the database.
    """

    if event.event_type != "log":
        return None

    status_code = event.payload.get("status_code")

    if (
        isinstance(status_code, bool)
        or not isinstance(status_code, int)
        or not 500 <= status_code <= 599
    ):
        return None

    path = event.payload.get("path", "unknown")

    if not isinstance(path, str) or not path.strip():
        path = "unknown"

    path = path.strip()

    return IncidentDetection(
        title=f"HTTP {status_code} failure in {event.service}",
        description=(
            f"Service {event.service} returned HTTP {status_code} "
            f"for endpoint {path}."
        ),
        service=event.service,
        severity="high",
        fingerprint=f"{event.service}:http:{status_code}:{path}",
    )