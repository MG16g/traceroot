import json
from pathlib import Path
from typing import Any

from app.tools.exceptions import (
    TelemetryNotFoundError,
    TelemetryParseError,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def load_telemetry(
    source: str,
    incident_id: str,
) -> list[dict[str, Any]]:
    file_path = DATA_DIR / source / f"{incident_id}.json"

    if not file_path.exists():
        raise TelemetryNotFoundError(
            f"No {source} telemetry found for incident {incident_id}"
        )

    try:
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
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