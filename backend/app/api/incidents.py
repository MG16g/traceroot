from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import Incident


router = APIRouter(
    prefix="/api/incidents",
    tags=["incidents"],
)


@router.get("", response_model=list[Incident])
def get_incidents(
    db: Session = Depends(get_db),
) -> list[Incident]:
    repository = IncidentRepository(db)

    incidents = repository.get_all()

    return [
        Incident.model_validate(
            incident,
            from_attributes=True,
        )
        for incident in incidents
    ]