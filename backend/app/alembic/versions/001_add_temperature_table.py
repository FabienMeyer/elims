"""Add temperature table.

Revision ID: 001
Revises:
Create Date: 2026-02-09

"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create temperature table."""
    op.create_table(
        "temperature",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("device_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_temperature_device_id"), "temperature", ["device_id"], unique=False)
    op.create_index(op.f("ix_temperature_timestamp"), "temperature", ["timestamp"], unique=False)


def downgrade() -> None:
    """Drop temperature table."""
    op.drop_index(op.f("ix_temperature_timestamp"), table_name="temperature")
    op.drop_index(op.f("ix_temperature_device_id"), table_name="temperature")
    op.drop_table("temperature")
