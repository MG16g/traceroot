import pytest

from app.tools.exceptions import TelemetryNotFoundError
from app.tools.telemetry_loader import load_telemetry


def test_load_logs_for_existing_incident():
    logs = load_telemetry(
        source="logs",
        incident_id="INC-001",
    )

    assert isinstance(logs, list)
    assert len(logs) > 0
    assert logs[0]["service"]


def test_missing_telemetry_raises_error():
    with pytest.raises(TelemetryNotFoundError):
        load_telemetry(
            source="logs",
            incident_id="INC-DOES-NOT-EXIST",
        )