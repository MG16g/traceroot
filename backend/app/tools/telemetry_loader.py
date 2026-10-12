
import json
from pathlib import Path
from typing import Any

from app.core.database import SessionLocal
from app.tools.exceptions import (
    TelemetryNotFoundError,
    TelemetryParseError,
)
from app.tools.live_telemetry import load_live_telemetry


BACKEND_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_ROOT / "data"


def load_telemetry(
    source: str,
    incident_id: str,
) -> list[dict[str, Any]]:
    file_path = DATA_DIR / source / f"{incident_id}.json"

    # Preserve existing JSON-backed incidents.
    if file_path.exists():
        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise TelemetryParseError(
                f"Invalid JSON in {file_path}"
            ) from exc

        if not isinstance(data, list):
            raise TelemetryParseError(
                f"Expected a list of telemetry records in {file_path}"
            )

        return data

    # Retrieve PostgreSQL telemetry for newly detected incidents.
    with SessionLocal() as db:
        live_records = load_live_telemetry(
            db=db,
            source=source,
            incident_id=incident_id,
        )

    if live_records is not None:
        return live_records

    raise TelemetryNotFoundError(
        f"No {source} telemetry found for incident {incident_id}"
    )
