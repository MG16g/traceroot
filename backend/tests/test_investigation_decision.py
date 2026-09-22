import pytest
from pydantic import ValidationError

from app.schemas.investigation import (
    InvestigationAction,
    InvestigationDecision,
    InvestigationState
)
from app.schemas.incident import Incident, IncidentSeverity


def test_valid_investigation_decision():
    decision = InvestigationDecision(
        action=InvestigationAction.SEARCH_LOGS,
        reason="Check payment-service error logs",
        parameters={
            "service": "payment-service",
            "level": "ERROR",
        },
    )

    assert decision.action == InvestigationAction.SEARCH_LOGS
    assert decision.reason == "Check payment-service error logs"
    assert decision.parameters["service"] == "payment-service"
    assert decision.parameters["level"] == "ERROR"


def test_invalid_investigation_action_is_rejected():
    with pytest.raises(ValidationError):
        InvestigationDecision(
            action="restart_server",
            reason="Restart the service",
            parameters={},
        )


def test_stop_decision_defaults_to_empty_parameters():
    decision = InvestigationDecision(
        action=InvestigationAction.STOP,
        reason="No further investigation is required",
    )

    assert decision.action == InvestigationAction.STOP
    assert decision.parameters == {}


def test_investigation_state_can_hold_decision():
    # Replace this Incident construction with the SAME valid Incident
    # construction/fixture already used in your Day 1 tests.
    incident = Incident(
        
        id="INC-001",
                title="Checkout payment failures",
                description="Payment failures increased after deployment",
                service="payment-service",
                severity=IncidentSeverity.CRITICAL,
    )

    decision = InvestigationDecision(
        action=InvestigationAction.SEARCH_LOGS,
        reason="Check payment-service error logs",
        parameters={
            "service": "payment-service",
        },
    )

    state = InvestigationState(
        incident=incident,
        current_decision=decision,
    )

    assert state.current_decision == decision
    assert state.current_decision.action == InvestigationAction.SEARCH_LOGS
    assert state.current_decision.parameters["service"] == "payment-service"