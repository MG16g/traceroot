import pytest
from pydantic import ValidationError

from app.schemas.api import (
    InvestigationRequest,
    InvestigationResponse,
    RootCauseResponse,
)


def test_investigation_request():
    request = InvestigationRequest(
        incident_id="INC-001"
    )

    assert request.incident_id == "INC-001"


def test_investigation_request_rejects_empty_id():
    with pytest.raises(ValidationError):
        InvestigationRequest(
            incident_id=""
        )


def test_root_cause_response():
    root_cause = RootCauseResponse(
        description=(
            "Database connection pool exhaustion "
            "caused payment failures"
        ),
        supporting_evidence=[
            "Evidence #1",
            "Evidence #2",
        ],
        contradicting_evidence=[],
        source_types=[
            "log",
            "metric",
        ],
        confidence=0.90,
        status="supported",
    )

    assert root_cause.confidence == 0.90
    assert root_cause.status == "supported"

    assert root_cause.source_types == [
        "log",
        "metric",
    ]


def test_investigation_response_defaults():
    response = InvestigationResponse(
        incident_id="INC-001",
        status="completed",
        iteration=2,
        current_step="completed",
    )

    assert response.evidence == []
    assert response.hypotheses == []
    assert response.executed_actions == []

    assert response.root_cause is None
    assert response.final_report is None
    assert response.error is None