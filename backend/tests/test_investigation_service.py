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
    compare_investigations,
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


def test_compare_investigations():

    baseline = InvestigationModel(
        id="INV-BASE",
        incident_id="INC-001",
        status="completed",
        iteration=2,
        current_step="completed",
        executed_actions=json.dumps([
            "search_logs",
            "query_metrics",
        ]),
        evidence=json.dumps([
            {
                "id": "EV-001",
                "source_type": "log",
                "service": "payment-service",
                "content": "Database timeout",
                "relevance_score": 1.0,
            },
        ]),
        hypotheses=json.dumps([
            {
                "id": "HYP-001",
                "description": "Database timeout",
                "supporting_evidence": ["EV-001"],
                "contradicting_evidence": [],
                "confidence": 0.7,
                "status": "investigating",
            },
        ]),
        root_cause=json.dumps({
            "description": "Database timeout",
            "supporting_evidence": ["EV-001"],
            "contradicting_evidence": [],
            "source_types": ["log"],
            "confidence": 0.45,
            "status": "investigating",
        }),
        created_at=datetime(
            2026, 10, 1, 10, 0,
            tzinfo=timezone.utc,
        ),
    )

    comparison = InvestigationModel(
        id="INV-NEW",
        incident_id="INC-001",
        status="completed",
        iteration=4,
        current_step="completed",
        executed_actions=json.dumps([
            "search_logs",
            "query_metrics",
            "get_deployments",
        ]),
        evidence=json.dumps([
            {
                "id": "EV-001",
                "source_type": "log",
                "service": "payment-service",
                "content": "Database timeout",
                "relevance_score": 1.0,
            },
            {
                "id": "EV-002",
                "source_type": "metric",
                "service": "payment-service",
                "content": "Connection utilization high",
                "relevance_score": 0.9,
            },
        ]),
        hypotheses=json.dumps([
            {
                "id": "HYP-001",
                "description": "Database timeout",
                "supporting_evidence": ["EV-001"],
                "contradicting_evidence": [],
                "confidence": 0.7,
                "status": "investigating",
            },
            {
                "id": "HYP-002",
                "description": "Pool exhaustion",
                "supporting_evidence": ["EV-002"],
                "contradicting_evidence": [],
                "confidence": 0.9,
                "status": "supported",
            },
        ]),
        root_cause=json.dumps({
            "description": "Connection pool exhaustion",
            "supporting_evidence": [
                "EV-001",
                "EV-002",
            ],
            "contradicting_evidence": [],
            "source_types": [
                "log",
                "metric",
            ],
            "confidence": 0.82,
            "status": "supported",
        }),
        created_at=datetime(
            2026, 10, 2, 10, 0,
            tzinfo=timezone.utc,
        ),
    )

    with patch(
        "app.services.investigation_service."
        "InvestigationRepository.get_by_id",
        side_effect=[
            baseline,
            comparison,
        ],
    ):
        result = compare_investigations(
            db=object(),
            baseline_investigation_id="INV-BASE",
            comparison_investigation_id="INV-NEW",
        )

    assert result is not None

    assert result.baseline.investigation_id == "INV-BASE"
    assert result.comparison.investigation_id == "INV-NEW"

    assert result.baseline.root_cause_confidence == 0.45
    assert result.comparison.root_cause_confidence == 0.82

    assert result.changes.confidence_delta == 0.37
    assert result.changes.iteration_delta == 2
    assert result.changes.action_count_delta == 1
    assert result.changes.evidence_count_delta == 1
    assert result.changes.hypothesis_count_delta == 1

    assert result.changes.new_evidence_count == 1
    assert result.changes.removed_evidence_count == 0

    assert result.changes.new_hypothesis_count == 1
    assert result.changes.removed_hypothesis_count == 0

    assert (
        result.changes.root_cause_status_changed
        is True
    )


def test_compare_investigations_missing_run():

    with patch(
        "app.services.investigation_service."
        "InvestigationRepository.get_by_id",
        side_effect=[
            None,
            None,
        ],
    ):
        result = compare_investigations(
            db=object(),
            baseline_investigation_id="INV-MISSING-A",
            comparison_investigation_id="INV-MISSING-B",
        )

    assert result is None


def test_compare_investigations_different_incidents():

    baseline = InvestigationModel(
        id="INV-A",
        incident_id="INC-001",
        status="completed",
        iteration=1,
        current_step="completed",
        executed_actions="[]",
        evidence="[]",
        hypotheses="[]",
    )

    comparison = InvestigationModel(
        id="INV-B",
        incident_id="INC-002",
        status="completed",
        iteration=1,
        current_step="completed",
        executed_actions="[]",
        evidence="[]",
        hypotheses="[]",
    )

    with patch(
        "app.services.investigation_service."
        "InvestigationRepository.get_by_id",
        side_effect=[
            baseline,
            comparison,
        ],
    ):
        try:
            compare_investigations(
                db=object(),
                baseline_investigation_id="INV-A",
                comparison_investigation_id="INV-B",
            )

            assert False, (
                "Expected ValueError"
            )

        except ValueError as exc:
            assert (
                "same incident"
                in str(exc)
            )


def test_compare_investigations_without_rca():

    created_at = datetime(
        2026,
        10,
        1,
        10,
        0,
        tzinfo=timezone.utc,
    )

    baseline = InvestigationModel(
        id="INV-A",
        incident_id="INC-001",
        status="failed",
        iteration=1,
        current_step="tool_error",
        executed_actions="[]",
        evidence="[]",
        hypotheses="[]",
        root_cause=None,
        created_at=created_at,
    )

    comparison = InvestigationModel(
        id="INV-B",
        incident_id="INC-001",
        status="completed",
        iteration=2,
        current_step="completed",
        executed_actions="[]",
        evidence="[]",
        hypotheses="[]",
        root_cause=json.dumps({
            "description": "Database timeout",
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "source_types": ["log"],
            "confidence": 0.8,
            "status": "supported",
        }),
        created_at=created_at,
    )

    with patch(
        "app.services.investigation_service."
        "InvestigationRepository.get_by_id",
        side_effect=[
            baseline,
            comparison,
        ],
    ):
        result = compare_investigations(
            db=object(),
            baseline_investigation_id="INV-A",
            comparison_investigation_id="INV-B",
        )

    assert result is not None

    assert (
        result.baseline.root_cause_confidence
        is None
    )

    assert (
        result.comparison.root_cause_confidence
        == 0.8
    )

    # A numeric delta cannot be calculated
    # when one side has no confidence value.
    assert result.changes.confidence_delta is None

    assert (
        result.changes.root_cause_status_changed
        is True
    )