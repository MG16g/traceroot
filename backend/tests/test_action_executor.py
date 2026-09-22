from unittest.mock import patch

from app.orchestration.investigation_graph import execute_action

from app.schemas.evidence import EvidenceSourceType

from app.schemas.incident import (
    Incident,
    IncidentSeverity,
)

from app.schemas.investigation import (
    InvestigationAction,
    InvestigationDecision,
    InvestigationState,
)


def test_execute_get_deployments_action():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    decision = InvestigationDecision(
        action=InvestigationAction.GET_DEPLOYMENTS,
        reason="Check recent payment-service deployments",
        parameters={
            "service": "payment-service",
        },
    )

    state = InvestigationState(
        incident=incident,
        current_decision=decision,
    )

    fake_results = [
        {
            "service": "payment-service",
            "version": "2.4.0",
            "status": "success",
        }
    ]

    with patch(
        "app.orchestration.investigation_graph.get_deployments",
        return_value=fake_results,
    ) as mock_get_deployments:

        result = execute_action(state)

    mock_get_deployments.assert_called_once_with(
        incident_id="INC-001",
        service="payment-service",
    )

    assert result["current_step"] == "evidence_collected"

    assert len(result["evidence"]) == 1

    evidence = result["evidence"][0]

    assert evidence.incident_id == "INC-001"
    assert evidence.source_type == EvidenceSourceType.DEPLOYMENT
    assert evidence.service == "payment-service"

    assert "2.4.0" in evidence.content


def test_execute_action_records_tool_error():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    decision = InvestigationDecision(
        action=InvestigationAction.GET_DEPLOYMENTS,
        reason="Check recent deployments",
        parameters={
            "service": "payment-service",
        },
    )

    state = InvestigationState(
        incident=incident,
        current_decision=decision,
    )

    with patch(
        "app.orchestration.investigation_graph.get_deployments",
        side_effect=RuntimeError("Deployment telemetry unavailable"),
    ):
        result = execute_action(state)

    assert result["current_step"] == "tool_error"
    assert result["error"] == "Deployment telemetry unavailable"