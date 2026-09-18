from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class HypothesisEvidenceModel(Base):
    __tablename__ = "hypothesis_evidence"

    hypothesis_id: Mapped[str] = mapped_column(
        ForeignKey("hypotheses.id", ondelete="CASCADE"),
        primary_key=True,
    )

    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("evidence.id", ondelete="CASCADE"),
        primary_key=True,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    hypothesis: Mapped["HypothesisModel"] = relationship(
        back_populates="evidence_links"
    )

    evidence: Mapped["EvidenceModel"] = relationship()