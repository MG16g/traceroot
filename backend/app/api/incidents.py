from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import get_db
from app.repositories.incident_repository import IncidentRepository
from app.schemas.incident import Incident, IncidentCreate,IncidentStatus, IncidentStatusUpdate
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
        status=IncidentStatus.OPEN.value,
    )

    try:
        created = repository.create(incident)

    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Incident {payload.id} already exists.",
        ) from exc

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
            detail=f"Incident {incident_id} was not found.",
        )

    current_status = IncidentStatus(incident.status)
    requested_status = payload.status

    allowed_transitions = {
        IncidentStatus.OPEN: {
            IncidentStatus.INVESTIGATING,
        },
        IncidentStatus.INVESTIGATING: {
            IncidentStatus.RESOLVED,
        },
        IncidentStatus.RESOLVED: set(),
    }

    # Repeated requests are safe.
    if current_status == requested_status:
        return Incident.model_validate(
            incident,
            from_attributes=True,
        )

    if requested_status not in allowed_transitions[current_status]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid incident status transition: "
                f"{current_status.value} -> "
                f"{requested_status.value}."
            ),
        )

    updated = repository.update_status(
        incident,
        requested_status.value,
    )

    return Incident.model_validate(
        updated,
        from_attributes=True,
    )