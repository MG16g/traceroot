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


def test_missing_telemetry_raises_error(monkeypatch):
    import app.tools.telemetry_loader as loader

    # Simulate an incident with no live telemetry.
    # This keeps the test independent of PostgreSQL.
    monkeypatch.setattr(
        loader,
        "load_live_telemetry",
        lambda db, source, incident_id: None,
    )

    with pytest.raises(TelemetryNotFoundError):
        load_telemetry(
            source="logs",
            incident_id="INC-DOES-NOT-EXIST",
        )