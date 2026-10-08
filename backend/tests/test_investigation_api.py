import pytest
from unittest.mock import patch
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_db
from app.schemas.api import (
    InvestigationResponse,
    InvestigationHistoryItem,
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



@pytest.fixture(autouse=True)
def isolated_database_override():
    previous_override = app.dependency_overrides.get(get_db)

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override


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


# -------------------------------------------------------------------
# GET /api/investigations/{incident_id}/history
# -------------------------------------------------------------------


def test_get_investigation_history():

    history = [
        InvestigationHistoryItem(
            investigation_id="INV-003",
            incident_id="INC-001",
            status="completed",
            iteration=3,
            current_step="completed",
            created_at=datetime(
                2026,
                10,
                1,
                10,
                30,
                tzinfo=timezone.utc,
            ),
            root_cause_confidence=0.92,
        ),
        InvestigationHistoryItem(
            investigation_id="INV-002",
            incident_id="INC-001",
            status="completed",
            iteration=2,
            current_step="completed",
            created_at=datetime(
                2026,
                9,
                30,
                18,
                0,
                tzinfo=timezone.utc,
            ),
            root_cause_confidence=0.84,
        ),
    ]

    with patch(
        "app.api.investigations."
        "get_investigation_history",
        return_value=history,
    ) as mock_get:

        response = client.get(
            "/api/investigations/INC-001/history"
        )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2

    assert body[0]["investigation_id"] == "INV-003"
    assert body[0]["incident_id"] == "INC-001"
    assert body[0]["status"] == "completed"
    assert body[0]["iteration"] == 3
    assert body[0]["root_cause_confidence"] == 0.92

    assert body[1]["investigation_id"] == "INV-002"
    assert body[1]["root_cause_confidence"] == 0.84

    mock_get.assert_called_once_with(
        db=fake_db,
        incident_id="INC-001",
    )


def test_get_investigation_history_empty():

    with patch(
        "app.api.investigations."
        "get_investigation_history",
        return_value=[],
    ) as mock_get:

        response = client.get(
            "/api/investigations/INC-999/history"
        )

    assert response.status_code == 200
    assert response.json() == []

    mock_get.assert_called_once_with(
        db=fake_db,
        incident_id="INC-999",
    )


def test_get_investigation_run():

    historical_response = InvestigationResponse(
        incident_id="INC-001",
        status="completed",
        iteration=3,
        current_step="completed",
        executed_actions=[
            "search_logs",
            "query_metrics",
        ],
        root_cause=RootCauseResponse(
            description="Database pool exhaustion",
            supporting_evidence=["EV-001"],
            contradicting_evidence=[],
            source_types=["log"],
            confidence=0.92,
            status="supported",
        ),
        final_report="Historical RCA report",
    )

    with patch(
        "app.api.investigations."
        "get_investigation_by_id",
        return_value=historical_response,
    ) as mock_get:

        response = client.get(
            "/api/investigations/runs/INV-003"
        )

    assert response.status_code == 200

    body = response.json()

    assert body["incident_id"] == "INC-001"
    assert body["status"] == "completed"
    assert body["iteration"] == 3
    assert body["current_step"] == "completed"
    assert body["final_report"] == (
        "Historical RCA report"
    )

    assert body["root_cause"] is not None
    assert (
        body["root_cause"]["confidence"]
        == 0.92
    )

    mock_get.assert_called_once_with(
        db=fake_db,
        investigation_id="INV-003",
    )


def test_get_investigation_run_not_found():

    with patch(
        "app.api.investigations."
        "get_investigation_by_id",
        return_value=None,
    ) as mock_get:

        response = client.get(
            "/api/investigations/runs/INV-MISSING"
        )

    assert response.status_code == 404

    assert response.json() == {
        "detail":
            "Investigation INV-MISSING not found"
    }

    mock_get.assert_called_once_with(
        db=fake_db,
        investigation_id="INV-MISSING",
    )
# -------------------------------------------------------------------
# GET /api/investigations/stream/{incident_id}
# -------------------------------------------------------------------


def create_fake_stream_states():
    """
    Creates deterministic accumulated graph states for
    testing the SSE investigation endpoint without calling
    the real LangGraph/LLM pipeline.
    """

    fake_response = create_fake_investigation_response()

    return [
        {
            "current_step": "triage",
            "iteration": 0,
        },
        {
            "current_step": "action_selected",
            "iteration": 1,
        },
        {
            "current_step": "evidence_collected",
            "iteration": 1,
        },
        {
            "current_step": "hypothesis_updated",
            "iteration": 1,
        },
        {
            "current_step": "root_cause_evaluated",
            "iteration": 1,
        },
        {
            "current_step": "completed",
            "iteration": 2,
            "_fake_response": fake_response,
        },
    ]


def test_stream_investigation_incident_not_found():
    """
    Streaming endpoint should return HTTP 404 when the
    requested incident does not exist.
    """

    with patch(
        "app.api.investigations."
        "IncidentRepository.get_by_id",
        return_value=None,
    ), patch(
        "app.api.investigations.stream_investigation",
    ) as mock_stream:

        response = client.get(
            "/api/investigations/stream/INC-404"
        )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "Incident INC-404 not found"
    )

    mock_stream.assert_not_called()


