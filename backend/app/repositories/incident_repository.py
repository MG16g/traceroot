from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.incident import IncidentModel


class IncidentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, incident: IncidentModel) -> IncidentModel:
        try:
            self.db.add(incident)
            self.db.commit()
            self.db.refresh(incident)

            return incident

        except SQLAlchemyError:
            self.db.rollback()
            raise

    def get_by_id(self, incident_id: str) -> IncidentModel | None:
        statement = select(IncidentModel).where(
            IncidentModel.id == incident_id
        )

        return self.db.scalar(statement)

    def get_all(self) -> list[IncidentModel]:
        statement = select(IncidentModel).order_by(
            IncidentModel.created_at.desc()
        )

        return list(self.db.scalars(statement).all())

    def update_status(
        self,
        incident: IncidentModel,
        status: str,
    ) -> IncidentModel:
        try:
            incident.status = status

            self.db.commit()
            self.db.refresh(incident)

            return incident

        except SQLAlchemyError:
            self.db.rollback()
            raise