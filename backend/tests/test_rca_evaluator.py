from app.schemas.evidence import (
    Evidence,
    EvidenceSourceType,
)

from app.services.rca_evaluator import (
    calculate_confidence,
    evaluate_hypothesis,
    resolve_evidence_reference,
    validate_evidence_references,

)

from app.schemas.hypothesis import (
    Hypothesis,
    HypothesisStatus,
)

from app.schemas.root_cause import RootCauseStatus


def create_test_evidence():
    return [
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


def test_resolve_valid_evidence_reference():
    evidence = create_test_evidence()

    result = resolve_evidence_reference(
        "Evidence #2",
        evidence,
    )

    assert result is not None
    assert result.id == "EV-002"


def test_resolve_out_of_range_evidence_reference():
    evidence = create_test_evidence()

    result = resolve_evidence_reference(
        "Evidence #99",
        evidence,
    )

    assert result is None


def test_resolve_malformed_evidence_reference():
    evidence = create_test_evidence()

    assert (
        resolve_evidence_reference(
            "Evidence 1",
            evidence,
        )
        is None
    )

    assert (
        resolve_evidence_reference(
            "EV-001",
            evidence,
        )
        is None
    )


def test_validate_evidence_references():
    evidence = create_test_evidence()

    valid, invalid = validate_evidence_references(
        [
            "Evidence #1",
            "Evidence #2",
            "Evidence #99",
            "fake evidence",
        ],
        evidence,
    )

    assert valid == [
        "Evidence #1",
        "Evidence #2",
    ]

    assert invalid == [
        "Evidence #99",
        "fake evidence",
    ]


def test_confidence_with_strong_multi_source_evidence():
    evidence = create_test_evidence()

    score = calculate_confidence(
        supporting_evidence=evidence,
        contradicting_evidence=[],
    )

    assert score == 0.70


def test_confidence_with_single_evidence_is_lower():
    evidence = create_test_evidence()

    score = calculate_confidence(
        supporting_evidence=[evidence[0]],
        contradicting_evidence=[],
    )

    assert score == 0.45


def test_contradicting_evidence_reduces_confidence():
    evidence = create_test_evidence()

    without_contradiction = calculate_confidence(
        supporting_evidence=evidence,
        contradicting_evidence=[],
    )

    with_contradiction = calculate_confidence(
        supporting_evidence=evidence,
        contradicting_evidence=[evidence[0]],
    )

    assert with_contradiction < without_contradiction

    assert with_contradiction == 0.60


def test_confidence_without_supporting_evidence_is_zero():
    score = calculate_confidence(
        supporting_evidence=[],
        contradicting_evidence=[],
    )

    assert score == 0.0


def test_evaluate_hypothesis_creates_supported_candidate():
    evidence = create_test_evidence()

    hypothesis = Hypothesis(
        id="HYP-001",
        incident_id="INC-001",
        description="Database connection exhaustion caused failures",
        supporting_evidence=[
            "Evidence #1",
            "Evidence #2",
        ],
        contradicting_evidence=[],
        confidence=0.99,
        status=HypothesisStatus.INVESTIGATING,
    )

    candidate = evaluate_hypothesis(
        hypothesis,
        evidence,
    )

    assert candidate.hypothesis_id == "HYP-001"

    # Deterministic score should be used.
    assert candidate.confidence == 0.70

    assert candidate.status == RootCauseStatus.SUPPORTED

    assert candidate.source_types == [
        "log",
        "metric",
    ]


def test_evaluate_hypothesis_removes_invalid_references():
    evidence = create_test_evidence()

    hypothesis = Hypothesis(
        id="HYP-002",
        incident_id="INC-001",
        description="Possible database issue",
        supporting_evidence=[
            "Evidence #1",
            "Evidence #99",
        ],
        contradicting_evidence=[],
        confidence=0.95,
    )

    candidate = evaluate_hypothesis(
        hypothesis,
        evidence,
    )

    assert candidate.supporting_evidence == [
        "Evidence #1",
    ]

    assert "Evidence #99" not in (
        candidate.supporting_evidence
    )

    assert candidate.confidence == 0.45

    assert (
        candidate.status
        == RootCauseStatus.INVESTIGATING
    )


def test_evaluate_hypothesis_can_reject_candidate():
    evidence = create_test_evidence()

    hypothesis = Hypothesis(
        id="HYP-003",
        incident_id="INC-001",
        description="Weak hypothesis",
        supporting_evidence=[
            "Evidence #1",
        ],
        contradicting_evidence=[
            "Evidence #2",
        ],
        confidence=0.90,
    )

    candidate = evaluate_hypothesis(
        hypothesis,
        evidence,
    )

    assert candidate.confidence == 0.35

    assert (
        candidate.status
        == RootCauseStatus.REJECTED
    )