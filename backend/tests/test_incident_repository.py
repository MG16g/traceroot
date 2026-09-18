from app.core.database import SessionLocal
from app.models.incident import IncidentModel
from app.repositories.incident_repository import IncidentRepository


def test_create_and_retrieve_incident():
    db = SessionLocal()

    try:
        repository = IncidentRepository(db)

        # Clean up if the test was previously executed
        existing = repository.get_by_id("INC-TEST-001")

        if existing:
            db.delete(existing)
            db.commit()

        incident = IncidentModel(
            id="INC-TEST-001",
            title="Checkout payment failures",
            description="Payment failures increased after deployment",
            service="payment-service",
            severity="critical",
            status="open",
        )

        created = repository.create(incident)

        assert created.id == "INC-TEST-001"

        retrieved = repository.get_by_id("INC-TEST-001")

        assert retrieved is not None
        assert retrieved.title == "Checkout payment failures"
        assert retrieved.service == "payment-service"
        assert retrieved.severity == "critical"

    finally:
        # Keep the development database clean after the test
        incident = db.get(IncidentModel, "INC-TEST-001")

        if incident:
            db.delete(incident)
            db.commit()

        db.close()