from unittest.mock import patch

from app.orchestration.investigation_graph import (
    generate_final_report,
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

from app.schemas.root_cause import (
    RootCauseCandidate,
    RootCauseStatus,
)

from app.schemas.investigation import InvestigationState


class FakeResponse:
    content = """
# Incident Summary

Checkout payment failures increased.

# Investigation Findings

Payment-service produced database connection failures.

# Root Cause Hypothesis

Database connection exhaustion may have contributed
to the payment failures.

# Supporting Evidence

Database connection failures were observed.

# Contradicting Evidence

The deployment itself completed successfully.

# Confidence

0.75

# Recommended Next Steps

Inspect database connection pool configuration.
"""


class FakeLLM:
    def invoke(self, prompt):
        return FakeResponse()


def test_generate_final_report():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    evidence = Evidence(
        id="EV-001",
        incident_id="INC-001",
        source_type=EvidenceSourceType.LOG,
        service="payment-service",
        content="Database connection failed",
        relevance_score=1.0,
    )

    hypothesis = Hypothesis(
        id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database connection exhaustion may have "
            "contributed to payment failures."
        ),
        supporting_evidence=[
            "Database connection failure log",
        ],
        contradicting_evidence=[
            "Deployment completed successfully",
        ],
        confidence=0.75,
        status=HypothesisStatus.INVESTIGATING,
    )

    state = InvestigationState(
        incident=incident,
        evidence=[evidence],
        hypotheses=[hypothesis],
    )

    with patch(
        "app.orchestration.investigation_graph.get_llm",
        return_value=FakeLLM(),
    ):
        result = generate_final_report(state)

    assert result["current_step"] == "completed"

    assert result["final_report"] is not None

    assert (
        "Incident Summary"
        in result["final_report"]
    )

    assert (
        "Database connection exhaustion"
        in result["final_report"]
    )

    assert (
        "Recommended Next Steps"
        in result["final_report"]
    )


def test_final_report_uses_deterministic_root_cause():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description=(
            "Payment failures increased after deployment"
        ),
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

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

        # Intentionally different.
        confidence=0.99,
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
            "Evidence #1",
            "Evidence #2",
        ],
        contradicting_evidence=[],
        source_types=[
            "log",
            "metric",
        ],

        # TraceRoot's authoritative score.
        confidence=0.70,
        status=RootCauseStatus.SUPPORTED,
    )

    state = InvestigationState(
        incident=incident,
        hypotheses=[hypothesis],
        root_cause_candidate=candidate,
    )

    class CapturingResponse:
        content = "Generated RCA report"

    class CapturingLLM:
        def __init__(self):
            self.prompt = None

        def invoke(self, prompt):
            self.prompt = prompt
            return CapturingResponse()

    fake_llm = CapturingLLM()

    with patch(
        "app.orchestration.investigation_graph.get_llm",
        return_value=fake_llm,
    ):
        result = generate_final_report(state)

    assert result["final_report"] == "Generated RCA report"

    assert result["current_step"] == "completed"

    assert "Deterministic Confidence:" in fake_llm.prompt
    assert "0.70" in fake_llm.prompt

    assert "Evaluation Status:" in fake_llm.prompt
    assert "supported" in fake_llm.prompt

    assert (
        "The deterministic root cause evaluation is authoritative"
        in fake_llm.prompt
    )