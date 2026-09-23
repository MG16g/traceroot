from unittest.mock import patch

from app.orchestration.investigation_graph import (
        MAX_ITERATIONS,
        build_action_fingerprint, 
        format_evidence_for_planner,
        format_hypotheses_for_planner,
        plan_next_action,
        route_action,
    )
from app.schemas.incident import Incident, IncidentSeverity
from app.schemas.investigation import (
    InvestigationAction,
    InvestigationDecision,
    InvestigationState,
)

from app.schemas.hypothesis import (
    Hypothesis,
    HypothesisStatus,
)

from app.orchestration.investigation_graph import (
    plan_next_action,
    route_action,
)
from app.schemas.evidence import Evidence, EvidenceSourceType
from tests.test_investigation_graph import create_test_incident


class FakeStructuredLLM:
    def invoke(self, prompt):
        return InvestigationDecision(
            action=InvestigationAction.SEARCH_LOGS,
            reason="Check payment-service error logs",
            parameters={
                "service": "payment-service",
                "level": "ERROR",
            },
        )


class FakeLLM:
    def with_structured_output(self, schema):
        assert schema is InvestigationDecision
        return FakeStructuredLLM()


def test_plan_next_action_returns_structured_decision():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    state = InvestigationState(
        incident=incident,
    )

    with patch(
        "app.orchestration.investigation_graph.get_llm",
        return_value=FakeLLM(),
    ):
        result = plan_next_action(state)

    decision = result["current_decision"]

    assert isinstance(decision, InvestigationDecision)

    assert decision.action == InvestigationAction.SEARCH_LOGS

    assert decision.reason == "Check payment-service error logs"

    assert decision.parameters == {
        "service": "payment-service",
        "level": "ERROR",
    }

    assert result["current_step"] == "action_selected"


def test_route_action_to_execute():
    decision = InvestigationDecision(
        action=InvestigationAction.GET_DEPLOYMENTS,
        reason="Check recent deployments",
        parameters={"service": "payment-service"},
    )

    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    state = InvestigationState(
        incident=incident,
        current_decision=decision,
    )

    assert route_action(state) == "execute_action"


def test_route_action_to_stop():
    decision = InvestigationDecision(
        action=InvestigationAction.STOP,
        reason="Sufficient evidence has been collected",
    )

    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    state = InvestigationState(
        incident=incident,
        current_decision=decision,
    )

    assert route_action(state) == "stop"


def test_format_evidence_for_planner_when_empty():
    result = format_evidence_for_planner([])

    assert result == "No evidence has been collected yet."

def test_format_evidence_for_planner_with_evidence():
    evidence = Evidence(
        id="EV-001",
        incident_id="INC-001",
        source_type=EvidenceSourceType.DEPLOYMENT,
        service="payment-service",
        content="Version 2.4.0 deployed successfully",
        relevance_score=1.0,
    )

    result = format_evidence_for_planner([evidence])

    assert "Evidence #1" in result
    assert "deployment" in result
    assert "payment-service" in result
    assert "Version 2.4.0 deployed successfully" in result


def test_route_action_stops_at_max_iterations():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    decision = InvestigationDecision(
        action=InvestigationAction.SEARCH_LOGS,
        reason="Continue investigating payment errors",
        parameters={
            "service": "payment-service",
        },
    )

    state = InvestigationState(
        incident=incident,
        current_decision=decision,
        iteration=MAX_ITERATIONS,
    )

    assert route_action(state) == "stop"


def test_build_action_fingerprint_is_deterministic():
    first = InvestigationDecision(
        action=InvestigationAction.SEARCH_LOGS,
        reason="Test",
        parameters={
            "service": "payment-service",
            "level": "ERROR",
        },
    )

    second = InvestigationDecision(
        action=InvestigationAction.SEARCH_LOGS,
        reason="Test",
        parameters={
            "level": "ERROR",
            "service": "payment-service",
        },
    )

    assert (
        build_action_fingerprint(first)
        == build_action_fingerprint(second)
    )


def test_route_action_detects_duplicate():
    incident = create_test_incident()

    decision = InvestigationDecision(
        action=InvestigationAction.GET_DEPLOYMENTS,
        reason="Check deployments again",
        parameters={
            "service": "payment-service",
        },
    )

    fingerprint = build_action_fingerprint(
        decision
    )

    state = InvestigationState(
        incident=incident,
        current_decision=decision,
        iteration=2,
        executed_actions=[fingerprint],
    )

    assert route_action(state) == "duplicate"

def test_format_hypotheses_for_planner_when_empty():
    result = format_hypotheses_for_planner([])

    assert result == "No hypothesis has been formed yet."

def test_format_hypotheses_for_planner_with_hypothesis():
    hypothesis = Hypothesis(
        id="HYP-001",
        incident_id="INC-001",
        description=(
            "Database connection exhaustion may be "
            "contributing to payment failures."
        ),
        supporting_evidence=[
            "Database connection failure log",
        ],
        contradicting_evidence=[
            "Deployment completed successfully",
        ],
        confidence=0.65,
        status=HypothesisStatus.INVESTIGATING,
    )

    result = format_hypotheses_for_planner(
        [hypothesis]
    )

    assert "Hypothesis #1" in result

    assert (
        "Database connection exhaustion"
        in result
    )

    assert "0.65" in result
    assert "investigating" in result

    assert (
        "Database connection failure log"
        in result
    )

    assert (
        "Deployment completed successfully"
        in result
    )