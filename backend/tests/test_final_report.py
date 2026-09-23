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