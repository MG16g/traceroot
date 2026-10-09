from unittest.mock import patch

from app.orchestration.investigation_graph import (
    build_investigation_graph,
)

from app.schemas.incident import (
    Incident,
    IncidentSeverity,
)

from app.schemas.investigation import (
    InvestigationAction,
    InvestigationDecision,
    InvestigationState,
    InvestigationStatus,
)

from app.schemas.hypothesis import HypothesisProposal


def create_test_incident():
    return Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )


class SequentialStructuredLLM:
    def __init__(self):
        self.call_count = 0

    def invoke(self, prompt):
        self.call_count += 1

        if self.call_count == 1:
            return InvestigationDecision(
                action=InvestigationAction.GET_DEPLOYMENTS,
                reason="Check recent deployments",
                parameters={
                    "service": "payment-service",
                },
            )

        if self.call_count == 2:
            return InvestigationDecision(
                action=InvestigationAction.SEARCH_LOGS,
                reason="Inspect payment-service errors",
                parameters={
                    "service": "payment-service",
                    "level": "ERROR",
                },
            )

        if self.call_count == 3:
            return InvestigationDecision(
                action=InvestigationAction.QUERY_METRICS,
                reason="Inspect payment-service error rate",
                parameters={
                    "service": "payment-service",
                    "metric": "error_rate",
                },
            )

        return InvestigationDecision(
            action=InvestigationAction.STOP,
            reason="Sufficient evidence has been collected",
        )


class SequentialFakeLLM:
    def __init__(self):
        self.structured_llm = SequentialStructuredLLM()

    def with_structured_output(self, schema):
        return self.structured_llm


def test_investigation_graph_runs_iterative_investigation():
    incident = create_test_incident()

    initial_state = InvestigationState(
        incident=incident,
    )

    fake_deployments = [
        {
            "deployment_id": "DEP-1001",
            "service": "payment-service",
            "version": "2.4.0",
            "timestamp": "2026-09-18T14:06:00Z",
            "status": "success",
        }
    ]

    fake_logs = [
        {
            "service": "payment-service",
            "level": "ERROR",
            "message": "Database connection failed",
            "timestamp": "2026-09-18T14:07:00Z",
        }
    ]

    fake_metrics = [
        {
            "service": "payment-service",
            "metric": "error_rate",
            "value": 0.42,
            "timestamp": "2026-09-18T14:08:00Z",
        }
    ]

    fake_llm = FakeLLM()

    graph = build_investigation_graph()

    with patch(
        "app.orchestration.investigation_graph.get_llm",
        return_value=fake_llm,
    ), patch(
        "app.orchestration.investigation_graph.get_deployments",
        return_value=fake_deployments,
    ) as mock_deployments, patch(
        "app.orchestration.investigation_graph.search_logs",
        return_value=fake_logs,
    ) as mock_logs, patch(
        "app.orchestration.investigation_graph.query_metrics",
        return_value=fake_metrics,
    ) as mock_metrics:

        result = graph.invoke(initial_state)

    # Planner sequence:
    # 1 deployment
    # 2 logs
    # 3 metrics
    # 4 STOP
    assert result["iteration"] == 4

    assert (
        result["current_decision"].action
        == InvestigationAction.STOP
    )

    mock_deployments.assert_called_once_with(
        incident_id="INC-001",
        service="payment-service",
    )

    mock_logs.assert_called_once_with(
        incident_id="INC-001",
        service="payment-service",
        level="ERROR",
    )

    mock_metrics.assert_called_once_with(
        incident_id="INC-001",
        service="payment-service",
        metric="error_rate",
    )

    # One Evidence object from each tool.
    assert len(result["evidence"]) == 3

    assert len(result["executed_actions"]) == 3

    assert any(
        InvestigationAction.GET_DEPLOYMENTS.value in action
        for action in result["executed_actions"]
    )

    assert any(
        InvestigationAction.SEARCH_LOGS.value in action
        for action in result["executed_actions"]
    )

    assert any(
        InvestigationAction.QUERY_METRICS.value in action
        for action in result["executed_actions"]
    )

    contents = [
        evidence.content
        for evidence in result["evidence"]
    ]

    assert any(
        "2.4.0" in content
        for content in contents
    )

    assert any(
        "Database connection failed" in content
        for content in contents
    )

    assert any(
        "error_rate" in content
        for content in contents
    )

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

    # RCA candidate should have been generated by the
    # deterministic evaluation layer.
    candidate = result["root_cause_candidate"]

    assert candidate is not None

    assert candidate.incident_id == "INC-001"

    assert candidate.hypothesis_id is not None

    assert candidate.confidence >= 0.0
    assert candidate.confidence <= 1.0

    assert candidate.status is not None

    assert isinstance(
        candidate.supporting_evidence,
        list,
    )

    assert isinstance(
        candidate.contradicting_evidence,
        list,
    )

    assert isinstance(
        candidate.source_types,
        list,
    )
    


