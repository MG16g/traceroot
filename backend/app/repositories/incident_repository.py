from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.incident import IncidentModel


class IncidentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, incident: IncidentModel) -> IncidentModel:
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        return incident

    def get_by_id(self, incident_id: str) -> IncidentModel | None:
        statement = select(IncidentModel).where(
            IncidentModel.id == incident_id
        )

        return self.db.scalar(statement)