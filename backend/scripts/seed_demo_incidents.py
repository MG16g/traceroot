from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.incident import IncidentModel
from app.repositories.incident_repository import IncidentRepository


DEMO_INCIDENTS = [
    {
        "id": "INC-001",
        "title": "Checkout payment failures",
        "description": (
            "Customers are experiencing payment failures "
            "during checkout."
        ),
        "service": "payment-service",
        "severity": "critical",
        "status": "open",
        "created_at": datetime(
            2026,
            9,
            18,
            14,
            5,
            tzinfo=timezone.utc,
        ),
    },
    {
        "id": "INC-002",
        "title": "Inventory reservation failures",
        "description": (
            "Inventory reservations are failing for a "
            "subset of checkout requests."
        ),
        "service": "inventory-service",
        "severity": "high",
        "status": "investigating",
        "created_at": datetime(
            2026,
            9,
            19,
            10,
            20,
            tzinfo=timezone.utc,
        ),
    },
    {
        "id": "INC-003",
        "title": "Checkout API latency spike",
        "description": (
            "Checkout API latency increased significantly, "
            "causing slow customer requests."
        ),
        "service": "checkout-service",
        "severity": "medium",
        "status": "open",
        "created_at": datetime(
            2026,
            9,
            20,
            16,
            40,
            tzinfo=timezone.utc,
        ),
    },
]


def seed_demo_incidents() -> None:
    db = SessionLocal()

    try:
        repository = IncidentRepository(db)

        for incident_data in DEMO_INCIDENTS:
            incident_id = incident_data["id"]

            existing = repository.get_by_id(incident_id)

            if existing is not None:
                print(
                    f"Skipping {incident_id}: "
                    "incident already exists."
                )
                continue

            incident = IncidentModel(**incident_data)

            repository.create(incident)

            print(
                f"Created {incident.id}: "
                f"{incident.title}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_incidents()