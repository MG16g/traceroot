from unittest.mock import patch
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_db
from app.schemas.api import (
    InvestigationResponse,
    RootCauseResponse,
)


# -------------------------------------------------------------------
# Fake database dependency
# -------------------------------------------------------------------

class FakeDB:
    pass


fake_db = FakeDB()


def override_get_db():
    yield fake_db


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def create_fake_incident_model():
    """
    Creates a lightweight object that behaves like the
    SQLAlchemy IncidentModel expected by the API.
    """

    class FakeIncidentModel:
        id = "INC-001"
        title = "Checkout payment failures"
        description = (
            "Payment failures increased after deployment"
        )
        service = "payment-service"
        severity = "critical"
        status = "open"

        created_at = datetime(
            2026,
            9,
            18,
            14,
            0,
            0,
            tzinfo=timezone.utc,
        )

    return FakeIncidentModel()


def create_fake_investigation_response():
    """
    Creates the response returned by the mocked
    investigation service.
    """

    return InvestigationResponse(
        incident_id="INC-001",
        status="completed",
        iteration=2,
        current_step="completed",
        executed_actions=[
            "search_logs|level=ERROR,service=payment-service",
            (
                "query_metrics|"
                "metric=db_connection_utilization,"
                "service=payment-service"
            ),
        ],
        root_cause=RootCauseResponse(
            description=(
                "Database connection pool exhaustion "
                "caused payment failures"
            ),
            supporting_evidence=[
                "EV-001",
                "EV-002",
            ],
            contradicting_evidence=[],
            source_types=[
                "log",
                "metric",
            ],
            confidence=0.9,
            status="supported",
        ),
        final_report=(
            "# Incident Summary\n\n"
            "Payment failures were caused by database "
            "connection pool exhaustion.\n\n"
            "# Recommended Next Steps\n\n"
            "Review database connection pool capacity."
        ),
        error=None,
    )


# -------------------------------------------------------------------
# POST /api/investigations
# -------------------------------------------------------------------

