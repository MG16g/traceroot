"""Add incident fingerprint for active-incident deduplication.

Revision ID: b7c4d9e2a103
Revises: fac5205096e4
"""

from alembic import op
import sqlalchemy as sa


revision = "b7c4d9e2a103"
down_revision = "fac5205096e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "incidents",
        sa.Column(
            "fingerprint",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.create_index(
        "uq_incidents_active_fingerprint",
        "incidents",
        ["fingerprint"],
        unique=True,
        postgresql_where=sa.text(
            "fingerprint IS NOT NULL "
            "AND status IN ('open', 'investigating')"
        ),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_incidents_active_fingerprint",
        table_name="incidents",
    )

    op.drop_column(
        "incidents",
        "fingerprint",
    )