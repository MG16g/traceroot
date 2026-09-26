from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InvestigationModel(Base):
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
    )

    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    iteration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    current_step: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    executed_actions: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )

    evidence: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )

    hypotheses: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )

    root_cause: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    final_report: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )