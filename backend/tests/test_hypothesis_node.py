from unittest.mock import patch

from app.orchestration.investigation_graph import (
    update_hypotheses,
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
    HypothesisProposal,
    HypothesisStatus,
)

from app.schemas.investigation import (
    InvestigationState,
)


class FakeHypothesisLLM:
    def invoke(self, prompt):
        return HypothesisProposal(
            description=(
                "Database connection exhaustion may be "
                "contributing to payment failures."
            ),
            supporting_evidence=[
                "Database connection failure log",
                "Elevated database utilization",
            ],
            contradicting_evidence=[
                "Deployment completed successfully",
            ],
            confidence=0.75,
        )


class FakeLLM:
    def with_structured_output(self, schema):
        assert schema is HypothesisProposal
        return FakeHypothesisLLM()


def test_update_hypotheses_from_evidence():
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

    state = InvestigationState(
        incident=incident,
        evidence=[evidence],
    )

    with patch(
        "app.orchestration.investigation_graph.get_llm",
        return_value=FakeLLM(),
    ):
        result = update_hypotheses(state)

    assert len(result["hypotheses"]) == 1

    hypothesis = result["hypotheses"][0]

    assert hypothesis.incident_id == "INC-001"

    assert (
        "Database connection exhaustion"
        in hypothesis.description
    )

    assert hypothesis.confidence == 0.75

    assert (
        hypothesis.status
        == HypothesisStatus.INVESTIGATING
    )

    assert (
        result["current_step"]
        == "hypothesis_updated"
    )