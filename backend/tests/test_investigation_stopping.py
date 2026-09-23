from app.orchestration.investigation_graph import (
    has_sufficient_evidence,
)

from app.schemas.incident import (
    Incident,
    IncidentSeverity,
)

from app.schemas.evidence import (
    Evidence,
    EvidenceSourceType,
)

from app.schemas.hypothesis import (
    Hypothesis,
    HypothesisStatus,
)

from app.schemas.investigation import InvestigationState


def create_incident():
    return Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )


def test_sufficient_evidence_returns_true():
    incident = create_incident()

    evidence = [
        Evidence(
            id="EV-001",
            incident_id="INC-001",
            source_type=EvidenceSourceType.DEPLOYMENT,
            service="payment-service",
            content="Version 2.4.0 deployed",
            relevance_score=1.0,
        ),
        Evidence(
            id="EV-002",
            incident_id="INC-001",
            source_type=EvidenceSourceType.LOG,
            service="payment-service",
            content="Database connection failed",
            relevance_score=1.0,
        ),
        Evidence(
            id="EV-003",
            incident_id="INC-001",
            source_type=EvidenceSourceType.METRIC,
            service="payment-service",
            content="Error rate increased",
            relevance_score=1.0,
        ),
    ]

    hypothesis = Hypothesis(
        id="HYP-001",
        incident_id="INC-001",
        description="Database exhaustion caused payment failures",
        supporting_evidence=["EV-002", "EV-003"],
        confidence=0.75,
        status=HypothesisStatus.INVESTIGATING,
    )

    state = InvestigationState(
        incident=incident,
        evidence=evidence,
        hypotheses=[hypothesis],
    )

    assert has_sufficient_evidence(state) is True


def test_sufficient_evidence_returns_false_when_confidence_low():
    incident = create_incident()

    evidence = [
        Evidence(
            id="EV-001",
            incident_id="INC-001",
            source_type=EvidenceSourceType.DEPLOYMENT,
            service="payment-service",
            content="Deployment detected",
            relevance_score=1.0,
        ),
        Evidence(
            id="EV-002",
            incident_id="INC-001",
            source_type=EvidenceSourceType.LOG,
            service="payment-service",
            content="Connection failure",
            relevance_score=1.0,
        ),
        Evidence(
            id="EV-003",
            incident_id="INC-001",
            source_type=EvidenceSourceType.METRIC,
            service="payment-service",
            content="Error rate increased",
            relevance_score=1.0,
        ),
    ]

    hypothesis = Hypothesis(
        id="HYP-001",
        incident_id="INC-001",
        description="Possible database exhaustion",
        confidence=0.40,
        status=HypothesisStatus.INVESTIGATING,
    )

    state = InvestigationState(
        incident=incident,
        evidence=evidence,
        hypotheses=[hypothesis],
    )

    assert has_sufficient_evidence(state) is False