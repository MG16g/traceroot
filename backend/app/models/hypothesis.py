from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HypothesisModel(Base):
    __tablename__ = "hypotheses"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )

    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    incident: Mapped["IncidentModel"] = relationship(
        back_populates="hypotheses"
    )

    evidence_links: Mapped[list["HypothesisEvidenceModel"]] = relationship(
        back_populates="hypothesis",
        cascade="all, delete-orphan",
    )