def test_create_investigation():
    """
    A valid incident should trigger the investigation
    service and persist the completed result.
    """

    fake_incident_model = create_fake_incident_model()
    fake_response = create_fake_investigation_response()

    with patch(
        "app.api.investigations."
        "IncidentRepository.get_by_id",
        return_value=fake_incident_model,
    ) as mock_get_incident, patch(
        "app.api.investigations.run_investigation",
        return_value=fake_response,
    ) as mock_run, patch(
        "app.api.investigations.persist_investigation",
    ) as mock_persist:

        response = client.post(
            "/api/investigations",
            json={
                "incident_id": "INC-001",
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert body["incident_id"] == "INC-001"
    assert body["status"] == "completed"
    assert body["iteration"] == 2
    assert body["current_step"] == "completed"

    assert len(body["executed_actions"]) == 2

    assert body["root_cause"] is not None

    assert (
        body["root_cause"]["description"]
        == (
            "Database connection pool exhaustion "
            "caused payment failures"
        )
    )

    assert body["root_cause"]["confidence"] == 0.9
    assert body["root_cause"]["status"] == "supported"

    assert (
        "Incident Summary"
        in body["final_report"]
    )

    # Verify incident lookup.
    mock_get_incident.assert_called_once_with(
        "INC-001"
    )

    # Verify investigation engine was called.
    mock_run.assert_called_once()

    # Verify result persistence was called.
    mock_persist.assert_called_once()

    persist_call = mock_persist.call_args

    assert (
        persist_call.kwargs["response"]
        == fake_response
    )

    assert (
        persist_call.kwargs["db"]
        is fake_db
    )


# -------------------------------------------------------------------
# Incident does not exist
# -------------------------------------------------------------------

def test_create_investigation_incident_not_found():
    """
    The API should return HTTP 404 when the requested
    incident does not exist.
    """

    with patch(
        "app.api.investigations."
        "IncidentRepository.get_by_id",
        return_value=None,
    ), patch(
        "app.api.investigations.run_investigation",
    ) as mock_run, patch(
        "app.api.investigations.persist_investigation",
    ) as mock_persist:

        response = client.post(
            "/api/investigations",
            json={
                "incident_id": "INC-404",
            },
        )

    assert response.status_code == 404

    body = response.json()

    assert "detail" in body

    mock_run.assert_not_called()
    mock_persist.assert_not_called()


# -------------------------------------------------------------------
# Request validation
# -------------------------------------------------------------------

def test_create_investigation_missing_incident_id():
    """
    FastAPI/Pydantic should reject requests that do not
    contain the required incident_id.
    """

    response = client.post(
        "/api/investigations",
        json={},
    )

    assert response.status_code == 422


# -------------------------------------------------------------------
# Investigation result contains expected RCA structure
# -------------------------------------------------------------------

def test_create_investigation_returns_root_cause():
    """
    Ensure that the public API exposes the deterministic
    root-cause evaluation produced by TraceRoot.
    """

    fake_incident_model = create_fake_incident_model()
    fake_response = create_fake_investigation_response()

    with patch(
        "app.api.investigations."
        "IncidentRepository.get_by_id",
        return_value=fake_incident_model,
    ), patch(
        "app.api.investigations.run_investigation",
        return_value=fake_response,
    ), patch(
        "app.api.investigations.persist_investigation",
    ):

        response = client.post(
            "/api/investigations",
            json={
                "incident_id": "INC-001",
            },
        )

    assert response.status_code == 200

    body = response.json()

    root_cause = body["root_cause"]

    assert root_cause is not None

    assert (
        root_cause["description"]
        == (
            "Database connection pool exhaustion "
            "caused payment failures"
        )
    )

    assert root_cause["confidence"] == 0.9

    assert root_cause["status"] == "supported"

    assert root_cause["source_types"] == [
        "log",
        "metric",
    ]

    assert root_cause["supporting_evidence"] == [
        "EV-001",
        "EV-002",
    ]

    assert root_cause["contradicting_evidence"] == []


# -------------------------------------------------------------------
# Persistence receives the exact investigation response
# -------------------------------------------------------------------

def test_completed_investigation_is_persisted():
    """
    The API layer should persist exactly the response
    generated by the investigation service.
    """

    fake_incident_model = create_fake_incident_model()
    fake_response = create_fake_investigation_response()

    with patch(
        "app.api.investigations."
        "IncidentRepository.get_by_id",
        return_value=fake_incident_model,
    ), patch(
        "app.api.investigations.run_investigation",
        return_value=fake_response,
    ), patch(
        "app.api.investigations.persist_investigation",
    ) as mock_persist:

        response = client.post(
            "/api/investigations",
            json={
                "incident_id": "INC-001",
            },
        )

    assert response.status_code == 200

    mock_persist.assert_called_once()

    call = mock_persist.call_args

    assert call.kwargs["db"] is fake_db
    assert call.kwargs["response"] == fake_response


def test_get_latest_investigation():

    fake_response = (
        create_fake_investigation_response()
    )

    with patch(
        "app.api.investigations."
        "get_latest_investigation",
        return_value=fake_response,
    ) as mock_get:

        response = client.get(
            "/api/investigations/INC-001"
        )

    assert response.status_code == 200

    body = response.json()

    assert body["incident_id"] == "INC-001"
    assert body["status"] == "completed"

    assert body["root_cause"] is not None

    assert (
        body["root_cause"]["confidence"]
        == 0.9
    )

    assert (
        "Incident Summary"
        in body["final_report"]
    )

    mock_get.assert_called_once_with(
        db=fake_db,
        incident_id="INC-001",
    )


def test_get_latest_investigation_not_found():

    with patch(
        "app.api.investigations."
        "get_latest_investigation",
        return_value=None,
    ):

        response = client.get(
            "/api/investigations/INC-404"
        )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == (
            "No investigation found for "
            "incident INC-404"
        )
    )