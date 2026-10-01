import json
from datetime import datetime, timezone

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

from app.models.investigation import InvestigationModel

from app.services.investigation_service import (
    build_investigation_response,
    get_investigation_by_id,
    get_investigation_history,
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


def test_get_investigation_history_converts_models():

    created_at = datetime(
        2026,
        10,
        1,
        10,
        30,
        tzinfo=timezone.utc,
    )

    model = InvestigationModel(
        id="INV-003",
        incident_id="INC-001",
        status="completed",
        iteration=3,
        current_step="completed",
        executed_actions="[]",
        evidence="[]",
        hypotheses="[]",
        root_cause=json.dumps(
            {
                "description": "Database pool exhaustion",
                "confidence": 0.92,
                "status": "supported",
            }
        ),
        created_at=created_at,
    )

    with patch(
        "app.services.investigation_service."
        "InvestigationRepository.get_history_by_incident_id",
        return_value=[model],
    ) as mock_get:

        result = get_investigation_history(
            db=object(),
            incident_id="INC-001",
        )

    assert len(result) == 1

    item = result[0]

    assert item.investigation_id == "INV-003"
    assert item.incident_id == "INC-001"
    assert item.status == "completed"
    assert item.iteration == 3
    assert item.current_step == "completed"
    assert item.created_at == created_at
    assert item.root_cause_confidence == 0.92

    mock_get.assert_called_once_with(
        "INC-001"
    )


def test_get_investigation_history_without_root_cause():

    model = InvestigationModel(
        id="INV-001",
        incident_id="INC-001",
        status="failed",
        iteration=1,
        current_step="tool_error",
        executed_actions="[]",
        evidence="[]",
        hypotheses="[]",
        root_cause=None,
        created_at=datetime(
            2026,
            10,
            1,
            9,
            0,
            tzinfo=timezone.utc,
        ),
    )

    with patch(
        "app.services.investigation_service."
        "InvestigationRepository.get_history_by_incident_id",
        return_value=[model],
    ):

        result = get_investigation_history(
            db=object(),
            incident_id="INC-001",
        )

    assert len(result) == 1
    assert result[0].investigation_id == "INV-001"
    assert result[0].root_cause_confidence is None


def test_get_investigation_by_id():

    model = InvestigationModel(
        id="INV-003",
        incident_id="INC-001",
        status="completed",
        iteration=3,
        current_step="completed",
        executed_actions=json.dumps(
            [
                "search_logs",
                "query_metrics",
            ]
        ),
        evidence="[]",
        hypotheses="[]",
        root_cause=json.dumps(
            {
                "description":
                    "Database pool exhaustion",
                "supporting_evidence": [],
                "contradicting_evidence": [],
                "source_types": ["log"],
                "confidence": 0.92,
                "status": "supported",
            }
        ),
        final_report="Historical RCA report",
        error=None,
    )

    with patch(
        "app.services.investigation_service."
        "InvestigationRepository.get_by_id",
        return_value=model,
    ) as mock_get:

        result = get_investigation_by_id(
            db=object(),
            investigation_id="INV-003",
        )

    assert result is not None
    assert result.incident_id == "INC-001"
    assert result.status == "completed"
    assert result.iteration == 3
    assert result.final_report == (
        "Historical RCA report"
    )

    assert result.root_cause is not None
    assert result.root_cause.confidence == 0.92

    mock_get.assert_called_once_with(
        "INV-003"
    )


def test_get_investigation_by_id_not_found():

    with patch(
        "app.services.investigation_service."
        "InvestigationRepository.get_by_id",
        return_value=None,
    ):

        result = get_investigation_by_id(
            db=object(),
            investigation_id="INV-MISSING",
        )

    assert result is None