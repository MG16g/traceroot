from app.schemas.incident import Incident, IncidentSeverity
from app.schemas.investigation import (
    InvestigationState,
    InvestigationStatus,
)


def test_create_investigation_state():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    state = InvestigationState(
        incident=incident
    )

    assert state.incident.id == "INC-001"
    assert state.evidence == []
    assert state.hypotheses == []
    assert state.current_step == "triage"
    assert state.iteration == 0
    assert state.status == InvestigationStatus.PENDING
    assert state.final_report is None