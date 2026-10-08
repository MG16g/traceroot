from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, OperationalError

from app.main import app
from app.core.dependencies import get_db
from app.repositories.incident_repository import IncidentRepository


class FakeDB:
    pass


@pytest.fixture
def client():
    previous_override = app.dependency_overrides.get(get_db)

    def override_get_db():
        yield FakeDB()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override


def make_incident(
    incident_id="INC-9001",
    status="open",
):
    from app.models.incident import IncidentModel

    return IncidentModel(
        id=incident_id,
        title="Payment service failures",
        description="Checkout payments are failing.",
        service="payment-service",
        severity="critical",
        status=status,
        created_at=datetime(
            2026, 10, 8, tzinfo=timezone.utc
        ),
    )

def fake_create_incident(incident):
    incident.created_at = datetime.now(timezone.utc)
    return incident

def valid_payload():
    return {
        "id": "INC-9001",
        "title": "Payment service failures",
        "description": "Checkout payments are failing.",
        "service": "payment-service",
        "severity": "critical",
    }


def test_create_incident_success(client):
    with patch.object(
        IncidentRepository,
        "get_by_id",
        return_value=None,
    ), patch.object(
        IncidentRepository,
        "create",
        side_effect=fake_create_incident,
    ):
        response = client.post(
            "/api/incidents",
            json=valid_payload(),
        )

    assert response.status_code == 201
    assert response.json()["id"] == "INC-9001"
    assert response.json()["status"] == "open"


def test_duplicate_incident_returns_409(client):
    with patch.object(
        IncidentRepository,
        "get_by_id",
        return_value=make_incident(),
    ):
        response = client.post(
            "/api/incidents",
            json=valid_payload(),
        )

    assert response.status_code == 409


@pytest.mark.parametrize(
    "incident_id",
    ["INVALID", "INC-ABC", "INC-"],
)
def test_invalid_incident_id_returns_422(
    client,
    incident_id,
):
    payload = valid_payload()
    payload["id"] = incident_id

    response = client.post(
        "/api/incidents",
        json=payload,
    )

    assert response.status_code == 422


def test_whitespace_title_returns_422(client):
    payload = valid_payload()
    payload["title"] = "   "

    response = client.post(
        "/api/incidents",
        json=payload,
    )

    assert response.status_code == 422


def test_initial_status_is_always_open(client):
    payload = valid_payload()
    payload["status"] = "resolved"

    with patch.object(
        IncidentRepository,
        "get_by_id",
        return_value=None,
    ), patch.object(
        IncidentRepository,
        "create",
        side_effect=fake_create_incident,
    ):
        response = client.post(
            "/api/incidents",
            json=payload,
        )

    assert response.status_code == 201
    assert response.json()["status"] == "open"


@pytest.mark.parametrize(
    "current_status,next_status",
    [
        ("open", "investigating"),
        ("investigating", "resolved"),
    ],
)
def test_valid_status_transition(
    client,
    current_status,
    next_status,
):
    incident = make_incident(status=current_status)

    def fake_update_status(record, status):
        record.status = status
        return record

    with patch.object(
        IncidentRepository,
        "get_by_id",
        return_value=incident,
    ), patch.object(
        IncidentRepository,
        "update_status",
        side_effect=fake_update_status,
    ):
        response = client.patch(
            "/api/incidents/INC-9001/status",
            json={"status": next_status},
        )

    assert response.status_code == 200
    assert response.json()["status"] == next_status


@pytest.mark.parametrize(
    "current_status,next_status",
    [
        ("open", "resolved"),
        ("investigating", "open"),
        ("resolved", "open"),
        ("resolved", "investigating"),
    ],
)
def test_invalid_status_transition(
    client,
    current_status,
    next_status,
):
    incident = make_incident(status=current_status)

    with patch.object(
        IncidentRepository,
        "get_by_id",
        return_value=incident,
    ), patch.object(
        IncidentRepository,
        "update_status",
    ) as update_mock:
        response = client.patch(
            "/api/incidents/INC-9001/status",
            json={"status": next_status},
        )

    assert response.status_code == 409
    update_mock.assert_not_called()


def test_same_status_is_idempotent(client):
    incident = make_incident(status="open")

    with patch.object(
        IncidentRepository,
        "get_by_id",
        return_value=incident,
    ), patch.object(
        IncidentRepository,
        "update_status",
    ) as update_mock:
        response = client.patch(
            "/api/incidents/INC-9001/status",
            json={"status": "open"},
        )

    assert response.status_code == 200
    update_mock.assert_not_called()


def test_missing_incident_returns_404(client):
    with patch.object(
        IncidentRepository,
        "get_by_id",
        return_value=None,
    ):
        response = client.get(
            "/api/incidents/INC-9999"
        )

    assert response.status_code == 404


def test_database_integrity_error_returns_409(client):
    error = IntegrityError(
        "INSERT INTO incidents",
        {},
        Exception("duplicate key"),
    )

    with patch.object(
        IncidentRepository,
        "get_by_id",
        return_value=None,
    ), patch.object(
        IncidentRepository,
        "create",
        side_effect=error,
    ):
        response = client.post(
            "/api/incidents",
            json=valid_payload(),
        )

    assert response.status_code == 409


def test_database_unavailable_returns_503(client):
    error = OperationalError(
        "SELECT * FROM incidents",
        {},
        Exception("database unavailable"),
    )

    with patch.object(
        IncidentRepository,
        "get_all",
        side_effect=error,
    ):
        response = client.get("/api/incidents")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database service is temporarily unavailable."
    }