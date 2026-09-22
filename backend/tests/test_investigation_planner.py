from unittest.mock import patch

from app.orchestration.investigation_graph import plan_next_action
from app.schemas.incident import Incident, IncidentSeverity
from app.schemas.investigation import (
    InvestigationAction,
    InvestigationDecision,
    InvestigationState,
)

from app.orchestration.investigation_graph import (
    plan_next_action,
    route_action,
)


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