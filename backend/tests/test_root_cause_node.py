from app.orchestration.investigation_graph import (
    evaluate_root_cause,
)

from app.schemas.evidence import (
    Evidence,
    EvidenceSourceType,
)

from app.schemas.hypothesis import Hypothesis

from app.schemas.incident import (
    Incident,
    IncidentSeverity,
)

from app.schemas.investigation import InvestigationState

from app.schemas.root_cause import RootCauseStatus


def create_state_with_hypothesis():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    evidence = [
        Evidence(
            id="EV-001",
            incident_id="INC-001",
            source_type=EvidenceSourceType.LOG,
            service="payment-service",
            content="DB connection pool exhausted",
            relevance_score=1.0,
        ),
        Evidence(
            id="EV-002",
            incident_id="INC-001",
            source_type=EvidenceSourceType.METRIC,
            service="payment-service",
            content="DB utilization reached 98%",
            relevance_score=1.0,
        ),
    ]

    hypothesis = Hypothesis(
        id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database connection pool exhaustion "
            "caused payment failures"
        ),
        supporting_evidence=[
            "Evidence #1",
            "Evidence #2",
        ],
        contradicting_evidence=[],
        confidence=0.99,
    )

    return InvestigationState(
        incident=incident,
        evidence=evidence,
        hypotheses=[hypothesis],
    )


def test_evaluate_root_cause_node():
    state = create_state_with_hypothesis()

    result = evaluate_root_cause(state)

    candidate = result["root_cause_candidate"]

    assert candidate is not None

    assert candidate.hypothesis_id == "HYP-001"

    # Deterministic score, not LLM's 0.99.
    assert candidate.confidence == 0.70

    assert candidate.status == RootCauseStatus.SUPPORTED

    assert result["current_step"] == "root_cause_evaluated"


def test_evaluate_root_cause_without_hypothesis():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    state = InvestigationState(
        incident=incident,
    )

    result = evaluate_root_cause(state)

    assert result["root_cause_candidate"] is None

    assert (
        result["current_step"]
        == "no_root_cause_candidate"
    )