def test_stream_investigation_returns_sse():
    """
    A valid streaming investigation should return an
    SSE response.
    """

    fake_incident_model = create_fake_incident_model()

    final_response = (
        create_fake_investigation_response()
    )

    stream_states = create_fake_stream_states()

    with patch(
        "app.api.investigations."
        "IncidentRepository.get_by_id",
        return_value=fake_incident_model,
    ), patch(
        "app.api.investigations.stream_investigation",
        return_value=iter(stream_states),
    ), patch(
        "app.api.investigations."
        "build_investigation_response",
        return_value=final_response,
    ), patch(
        "app.api.investigations.persist_investigation",
    ):

        response = client.get(
            "/api/investigations/stream/INC-001"
        )

    assert response.status_code == 200

    assert (
        "text/event-stream"
        in response.headers["content-type"]
    )


def test_stream_investigation_emits_progress():
    """
    Streaming endpoint should emit started and progress
    events while the graph executes.
    """

    fake_incident_model = create_fake_incident_model()

    final_response = (
        create_fake_investigation_response()
    )

    stream_states = create_fake_stream_states()

    with patch(
        "app.api.investigations."
        "IncidentRepository.get_by_id",
        return_value=fake_incident_model,
    ), patch(
        "app.api.investigations.stream_investigation",
        return_value=iter(stream_states),
    ), patch(
        "app.api.investigations."
        "build_investigation_response",
        return_value=final_response,
    ), patch(
        "app.api.investigations.persist_investigation",
    ):

        response = client.get(
            "/api/investigations/stream/INC-001"
        )

    body = response.text

    assert "event: started" in body
    assert "event: progress" in body

    assert '"step": "action_selected"' in body
    assert '"step": "evidence_collected"' in body
    assert '"step": "hypothesis_updated"' in body

    assert (
        '"step": "root_cause_evaluated"'
        in body
    )


def test_stream_investigation_emits_completed_response():
    """
    Successful stream should finish with a completed
    event containing the public InvestigationResponse.
    """

    fake_incident_model = create_fake_incident_model()

    final_response = (
        create_fake_investigation_response()
    )

    stream_states = create_fake_stream_states()

    with patch(
        "app.api.investigations."
        "IncidentRepository.get_by_id",
        return_value=fake_incident_model,
    ), patch(
        "app.api.investigations.stream_investigation",
        return_value=iter(stream_states),
    ), patch(
        "app.api.investigations."
        "build_investigation_response",
        return_value=final_response,
    ), patch(
        "app.api.investigations.persist_investigation",
    ):

        response = client.get(
            "/api/investigations/stream/INC-001"
        )

    body = response.text

    assert "event: completed" in body

    assert '"incident_id": "INC-001"' in body
    assert '"status": "completed"' in body
    assert '"confidence": 0.9' in body

    assert "Incident Summary" in body


def test_stream_investigation_persists_once():
    """
    Successful streamed investigation should persist the
    final response exactly once.
    """

    fake_incident_model = create_fake_incident_model()

    final_response = (
        create_fake_investigation_response()
    )

    stream_states = create_fake_stream_states()

    with patch(
        "app.api.investigations."
        "IncidentRepository.get_by_id",
        return_value=fake_incident_model,
    ), patch(
        "app.api.investigations.stream_investigation",
        return_value=iter(stream_states),
    ), patch(
        "app.api.investigations."
        "build_investigation_response",
        return_value=final_response,
    ), patch(
        "app.api.investigations.persist_investigation",
    ) as mock_persist:

        response = client.get(
            "/api/investigations/stream/INC-001"
        )

    assert response.status_code == 200

    mock_persist.assert_called_once()

    call = mock_persist.call_args

    assert call.kwargs["db"] is fake_db

    assert (
        call.kwargs["response"]
        == final_response
    )


def test_stream_investigation_emits_investigation_error():
    """
    If graph execution fails after the SSE connection
    starts, the API should emit investigation_error and
    must not persist a result.
    """

    fake_incident_model = create_fake_incident_model()

    def failing_stream(_incident):
        yield {
            "current_step": "action_selected",
            "iteration": 1,
        }

        raise RuntimeError(
            "Simulated investigation failure"
        )

    with patch(
        "app.api.investigations."
        "IncidentRepository.get_by_id",
        return_value=fake_incident_model,
    ), patch(
        "app.api.investigations.stream_investigation",
        side_effect=failing_stream,
    ), patch(
        "app.api.investigations.persist_investigation",
    ) as mock_persist:

        response = client.get(
            "/api/investigations/stream/INC-001"
        )

    assert response.status_code == 200

    body = response.text

    assert "event: started" in body
    assert "event: progress" in body

    assert (
        "event: investigation_error"
        in body
    )

    assert (
        "Simulated investigation failure"
        in body
    )

    assert "event: completed" not in body

    mock_persist.assert_not_called()


