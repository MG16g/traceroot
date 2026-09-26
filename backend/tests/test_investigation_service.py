from unittest.mock import patch, MagicMock

from app.services.investigation_service import (
    persist_investigation,
)

from app.schemas.evidence import (
    Evidence,
    EvidenceSourceType,
)

from app.schemas.hypothesis import (
    Hypothesis,
    HypothesisStatus,
)

from app.schemas.root_cause import (
    RootCauseCandidate,
    RootCauseStatus,
)

from app.services.investigation_service import (
    build_investigation_response,
)
from app.schemas.api import InvestigationResponse, RootCauseResponse


def test_build_investigation_response():

    evidence = Evidence(
        id="EV-001",
        incident_id="INC-001",
        source_type=EvidenceSourceType.LOG,
        service="payment-service",
        content=(
            "DBConnectionPoolExhausted"
        ),
        relevance_score=1.0,
    )

    hypothesis = Hypothesis(
        id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database connection pool exhaustion "
            "caused payment failures"
        ),
        supporting_evidence=[
            "EV-001",
        ],
        contradicting_evidence=[],
        confidence=0.9,
        status=HypothesisStatus.INVESTIGATING,
    )

    candidate = RootCauseCandidate(
        hypothesis_id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database connection pool exhaustion "
            "caused payment failures"
        ),
        supporting_evidence=[
            "EV-001",
        ],
        contradicting_evidence=[],
        source_types=[
            EvidenceSourceType.LOG,
        ],
        confidence=0.9,
        status=RootCauseStatus.SUPPORTED,
    )

    result = {
        "iteration": 2,
        "current_step": "completed",
        "status": "completed",
        "executed_actions": [
            (
                "search_logs|"
                "level=ERROR,"
                "service=payment-service"
            )
        ],
        "evidence": [
            evidence,
        ],
        "hypotheses": [
            hypothesis,
        ],
        "root_cause_candidate": candidate,
        "final_report": "RCA report",
        "error": None,
    }

    response = build_investigation_response(
        result=result,
        incident_id="INC-001",
    )

    assert response.incident_id == "INC-001"

    assert response.status == "completed"

    assert response.iteration == 2

    assert response.current_step == "completed"

    assert len(response.evidence) == 1

    assert (
        response.evidence[0].source_type
        == "log"
    )

    assert len(response.hypotheses) == 1

    assert (
        response.hypotheses[0].confidence
        == 0.9
    )

    assert response.root_cause is not None

    assert (
        response.root_cause.status
        == "supported"
    )

    assert (
        response.root_cause.confidence
        == 0.9
    )

    assert response.final_report == "RCA report"


def test_persist_investigation():

    db = MagicMock()

    response = InvestigationResponse(
        incident_id="INC-001",
        status="completed",
        iteration=2,
        current_step="completed",
        executed_actions=[
            "search_logs|service=payment-service"
        ],
        root_cause=RootCauseResponse(
            description=(
                "Database connection pool exhaustion"
            ),
            supporting_evidence=[
                "EV-001",
            ],
            contradicting_evidence=[],
            source_types=[
                "log",
                "metric",
            ],
            confidence=0.9,
            status="supported",
        ),
        final_report="RCA report",
    )

    with patch(
        "app.services.investigation_service."
        "InvestigationRepository.create"
    ) as mock_create:

        mock_create.side_effect = (
            lambda investigation: investigation
        )

        saved = persist_investigation(
            db=db,
            response=response,
        )

    assert saved.incident_id == "INC-001"

    assert saved.id.startswith(
        "INV-"
    )

    assert saved.status == "completed"

    assert saved.iteration == 2

    assert saved.final_report == "RCA report"

    assert (
        "Database connection pool exhaustion"
        in saved.root_cause
    )

    assert (
        "search_logs"
        in saved.executed_actions
    )

    mock_create.assert_called_once()