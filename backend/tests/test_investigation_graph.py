from unittest.mock import patch

from app.orchestration.investigation_graph import build_investigation_graph

from app.schemas.incident import (
    Incident,
    IncidentSeverity,
)

from app.schemas.investigation import (
    InvestigationAction,
    InvestigationDecision,
    InvestigationState,
)


class FakeStructuredLLM:
    def invoke(self, prompt):
        return InvestigationDecision(
            action=InvestigationAction.GET_DEPLOYMENTS,
            reason="Check recent payment-service deployments",
            parameters={
                "service": "payment-service",
            },
        )


class FakeLLM:
    def with_structured_output(self, schema):
        return FakeStructuredLLM()


def test_investigation_graph_executes_selected_action():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    initial_state = InvestigationState(
        incident=incident,
    )

    fake_deployments = [
        {
            "service": "payment-service",
            "version": "2.4.0",
            "timestamp": "2026-09-22T14:06:00",
            "status": "success",
        }
    ]

    graph = build_investigation_graph()

    with patch(
        "app.orchestration.investigation_graph.get_llm",
        return_value=FakeLLM(),
    ), patch(
        "app.orchestration.investigation_graph.get_deployments",
        return_value=fake_deployments,
    ) as mock_get_deployments:

        result = graph.invoke(initial_state)

    # Planner decision survived through graph state
    assert (
        result["current_decision"].action
        == InvestigationAction.GET_DEPLOYMENTS
    )

    # Correct deterministic tool was called
    mock_get_deployments.assert_called_once_with(
        incident_id="INC-001",
        service="payment-service",
    )

    # Executor completed
    assert result["current_step"] == "evidence_collected"

    # Tool result became Evidence
    assert len(result["evidence"]) == 1

    evidence = result["evidence"][0]

    assert evidence.incident_id == "INC-001"
    assert evidence.service == "payment-service"
    assert "2.4.0" in evidence.content



def test_investigation_graph_stops_without_tool_execution():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    initial_state = InvestigationState(
        incident=incident,
    )

    class StopStructuredLLM:
        def invoke(self, prompt):
            return InvestigationDecision(
                action=InvestigationAction.STOP,
                reason="No further evidence is required",
            )

    class StopLLM:
        def with_structured_output(self, schema):
            return StopStructuredLLM()

    graph = build_investigation_graph()

    with patch(
        "app.orchestration.investigation_graph.get_llm",
        return_value=StopLLM(),
    ), patch(
        "app.orchestration.investigation_graph.search_logs"
    ) as mock_logs, patch(
        "app.orchestration.investigation_graph.query_metrics"
    ) as mock_metrics, patch(
        "app.orchestration.investigation_graph.get_deployments"
    ) as mock_deployments:

        result = graph.invoke(initial_state)

    assert result["current_decision"].action == InvestigationAction.STOP

    mock_logs.assert_not_called()
    mock_metrics.assert_not_called()
    mock_deployments.assert_not_called()

    assert result["evidence"] == []