# -------------------------------------------------------------------
# GET /api/investigations/compare/{baseline_id}/{comparison_id}
# -------------------------------------------------------------------


def test_compare_investigations():

    comparison_result = {
        "incident_id": "INC-001",
        "baseline_investigation_id": "INV-001",
        "comparison_investigation_id": "INV-002",
        "baseline_confidence": 0.70,
        "comparison_confidence": 0.90,
        "confidence_change": 0.20,
        "baseline_evidence_count": 1,
        "comparison_evidence_count": 3,
        "evidence_count_change": 2,
        "baseline_hypothesis_count": 1,
        "comparison_hypothesis_count": 2,
        "hypothesis_count_change": 1,
    }

    with patch(
        "app.api.investigations."
        "compare_investigations",
        return_value=comparison_result,
    ) as mock_compare:

        response = client.get(
            "/api/investigations/compare/"
            "INV-001/INV-002"
        )

    assert response.status_code == 200

    body = response.json()

    assert body["incident_id"] == "INC-001"

    assert (
        body["baseline_investigation_id"]
        == "INV-001"
    )

    assert (
        body["comparison_investigation_id"]
        == "INV-002"
    )

    assert body["baseline_confidence"] == 0.70
    assert body["comparison_confidence"] == 0.90

    assert body["confidence_change"] == 0.20

    assert body["baseline_evidence_count"] == 1
    assert body["comparison_evidence_count"] == 3
    assert body["evidence_count_change"] == 2

    assert body["baseline_hypothesis_count"] == 1
    assert body["comparison_hypothesis_count"] == 2
    assert body["hypothesis_count_change"] == 1

    mock_compare.assert_called_once_with(
        db=fake_db,
        baseline_investigation_id="INV-001",
        comparison_investigation_id="INV-002",
    )


def test_compare_investigations_not_found():

    with patch(
        "app.api.investigations."
        "compare_investigations",
        return_value=None,
    ) as mock_compare:

        response = client.get(
            "/api/investigations/compare/"
            "INV-MISSING/INV-002"
        )

    assert response.status_code == 404

    assert "detail" in response.json()

    mock_compare.assert_called_once_with(
        db=fake_db,
        baseline_investigation_id="INV-MISSING",
        comparison_investigation_id="INV-002",
    )


def test_compare_investigations_different_incidents():

    with patch(
        "app.api.investigations."
        "compare_investigations",
        side_effect=ValueError(
            "Investigations belong to different incidents"
        ),
    ) as mock_compare:

        response = client.get(
            "/api/investigations/compare/"
            "INV-001/INV-OTHER"
        )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == "Investigations belong to different incidents"
    )

    mock_compare.assert_called_once_with(
        db=fake_db,
        baseline_investigation_id="INV-001",
        comparison_investigation_id="INV-OTHER",
    )


def test_get_investigation_rca_report():

    report = {
        "investigation_id": "INV-RCA-001",
        "incident_id": "INC-001",
        "created_at": "2026-10-02T10:00:00Z",

        "investigation_status": "completed",
        "iteration": 3,
        "current_step": "completed",

        "root_cause_description": (
            "Database connection pool exhaustion"
        ),
        "root_cause_status": "supported",
        "root_cause_confidence": 0.9,

        "evidence_count": 1,
        "hypothesis_count": 1,
        "action_count": 2,

        "supporting_evidence": [
            "EV-001",
        ],
        "contradicting_evidence": [],

        "source_types": [
            "log",
        ],

        "evidence": [
            {
                "id": "EV-001",
                "source_type": "log",
                "service": "payment-service",
                "content": (
                    "Database connection timeout"
                ),
                "relevance_score": 0.95,
            }
        ],

        "executed_actions": [
            "search_logs",
            "query_metrics",
        ],

        "final_report": (
            "# Incident Summary\n"
            "Payment failures increased."
        ),

        "error": None,
    }

    with patch(
        "app.api.investigations."
        "get_rca_report",
        return_value=report,
    ) as mock_report:

        response = client.get(
            "/api/investigations/runs/"
            "INV-RCA-001/report"
        )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["investigation_id"]
        == "INV-RCA-001"
    )

    assert data["incident_id"] == "INC-001"

    assert (
        data["root_cause_status"]
        == "supported"
    )

    assert (
        data["root_cause_confidence"]
        == 0.9
    )

    assert data["evidence_count"] == 1
    assert data["hypothesis_count"] == 1
    assert data["action_count"] == 2

    assert len(data["evidence"]) == 1

    mock_report.assert_called_once_with(
        db=fake_db,
        investigation_id="INV-RCA-001",
    )


def test_get_investigation_rca_report_not_found():

    with patch(
        "app.api.investigations."
        "get_rca_report",
        return_value=None,
    ) as mock_report:

        response = client.get(
            "/api/investigations/runs/"
            "INV-MISSING/report"
        )

    assert response.status_code == 404

    data = response.json()

    assert "detail" in data

    assert (
        "INV-MISSING"
        in data["detail"]
    )

    mock_report.assert_called_once_with(
        db=fake_db,
        investigation_id="INV-MISSING",
    )