from app.orchestration.investigation_graph import (
    has_sufficient_evidence,
)

from app.schemas.evidence import (
    Evidence,
    EvidenceSourceType,
)

from app.schemas.hypothesis import (
    Hypothesis,
    HypothesisStatus,
)

from app.schemas.incident import (
    Incident,
    IncidentSeverity,
)

from app.schemas.investigation import InvestigationState

from app.schemas.root_cause import (
    RootCauseCandidate,
    RootCauseStatus,
)


def create_incident():
    return Incident(
        id="INC-001",
        title="Checkout payment failures",
        description=(
            "Payment failures increased after deployment"
        ),
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
        description=(
            "Database exhaustion caused payment failures"
        ),
        supporting_evidence=[
            "Evidence #2",
            "Evidence #3",
        ],
        contradicting_evidence=[],
        confidence=0.75,
        status=HypothesisStatus.INVESTIGATING,
    )

    root_cause_candidate = RootCauseCandidate(
        hypothesis_id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database exhaustion caused payment failures"
        ),
        supporting_evidence=[
            "Evidence #2",
            "Evidence #3",
        ],
        contradicting_evidence=[],
        source_types=[
            "log",
            "metric",
        ],
        confidence=0.70,
        status=RootCauseStatus.SUPPORTED,
    )

    state = InvestigationState(
        incident=incident,
        evidence=evidence,
        hypotheses=[hypothesis],
        root_cause_candidate=root_cause_candidate,
    )

    assert has_sufficient_evidence(state) is True


def test_sufficient_evidence_returns_false_when_confidence_low():
    incident = create_incident()

    evidence = [
        Evidence(
            id="EV-001",
            incident_id="INC-001",
            source_type=EvidenceSourceType.LOG,
            service="payment-service",
            content="Database connection failed",
            relevance_score=1.0,
        ),
        Evidence(
            id="EV-002",
            incident_id="INC-001",
            source_type=EvidenceSourceType.METRIC,
            service="payment-service",
            content="Error rate increased",
            relevance_score=1.0,
        ),
        Evidence(
            id="EV-003",
            incident_id="INC-001",
            source_type=EvidenceSourceType.DEPLOYMENT,
            service="payment-service",
            content="Version 2.4.0 deployed",
            relevance_score=1.0,
        ),
    ]

    hypothesis = Hypothesis(
        id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database exhaustion caused payment failures"
        ),
        supporting_evidence=[
            "Evidence #1",
        ],
        contradicting_evidence=[],
        confidence=0.95,
        status=HypothesisStatus.INVESTIGATING,
    )

    root_cause_candidate = RootCauseCandidate(
        hypothesis_id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database exhaustion caused payment failures"
        ),
        supporting_evidence=[
            "Evidence #1",
        ],
        contradicting_evidence=[],
        source_types=[
            "log",
        ],
        confidence=0.45,
        status=RootCauseStatus.INVESTIGATING,
    )

    state = InvestigationState(
        incident=incident,
        evidence=evidence,
        hypotheses=[hypothesis],
        root_cause_candidate=root_cause_candidate,
    )

    assert has_sufficient_evidence(state) is False


def test_high_llm_confidence_does_not_stop_without_supported_rca():
    incident = create_incident()

    evidence = [
        Evidence(
            id="EV-001",
            incident_id="INC-001",
            source_type=EvidenceSourceType.LOG,
            service="payment-service",
            content="DB pool exhausted",
            relevance_score=1.0,
        ),
        Evidence(
            id="EV-002",
            incident_id="INC-001",
            source_type=EvidenceSourceType.LOG,
            service="payment-service",
            content="Database timeout",
            relevance_score=1.0,
        ),
        Evidence(
            id="EV-003",
            incident_id="INC-001",
            source_type=EvidenceSourceType.METRIC,
            service="payment-service",
            content="DB utilization increased",
            relevance_score=1.0,
        ),
    ]

    # The LLM is highly confident.
    hypothesis = Hypothesis(
        id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database exhaustion caused payment failures"
        ),
        supporting_evidence=[
            "Evidence #1",
        ],
        contradicting_evidence=[],
        confidence=0.99,
        status=HypothesisStatus.INVESTIGATING,
    )

    # But TraceRoot's deterministic evaluator does not
    # consider the RCA sufficiently supported.
    root_cause_candidate = RootCauseCandidate(
        hypothesis_id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database exhaustion caused payment failures"
        ),
        supporting_evidence=[
            "Evidence #1",
        ],
        contradicting_evidence=[],
        source_types=[
            "log",
        ],
        confidence=0.45,
        status=RootCauseStatus.INVESTIGATING,
    )

    state = InvestigationState(
        incident=incident,
        evidence=evidence,
        hypotheses=[hypothesis],
        root_cause_candidate=root_cause_candidate,
    )

    assert has_sufficient_evidence(state) is False


def test_supported_rca_with_multi_source_evidence_can_stop():
    incident = create_incident()

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
        Evidence(
            id="EV-003",
            incident_id="INC-001",
            source_type=EvidenceSourceType.LOG,
            service="payment-service",
            content="Payment transaction timed out",
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
            "Evidence #3",
        ],
        contradicting_evidence=[],
        confidence=0.95,
        status=HypothesisStatus.INVESTIGATING,
    )

    root_cause_candidate = RootCauseCandidate(
        hypothesis_id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database connection pool exhaustion "
            "caused payment failures"
        ),
        supporting_evidence=[
            "Evidence #1",
            "Evidence #2",
            "Evidence #3",
        ],
        contradicting_evidence=[],
        source_types=[
            "log",
            "metric",
        ],
        confidence=0.80,
        status=RootCauseStatus.SUPPORTED,
    )

    state = InvestigationState(
        incident=incident,
        evidence=evidence,
        hypotheses=[hypothesis],
        root_cause_candidate=root_cause_candidate,
    )

    assert has_sufficient_evidence(state) is True