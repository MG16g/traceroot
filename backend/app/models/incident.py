from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IncidentModel(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    service: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    evidence: Mapped[list["EvidenceModel"]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )

    hypotheses: Mapped[list["HypothesisModel"]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
    )