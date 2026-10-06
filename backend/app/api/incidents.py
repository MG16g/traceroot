from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import Incident, IncidentCreate, IncidentStatusUpdate
from app.models.incident import IncidentModel


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


@router.get(
    "/{incident_id}",
    response_model=Incident,
)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
) -> Incident:
    repository = IncidentRepository(db)

    incident = repository.get_by_id(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Incident {incident_id} was not found."
            ),
        )

    return Incident.model_validate(
        incident,
        from_attributes=True,
    )


@router.post(
    "",
    response_model=Incident,
    status_code=status.HTTP_201_CREATED,
)
def create_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
) -> Incident:
    repository = IncidentRepository(db)

    existing = repository.get_by_id(payload.id)

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Incident {payload.id} already exists."
            ),
        )

    incident = IncidentModel(
        id=payload.id,
        title=payload.title,
        description=payload.description,
        service=payload.service,
        severity=payload.severity.value,
        status=payload.status.value,
    )

    created = repository.create(incident)

    return Incident.model_validate(
        created,
        from_attributes=True,
    )


@router.patch(
    "/{incident_id}/status",
    response_model=Incident,
)
def update_incident_status(
    incident_id: str,
    payload: IncidentStatusUpdate,
    db: Session = Depends(get_db),
) -> Incident:
    repository = IncidentRepository(db)

    incident = repository.get_by_id(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Incident {incident_id} was not found."
            ),
        )

    updated = repository.update_status(
        incident,
        payload.status.value,
    )

    return Incident.model_validate(
        updated,
        from_attributes=True,
    )