def test_investigation_graph_attempts_telemetry_before_stopping():
    incident = create_test_incident()

    initial_state = InvestigationState(
        incident=incident,
    )

    class StopStructuredLLM:
        def invoke(self, prompt):
            return InvestigationDecision(
                action=InvestigationAction.STOP,
                reason="No investigation required",
            )

    class StopReportResponse:
        content = (
            "# Incident Summary\n"
            "Initial telemetry was checked.\n\n"
            "# Investigation Findings\n"
            "No matching telemetry records were returned.\n\n"
            "# Root Cause Hypothesis\n"
            "No evidence-backed root cause is available.\n\n"
            "# Recommended Next Steps\n"
            "Investigate additional telemetry sources."
        )

    class StopLLM:
        def with_structured_output(self, schema, **kwargs):
            return StopStructuredLLM()

        def invoke(self, prompt):
            return StopReportResponse()

    graph = build_investigation_graph()

    with patch(
        "app.orchestration.investigation_graph.get_llm",
        return_value=StopLLM(),
    ), patch(
        "app.orchestration.investigation_graph.search_logs",
        return_value=[],
    ) as mock_logs, patch(
        "app.orchestration.investigation_graph.query_metrics",
    ) as mock_metrics, patch(
        "app.orchestration.investigation_graph.get_deployments",
    ) as mock_deployments:

        result = graph.invoke(initial_state)

    # Initial STOP must be overridden by a telemetry action.
    mock_logs.assert_called_once_with(
        incident_id=incident.id,
    )

    # Other telemetry tools should not be invoked.
    mock_metrics.assert_not_called()
    mock_deployments.assert_not_called()

    # The planner runs again after the empty log result.
    assert result["iteration"] == 2

    # The investigation must terminate without looping forever.
    assert result["current_step"] == "completed"

    # The attempted action must be recorded.
    assert result["executed_actions"] == [
        "search_logs|"
    ]

    # Empty telemetry must not produce fabricated evidence.
    assert result["evidence"] == []
    assert result["hypotheses"] == []
    assert result.get("root_cause_candidate") is None

    # The final report must still be generated.
    assert result["final_report"] is not None

    # The investigation status must be updated.
    assert result["status"] == InvestigationStatus.COMPLETED

    

    
class SequentialDecisionLLM:
    def __init__(self):
        self.call_count = 0

    def invoke(self, prompt):
        self.call_count += 1

        if self.call_count == 1:
            return InvestigationDecision(
                action=InvestigationAction.GET_DEPLOYMENTS,
                reason="Check recent deployments",
                parameters={
                    "service": "payment-service",
                },
            )

        if self.call_count == 2:
            return InvestigationDecision(
                action=InvestigationAction.SEARCH_LOGS,
                reason="Inspect payment-service errors",
                parameters={
                    "service": "payment-service",
                    "level": "ERROR",
                },
            )

        if self.call_count == 3:
            return InvestigationDecision(
                action=InvestigationAction.QUERY_METRICS,
                reason="Inspect payment-service error rate",
                parameters={
                    "service": "payment-service",
                    "metric": "error_rate",
                },
            )

        return InvestigationDecision(
            action=InvestigationAction.STOP,
            reason="Sufficient evidence has been collected",
        )


class FakeHypothesisLLM:
    def invoke(self, prompt):
        return HypothesisProposal(
            description=(
                "Database connection exhaustion may be "
                "contributing to payment failures."
            ),
            supporting_evidence=[
                "Payment-service investigation evidence",
            ],
            contradicting_evidence=[],
            confidence=0.75,
        )


class FakeReportResponse:
    content = """
# Incident Summary

Checkout payment failures increased.

# Investigation Findings

The investigation identified deployment, log,
and metric evidence related to payment-service.

# Root Cause Hypothesis

Database connection exhaustion may be contributing
to payment failures.

# Supporting Evidence

Database connection failures and elevated error
rates were observed.

# Contradicting Evidence

The deployment completed successfully.

# Confidence

0.75

# Recommended Next Steps

Inspect database connection pool configuration
and database resource utilization.
"""


class FakeLLM:
    def __init__(self):
        self.decision_llm = SequentialDecisionLLM()
        self.hypothesis_llm = FakeHypothesisLLM()

    def with_structured_output(self, schema, **kwargs):
        if schema is InvestigationDecision:
            return self.decision_llm

        if schema is HypothesisProposal:
            return self.hypothesis_llm

        raise AssertionError(
            f"Unexpected structured schema: {schema}"
        )

    def invoke(self, prompt):
        return FakeReportResponse()

