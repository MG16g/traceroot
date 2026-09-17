from app.schemas.incident import (
    Incident,
    IncidentSeverity,
)


def test_create_incident():
    incident = Incident(
        id="INC-001",
        title="Checkout payment failures",
        description="Payment failures increased after deployment",
        service="payment-service",
        severity=IncidentSeverity.CRITICAL,
    )

    assert incident.id == "INC-001"
    assert incident.service == "payment-service"
    assert incident.severity == IncidentSeverity.CRITICAL