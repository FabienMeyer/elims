"""Create items table."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the initial schema."""
    op.create_table(
        "item",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
    )
    op.create_index("ix_item_name", "item", ["name"])


def downgrade() -> None:
    """Remove the initial schema."""
    op.drop_index("ix_item_name", table_name="item")
    op.drop_table("item")
